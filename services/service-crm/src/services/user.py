from typing import Dict, List, Optional
import logging

from fastapi import HTTPException, status
from itsdangerous import BadSignature, URLSafeTimedSerializer

from src.schemas.user import LoginResponse
from src.dependencies.redis_dependency import RedisDependency
from src.handlers.auth import AuthHandler
from src.schemas.user import (
    AuthUser,
    UserCreateRequest,
    UserResponse,
    UserUpdateRequest,
)
from src.dao.user import UserDAO
from src.settings import settings

logger = logging.getLogger(__name__)


class UserAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class UserService:
    """Сервис бизнес-логики для пользователей"""

    def __init__(
        self,
        user_dao: UserDAO,
        auth_handler: AuthHandler,
        redis: RedisDependency,
    ):
        self.user_dao = user_dao
        self.auth_handler = auth_handler
        self.redis = redis
        self.serializer = URLSafeTimedSerializer(
            secret_key=settings.secret_key.get_secret_value()
        )

    async def _store_access_token(
        self, token: str, user_id: int, session_id: str
    ) -> None:
        async with self.redis.get_client() as client:
            await client.set(f"{user_id}:{session_id}", token)

    async def register_user(self, dto: UserCreateRequest) -> UserResponse:
        """Регистрация нового пользователя"""
        if await self.user_dao.email_exists(dto.email):
            raise UserAlreadyExistsError(
                f"User with email '{dto.email}' already exists"
            )

        hashed_password = await self.auth_handler.get_password_hash(dto.password)
        new_user = UserCreateRequest(
            email=dto.email,
            password=hashed_password,
            first_name=dto.first_name,
            last_name=dto.last_name,
        )
        new_user_dict = new_user.__dict__
        new_user_dict["password_hash"] = new_user_dict.pop("password")
        user_dict = await self.user_dao.create(**new_user_dict)
        confirmation_token = self.serializer.dumps(dto.email)
        confirmation_url = f":url/auth/register_confirm?token={confirmation_token}"
        print(f"SEND Message to {dto.email}: {confirmation_url}")
        print(f"User registered: {user_dict['id']} ({user_dict['email']})")
        return UserResponse(**user_dict)

    async def confirm_user(self, token: str) -> None:
        try:
            email = self.serializer.loads(token, max_age=3600)
        except BadSignature:
            raise HTTPException(status_code=400, detail="Bad token")
        await self.user_dao.confirm(email=email)

    async def login(self, user: AuthUser) -> LoginResponse:
        exist_user = await self.user_dao.get_by_email(email=user.email)
        if exist_user is None or not await self.auth_handler.verify_password(
            hashed_password=exist_user["password_hash"], raw_password=user.password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Wrong email or password",
            )
        token, session_id = await self.auth_handler.create_access_token(
            user_id=exist_user["id"]
        )
        await self._store_access_token(
            token=token, user_id=exist_user["id"], session_id=session_id
        )
        return LoginResponse(access_token=token)

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

    async def list_users(
        self,
        page: int = 1,
        per_page: int = 20,
        is_active: Optional[bool] = None,
    ) -> tuple[List[UserResponse], int]:
        """Получение списка пользователей с пагинацией"""
        if is_active is not None and is_active:
            users_dict = await self.user_dao.get_active_users()
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

    async def deactivate_user(self, user_id: int) -> UserResponse:
        """Деактивация пользователя"""
        user_dict = await self.user_dao.get_by_id(user_id)
        if not user_dict:
            raise UserNotFoundError(f"User with id {user_id} not found")

        await self.user_dao.deactivate_user(user_id)
        await self._revoke_user_sessions(user_id)

        updated_dict = await self.user_dao.get_by_id(user_id)
        return UserResponse(**updated_dict)

    async def activate_user(self, user_id: int) -> UserResponse:
        """Активация пользователя"""
        user_dict = await self.user_dao.get_by_id(user_id)
        if not user_dict:
            raise UserNotFoundError(f"User with id {user_id} not found")
        await self.user_dao.activate_user(user_id)
        updated_dict = await self.user_dao.get_by_id(user_id)
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

    async def check_emails_availability(self, emails: List[str]) -> Dict[str, bool]:
        """Проверка доступности email"""
        existing = await self.user_dao.check_multiple_emails_exist(emails)
        return {email: not exists for email, exists in existing.items()}

    async def _send_welcome_email(self, user_dict: dict) -> None:
        logger.info(f"Sending welcome email to {user_dict['email']}")

    async def _revoke_user_sessions(self, user_id: int) -> None:
        logger.info(f"Revoking sessions for user {user_id}")

    async def get_access_token(self, user_id: int, session_id: str) -> str | None:
        async with self.redis.get_client() as client:
            return await client.get(f"{user_id}:{session_id}")

    async def revoke_access_token(self, user_id: int, session_id: str) -> None:
        async with self.redis.get_client() as client:
            await client.delete(f"{user_id}:{session_id}")
