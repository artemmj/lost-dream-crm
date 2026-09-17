import datetime
import uuid
from typing import NamedTuple

import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

from src.settings import settings


class TokenData(NamedTuple):
    """Структура данных для возвращаемого токена и сессии."""

    access_token: str
    session_id: str


class AuthHandler:
    """Утилитарный класс для работы с безопасностью: хеширование паролей и JWT."""

    def __init__(self):
        # bcrypt автоматически управляет солью
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = settings.secret_key
        self.algorithm = "HS256"

    async def get_password_hash(self, password: str) -> str:
        """Хеширует пароль с использованием bcrypt."""
        return self.pwd_context.hash(password)

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверяет соответствие пароля его хешу."""
        return self.pwd_context.verify(plain_password, hashed_password)

    async def create_access_token(self, user_id: int) -> TokenData:
        """
        Создает JWT токен и уникальный ID сессии.
        """
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            seconds=settings.access_token_expire
        )

        session_id = str(uuid.uuid4())

        to_encode = {
            "sub": str(user_id),  # Standard claim for subject (user ID)
            # get_current_user читает user_id из токена — дублируем явным claim'ом
            "user_id": user_id,
            "session_id": session_id,
            "exp": expire,
            "iat": datetime.datetime.now(datetime.timezone.utc),
            "type": "access",
        }

        encoded_jwt = jwt.encode(
            to_encode, self.secret_key.get_secret_value(), algorithm=self.algorithm
        )
        return TokenData(access_token=encoded_jwt, session_id=session_id)

    async def decode_access_token(self, token: str) -> dict:
        """
        Декодирует и валидирует JWT токен.
        """
        try:
            payload = jwt.decode(
                token, self.secret_key.get_secret_value(), algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
