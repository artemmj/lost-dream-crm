from fastapi import Depends

from src.dao.user import UserDAO
from src.services.user import UserService
from src.handlers.auth import AuthHandler
from src.dependencies.redis_dependency import RedisDependency
from src.dependencies.db_dependency import DBDependency


def get_user_service(
    db: DBDependency = Depends(DBDependency),
    auth_handler: AuthHandler = Depends(AuthHandler),
    redis: RedisDependency = Depends(RedisDependency),
) -> UserService:
    """Фабрика сервиса с правильным графом зависимостей"""
    user_dao = UserDAO(db)
    return UserService(user_dao=user_dao, auth_handler=auth_handler, redis=redis)
