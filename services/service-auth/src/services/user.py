from typing import Optional
import logging

from fastapi import HTTPException, status
from itsdangerous import BadSignature, URLSafeTimedSerializer

from src.models.user import User
from src.schemas.user import (
    LoginResponse,
    UserMeResponse,
    AuthUser,
    UserCreateRequest,
    UserResponse,
)
from src.dependencies.redis import RedisDependency
from src.handlers.auth import AuthHandler
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
        logger.info(f"SEND Message to {dto.email}: {confirmation_url}")
        logger.info(f"User registered: {user_dict['id']} ({user_dict['email']})")
        return UserResponse(**user_dict)

    async def confirm_user(self, token: str) -> None:
        try:
            email = self.serializer.loads(token, max_age=3600)
        except BadSignature:
            raise HTTPException(status_code=400, detail="Bad token")
        await self.user_dao.confirm_email(email=email)

    async def login(self, user: AuthUser) -> LoginResponse:
        exist_user = await self.user_dao.get_by_email(email=user.email)
        if exist_user is None or not await self.auth_handler.verify_password(
            user.password, exist_user["password_hash"]
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Wrong email or password",
            )
        if not exist_user["is_active"] or exist_user["is_banned"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled or banned",
            )
        token, session_id = await self.auth_handler.create_access_token(
            user_id=exist_user["id"]
        )
        await self._store_access_token(
            token=token, user_id=exist_user["id"], session_id=session_id
        )
        return LoginResponse(access_token=token)

    async def logout_user(self, user: UserMeResponse) -> dict:
        await self.revoke_access_token(user_id=user.id, session_id=user.session_id)
        return {"message": "Logged out"}

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

    async def _revoke_user_sessions(self, user_id: int) -> None:
        logger.info(f"Revoking sessions for user {user_id}")

    async def get_access_token(self, user_id: int, session_id: str) -> str | None:
        async with self.redis.get_client() as client:
            return await client.get(f"{user_id}:{session_id}")

    async def revoke_access_token(self, user_id: int, session_id: str) -> None:
        async with self.redis.get_client() as client:
            await client.delete(f"{user_id}:{session_id}")
