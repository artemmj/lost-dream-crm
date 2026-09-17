from fastapi import Depends, HTTPException

from src.dao.user import UserDAO
from src.dependencies.redis import redis_dependency
from src.dependencies.db import db_dependency
from src.handlers.auth import AuthHandler
from src.schemas.auth import AuthUser, LoginResponse, UserCreateRequest


class AuthService:
    def __init__(self, user_dao: UserDAO, auth_handler: AuthHandler, redis_client):
        self.user_dao = user_dao
        self.auth_handler = auth_handler
        self.redis = redis_client

    async def register(self, dto: UserCreateRequest):
        if await self.user_dao.email_exists(dto.email):
            raise HTTPException(status_code=409, detail="Email already registered")

        hashed_pw = await self.auth_handler.get_password_hash(dto.password)
        user_data = {
            "email": dto.email,
            "password_hash": hashed_pw,
            "first_name": dto.first_name,
            "last_name": dto.last_name,
        }
        user = await self.user_dao.create(user_data)
        return user

    async def login(self, credentials: AuthUser) -> LoginResponse:
        user = await self.user_dao.get_by_email(credentials.email)
        if not user or not await self.auth_handler.verify_password(
            credentials.password, user.password_hash
        ):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not user.is_active or user.is_banned:
            raise HTTPException(status_code=403, detail="Account disabled")

        token, session_id = await self.auth_handler.create_access_token(user_id=user.id)
        async with self.redis.get_client() as client:
            await client.set(f"{user.id}:{session_id}", token, ex=3600)

        return LoginResponse(access_token=token)

    async def logout(self, user_id: int, session_id: str):
        async with self.redis.get_client() as client:
            await client.delete(f"{user_id}:{session_id}")
        return {"message": "Logged out"}


def get_auth_service(
    auth_handler: AuthHandler = Depends(AuthHandler),
) -> AuthService:
    """Создаёт AuthService с DAO нового стиля.

    db и redis берутся из модульных синглтонов: движок SQLAlchemy
    и пулы Redis создаются один раз на процесс, а не на каждый запрос.
    """
    user_dao = UserDAO(db=db_dependency)
    return AuthService(
        user_dao=user_dao,
        auth_handler=auth_handler,
        redis_client=redis_dependency,
    )
