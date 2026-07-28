import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

from src.dao.user import UserDAO

logger = logging.getLogger(__name__)


class UserAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
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
    created_at: datetime.datetime
    updated_at: datetime.datetime
    email: str
    password_hash: str
    first_name: str
    last_name: str
    is_active: bool
    is_banned: bool
    is_superuser: bool
    is_verified: bool


class UserService:
    """Сервис бизнес-логики для пользователей"""

    def __init__(self, user_dao: UserDAO):
        self.user_dao = user_dao

    async def register_user(self, dto: UserCreateDTO) -> UserResponseDTO:
        """Регистрация нового пользователя"""
        if await self.user_dao.email_exists(dto.email):
            raise UserAlreadyExistsError(
                f"User with email '{dto.email}' already exists"
            )

        user_dict = await self.user_dao.create(
            email=dto.email,
            password_hash=dto.password_hash,
            first_name=dto.first_name,
            last_name=dto.last_name,
            is_active=dto.is_active,
            is_banned=dto.is_banned,
            is_superuser=dto.is_superuser,
            is_verified=dto.is_verified,
        )

        await self._send_welcome_email(user_dict)
        logger.info(f"User registered: {user_dict['id']} ({user_dict['email']})")

        return UserResponseDTO(**user_dict)

    async def get_user(self, user_id: int) -> UserResponseDTO:
        """Получение пользователя по ID"""
        user_dict = await self.user_dao.get_by_id(user_id)
        if not user_dict:
            raise UserNotFoundError(f"User with id {user_id} not found")
        return UserResponseDTO(**user_dict)

    async def get_user_by_email(self, email: str) -> UserResponseDTO:
        """Поиск пользователя по email"""
        user_dict = await self.user_dao.get_by_email(email)
        if not user_dict:
            raise UserNotFoundError(f"User with email '{email}' not found")
        return UserResponseDTO(**user_dict)

    async def list_users(
        self,
        page: int = 1,
        per_page: int = 20,
        is_active: Optional[bool] = None,
    ) -> tuple[List[UserResponseDTO], int]:
        """Получение списка пользователей с пагинацией"""
        if is_active is not None and is_active:
            users_dict = await self.user_dao.get_active_users()
            total = len(users_dict)
            start = (page - 1) * per_page
            users_dict = users_dict[start : start + per_page]
        else:
            users_dict = await self.user_dao.get_all(
                limit=per_page, offset=(page - 1) * per_page
            )
            total = await self.user_dao.count()

        return [UserResponseDTO(**u) for u in users_dict], total

    async def update_user(self, user_id: int, dto: UserUpdateDTO) -> UserResponseDTO:
        """Обновление пользователя"""
        # Получаем ORM объект для обновления
        user = await self.user_dao.get_obj_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")

        if dto.email and dto.email != user.email:
            if await self.user_dao.email_exists_excluding_user(dto.email, user_id):
                raise UserAlreadyExistsError(f"Email '{dto.email}' already taken")

        update_data = {k: v for k, v in dto.__dict__.items() if v is not None}
        for field, value in update_data.items():
            setattr(user, field, value)

        updated_dict = await self.user_dao.update(user)
        return UserResponseDTO(**updated_dict)

    async def deactivate_user(self, user_id: int) -> UserResponseDTO:
        """Деактивация пользователя"""
        user_dict = await self.user_dao.get_by_id(user_id)
        if not user_dict:
            raise UserNotFoundError(f"User with id {user_id} not found")

        await self.user_dao.deactivate_user(user_id)
        await self._revoke_user_sessions(user_id)

        updated_dict = await self.user_dao.get_by_id(user_id)
        return UserResponseDTO(**updated_dict)

    async def activate_user(self, user_id: int) -> UserResponseDTO:
        """Активация пользователя"""
        user_dict = await self.user_dao.get_by_id(user_id)
        if not user_dict:
            raise UserNotFoundError(f"User with id {user_id} not found")
        await self.user_dao.activate_user(user_id)
        updated_dict = await self.user_dao.get_by_id(user_id)
        return UserResponseDTO(**updated_dict)

    async def delete_user(self, user_id: int) -> None:
        """Удаление пользователя"""
        user = await self.user_dao.get_obj_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")

        await self.user_dao.delete(user)
        logger.info(f"User {user_id} deleted")

    async def ban_user(self, user_id: int) -> UserResponseDTO:
        """Бан пользователя"""
        user = await self.user_dao.get_obj_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")

        user.is_banned = True
        user.is_active = False
        updated_dict = await self.user_dao.update(user)

        logger.info(f"User {user_id} banned")
        return UserResponseDTO(**updated_dict)

    async def unban_user(self, user_id: int) -> UserResponseDTO:
        """Разбан пользователя"""
        user = await self.user_dao.get_obj_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")

        user.is_banned = False
        user.is_active = True
        updated_dict = await self.user_dao.update(user)

        logger.info(f"User {user_id} unbanned")
        return UserResponseDTO(**updated_dict)

    async def check_emails_availability(self, emails: List[str]) -> Dict[str, bool]:
        """Проверка доступности email"""
        existing = await self.user_dao.check_multiple_emails_exist(emails)
        return {email: not exists for email, exists in existing.items()}

    async def _send_welcome_email(self, user_dict: dict) -> None:
        logger.info(f"Sending welcome email to {user_dict['email']}")

    async def _revoke_user_sessions(self, user_id: int) -> None:
        logger.info(f"Revoking sessions for user {user_id}")
