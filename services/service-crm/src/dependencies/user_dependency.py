from fastapi import Depends

from src.dao.user import UserDAO
from src.services.user import UserService
from src.handlers.auth import AuthHandler
from src.dependencies.redis_dependency import redis_dependency
from src.dependencies.db_dependency import db_dependency


def get_user_service(
    auth_handler: AuthHandler = Depends(AuthHandler),
) -> UserService:
    """Фабрика сервиса с правильным графом зависимостей.

    db и redis берутся из модульных синглтонов: движок SQLAlchemy
    и пулы Redis создаются один раз на процесс, а не на каждый запрос.
    """
    user_dao = UserDAO(db_dependency)
    return UserService(
        user_dao=user_dao,
        auth_handler=auth_handler,
        redis=redis_dependency,
    )
