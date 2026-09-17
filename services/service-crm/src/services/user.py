from typing import Dict, List, Optional, Tuple
import logging

from src.models.user import User
from src.schemas.user import UserResponse, UserUpdateRequest
from src.dao.user import UserDAO

logger = logging.getLogger(__name__)


class UserAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class UserService:
    """Сервис бизнес-логики для пользователей.

    Аутентификация и проверка пермишенов вынесены в service-auth
    (см. handlers/auth_proxy.py) — здесь только управление пользователями.
    """

    def __init__(self, user_dao: UserDAO):
        self.user_dao = user_dao

    async def get_user(self, user_id: int) -> UserResponse:
        """Получение пользователя по ID"""
        user_dict = await self.user_dao.get_by_id(user_id)
        if not user_dict:
            raise UserNotFoundError(f"User with id {user_id} not found")
        return UserResponse(**user_dict)

    async def get_user_by_email(self, email: str) -> UserResponse:
        """Поиск пользователя по email"""
        user_dict = await self.user_dao.get_by_email(email)
        if not user_dict:
            raise UserNotFoundError(f"User with email '{email}' not found")
        return UserResponse(**user_dict)

    async def get_user_with_roles(self, user_id: int) -> Optional[User]:
        """Получение пользователя с ролями и пермишенами."""
        return await self.user_dao.get_by_id_with_roles(user_id)

    async def get_users_with_roles(
        self, page: int, per_page: int, search: Optional[str] = None
    ) -> Tuple[List[Dict], int]:
        """Список пользователей с ролями."""
        return await self.user_dao.get_list_with_roles(page, per_page, search)

    async def list_users(
        self,
        page: int = 1,
        per_page: int = 20,
        is_active: Optional[bool] = None,
    ) -> tuple[List[UserResponse], int]:
        """Получение списка пользователей с пагинацией"""
        if is_active is not None and is_active:
            users_dict = await self.user_dao.get_all_users()
            total = len(users_dict)
            start = (page - 1) * per_page
            users_dict = users_dict[start : start + per_page]  # noqa: E203
        else:
            users_dict = await self.user_dao.get_all(
                limit=per_page, offset=(page - 1) * per_page
            )
            total = await self.user_dao.count()

        return [UserResponse(**u) for u in users_dict], total

    async def update_user(self, user_id: int, dto: UserUpdateRequest) -> UserResponse:
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
        return UserResponse(**updated_dict)

    async def delete_user(self, user_id: int) -> None:
        """Удаление пользователя"""
        user = await self.user_dao.get_obj_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")

        await self.user_dao.delete(user)
        logger.info(f"User {user_id} deleted")

    async def ban_user(self, user_id: int) -> UserResponse:
        """Бан пользователя"""
        user = await self.user_dao.get_obj_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")

        user.is_banned = True
        user.is_active = False
        updated_dict = await self.user_dao.update(user)

        logger.info(f"User {user_id} banned")
        return UserResponse(**updated_dict)

    async def unban_user(self, user_id: int) -> UserResponse:
        """Разбан пользователя"""
        user = await self.user_dao.get_obj_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")

        user.is_banned = False
        user.is_active = True
        updated_dict = await self.user_dao.update(user)

        logger.info(f"User {user_id} unbanned")
        return UserResponse(**updated_dict)

    async def _send_welcome_email(self, user_dict: dict) -> None:
        logger.info(f"Sending welcome email to {user_dict['email']}")
