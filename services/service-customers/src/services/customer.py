import datetime
import logging
from dataclasses import dataclass
from typing import List, Optional

from src.dao.customer import CustomerDAO
from src.models.customer import Customer
from src.kafka.events import CustomerCreatedEvent
from src.dependencies.db_dependency import db_dependency
from src.dao.outbox_dao import OutboxDAO

logger = logging.getLogger(__name__)


class CustomerAlreadyExistsError(Exception):
    pass


class CustomerNotFoundError(Exception):
    pass


@dataclass
class CustomerCreateDTO:
    email: str
    phone: str
    password_hash: str
    first_name: str
    last_name: str
    middle_name: str


@dataclass
class CustomerUpdateDTO:
    email: Optional[str] = None
    phone: Optional[str] = None
    password_hash: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None


@dataclass
class CustomerResponseDTO:
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    email: str
    phone: str
    password_hash: str
    first_name: str
    last_name: str
    middle_name: str


class CustomerService:
    """Сервис бизнес-логики для пользователей"""

    def __init__(self, customer_dao: CustomerDAO, outbox_dao: OutboxDAO):
        self.customer_dao = customer_dao
        self.outbox_dao = outbox_dao

    async def register_customer(self, dto: CustomerCreateDTO) -> CustomerResponseDTO:
        """Регистрация нового клиента (атомарно с записью в outbox)"""
        if await self.customer_dao.email_exists(dto.email):
            raise CustomerAlreadyExistsError(
                f"Customer with email '{dto.email}' already exists"
            )

        async with self.customer_dao.db.session_scope() as session:
            # 1. Создаём ORM-объект вручную, используя ту же сессию
            customer_obj = Customer(
                email=dto.email,
                phone=dto.phone,
                password_hash=dto.password_hash,
                first_name=dto.first_name,
                last_name=dto.last_name,
                middle_name=dto.middle_name,
            )
            session.add(customer_obj)
            await session.flush()
            await session.refresh(customer_obj)

            # Конвертируем в dict для совместимости с остальным кодом
            customer_dict = self.customer_dao._model_to_dict(customer_obj)

            # 2. Формируем событие (БЕЗ PII!)
            event = CustomerCreatedEvent.from_customer_dict(customer_dict)

            # 3. Атомарная запись в outbox (ТА ЖЕ сессия!)
            await self.outbox_dao.save_in_session(
                session,
                aggregate_type="customer",
                aggregate_id=customer_dict["id"],
                event_type="customer.created.v1",
                payload=event.to_payload(),
            )
            # commit произойдёт автоматически при выходе из session_scope

        # Отправка email — ПОСЛЕ коммита (не блокируем транзакцию)
        await self._send_welcome_email(customer_dict)
        logger.info(f"Customer registered: {customer_dict['id']}")

        return CustomerResponseDTO(**customer_dict)

    async def get_customer(self, customer_id: int) -> CustomerResponseDTO:
        """Получение пользователя по ID"""
        customer_dict = await self.customer_dao.get_by_id(customer_id)
        if not customer_dict:
            raise CustomerNotFoundError(f"Customer with id {customer_id} not found")
        return CustomerResponseDTO(**customer_dict)

    async def get_customer_by_email(self, email: str) -> CustomerResponseDTO:
        """Поиск пользователя по email"""
        customer_dict = await self.customer_dao.get_by_email(email)
        if not customer_dict:
            raise CustomerNotFoundError(f"Customer with email '{email}' not found")
        return CustomerResponseDTO(**customer_dict)

    async def list_customers(
        self,
        page: int = 1,
        per_page: int = 20,
        is_active: Optional[bool] = None,
    ) -> tuple[List[CustomerResponseDTO], int]:
        """Получение списка пользователей с пагинацией"""
        if is_active is not None and is_active:
            customers_dict = await self.customer_dao.get_active_customers()
            total = len(customers_dict)
            start = (page - 1) * per_page
            customers_dict = customers_dict[start : start + per_page]  # noqa: E203
        else:
            customers_dict = await self.customer_dao.get_all(
                limit=per_page, offset=(page - 1) * per_page
            )
            total = await self.customer_dao.count()

        return [CustomerResponseDTO(**u) for u in customers_dict], total

    async def update_customer(
        self, customer_id: int, dto: CustomerUpdateDTO
    ) -> CustomerResponseDTO:
        """Обновление пользователя"""
        # Получаем ORM объект для обновления
        customer = await self.customer_dao.get_obj_by_id(customer_id)
        if not customer:
            raise CustomerNotFoundError(f"Customer with id {customer_id} not found")

        if dto.email and dto.email != customer.email:
            if await self.customer_dao.email_exists_excluding_customer(
                dto.email, customer_id
            ):
                raise CustomerAlreadyExistsError(f"Email '{dto.email}' already taken")

        update_data = {k: v for k, v in dto.__dict__.items() if v is not None}
        for field, value in update_data.items():
            setattr(customer, field, value)

        updated_dict = await self.customer_dao.update(customer)
        return CustomerResponseDTO(**updated_dict)

    async def deactivate_customer(self, customer_id: int) -> CustomerResponseDTO:
        """Деактивация пользователя"""
        customer_dict = await self.customer_dao.get_by_id(customer_id)
        if not customer_dict:
            raise CustomerNotFoundError(f"Customer with id {customer_id} not found")

        await self.customer_dao.deactivate_customer(customer_id)
        await self._revoke_customer_sessions(customer_id)

        updated_dict = await self.customer_dao.get_by_id(customer_id)
        return CustomerResponseDTO(**updated_dict)

    async def delete_customer(self, customer_id: int) -> None:
        """Удаление пользователя"""
        customer = await self.customer_dao.get_obj_by_id(customer_id)
        if not customer:
            raise CustomerNotFoundError(f"Customer with id {customer_id} not found")

        await self.customer_dao.delete(customer)
        logger.info(f"Customer {customer_id} deleted")

    async def ban_customer(self, customer_id: int) -> CustomerResponseDTO:
        """Бан пользователя"""
        customer = await self.customer_dao.get_obj_by_id(customer_id)
        if not customer:
            raise CustomerNotFoundError(f"Customer with id {customer_id} not found")

        customer.is_banned = True
        customer.is_active = False
        updated_dict = await self.customer_dao.update(customer)

        logger.info(f"Customer {customer_id} banned")
        return CustomerResponseDTO(**updated_dict)

    async def unban_customer(self, customer_id: int) -> CustomerResponseDTO:
        """Разбан пользователя"""
        customer = await self.customer_dao.get_obj_by_id(customer_id)
        if not customer:
            raise CustomerNotFoundError(f"Customer with id {customer_id} not found")

        customer.is_banned = False
        customer.is_active = True
        updated_dict = await self.customer_dao.update(customer)

        logger.info(f"Customer {customer_id} unbanned")
        return CustomerResponseDTO(**updated_dict)

    async def _send_welcome_email(self, customer_dict: dict) -> None:
        logger.info(f"Sending welcome email to {customer_dict['email']}")

    async def _revoke_customer_sessions(self, customer_id: int) -> None:
        logger.info(f"Revoking sessions for customer {customer_id}")


def get_customer_service() -> CustomerService:
    """Фабрика сервиса клиентов с поддержкой Outbox"""
    customer_dao = CustomerDAO(db_dependency)
    outbox_dao = OutboxDAO(db_dependency)

    return CustomerService(customer_dao=customer_dao, outbox_dao=outbox_dao)
