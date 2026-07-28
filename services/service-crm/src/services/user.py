import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

from src.dao.user import UserDAO
from src.models import User

logger = logging.getLogger(__name__)


class UserAlreadyExistsError(Exception):
    """Пользователь с таким email уже существует"""

    pass


class UserNotFoundError(Exception):
    """Пользователь не найден"""

    pass


@dataclass
class UserCreateDTO:
    email: str
    password_hash: str
    first_name: str
    last_name: str
    is_active: bool = True
    is_banned: bool = False
    is_superuser: bool = False
    is_verified: bool = False


@dataclass
class UserUpdateDTO:
    email: Optional[str] = None
    password_hash: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_banned: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_verified: Optional[bool] = None


@dataclass
class UserResponseDTO:
    id: int
    email: str
    first_name: str
    last_name: str
    is_active: bool
    is_banned: bool
    is_superuser: bool
    is_verified: bool


class UserService:
    def __init__(self, user_dao: UserDAO):
        self.user_dao = user_dao

    async def register_user(self, dto: UserCreateDTO) -> UserResponseDTO:
        if await self.user_dao.email_exists(dto.email):
            raise UserAlreadyExistsError(
                f"User with email '{dto.email}' already exists"
            )
        user = await self.user_dao.create(
            email=dto.email,
            password_hash=dto.password_hash,
            first_name=dto.first_name,
            last_name=dto.last_name,
            is_active=dto.is_active,
            is_banned=dto.is_banned,
            is_superuser=dto.is_superuser,
            is_verified=dto.is_verified,
        )
        await self._send_welcome_email(user)
        logger.info(f"User registered: {user.id} ({user.email})")
        return self._to_dto(user)

    async def get_user(self, user_id: int) -> UserResponseDTO:
        user = await self.user_dao.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")
        return self._to_dto(user)

    async def get_user_by_email(self, email: str) -> UserResponseDTO:
        user = await self.user_dao.get_by_email(email)
        if not user:
            raise UserNotFoundError(f"User with email '{email}' not found")
        return self._to_dto(user)

    async def list_users(
        self,
        page: int = 1,
        per_page: int = 20,
        is_active: Optional[bool] = None,
    ) -> tuple[List[UserResponseDTO], int]:
        if is_active is not None and is_active:
            # Для активных используем оптимизированный метод
            users = await self.user_dao.get_active_users()
            total = len(users)
            # Применяем пагинацию вручную
            start = (page - 1) * per_page
            users = users[start : start + per_page]
        else:
            users = await self.user_dao.get_all(
                limit=per_page, offset=(page - 1) * per_page
            )
            total = await self.user_dao.count()
        return [self._to_dto(u) for u in users], total

    async def update_user(
        self,
        user_id: int,
        dto: UserUpdateDTO,
    ) -> UserResponseDTO:
        user = await self.user_dao.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")
        if dto.email and dto.email != user.email:
            if await self.user_dao.email_exists_excluding_user(dto.email, user_id):
                raise UserAlreadyExistsError(
                    f"Email '{dto.email}' already taken by another user"
                )
            logger.info(
                f"User {user_id} changing email from {user.email} to {dto.email}"
            )
        update_data = {k: v for k, v in dto.__dict__.items() if v is not None}
        for field, value in update_data.items():
            setattr(user, field, value)
        updated_user = await self.user_dao.update(user)
        return self._to_dto(updated_user)

    async def deactivate_user(self, user_id: int) -> UserResponseDTO:
        user = await self.user_dao.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")
        await self.user_dao.deactivate_user(user_id)
        await self._revoke_user_sessions(user_id)
        logger.info(f"User {user_id} deactivated")
        updated_user = await self.user_dao.get_by_id(user_id)
        return self._to_dto(updated_user)

    async def delete_user(self, user_id: int) -> None:
        user = await self.user_dao.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")
        await self._check_can_delete_user(user)
        await self.user_dao.delete(user)
        logger.info(f"User {user_id} deleted")

    async def bulk_create_users(
        self,
        users_dto: List[UserCreateDTO],
    ) -> Dict[str, any]:
        created = []
        skipped = []
        for dto in users_dto:
            try:
                user = await self.register_user(dto)
                created.append(user)
            except UserAlreadyExistsError:
                skipped.append(dto.email)
        return {
            "created": len(created),
            "skipped": len(skipped),
            "skipped_emails": skipped,
            "users": created,
        }

    async def check_emails_availability(
        self,
        emails: List[str],
    ) -> Dict[str, bool]:
        existing = await self.user_dao.check_multiple_emails_exist(emails)
        return {email: not exists for email, exists in existing.items()}

    # ===== Приватные методы =====

    def _to_dto(self, user: User) -> UserResponseDTO:
        """Конвертация модели в DTO"""
        return UserResponseDTO(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            is_banned=user.is_banned,
            is_superuser=user.is_superuser,
            is_verified=user.is_verified,
        )

    async def _send_welcome_email(self, user: User) -> None:
        """Отправка приветственного письма (заглушка)"""
        logger.info(f"Sending welcome email to {user.email}")
        # В реальном коде здесь интеграция с email-сервисом

    async def _revoke_user_sessions(self, user_id: int) -> None:
        """Отзыв всех сессий пользователя (заглушка)"""
        logger.info(f"Revoking sessions for user {user_id}")

    async def _check_can_delete_user(self, user: User) -> None:
        """Проверка возможности удаления пользователя"""
        # Проверка на наличие активных заказов
        # if await self.order_dao.has_active_orders(user.id):
        #     raise ValueError("Cannot delete user with active orders")
        pass
