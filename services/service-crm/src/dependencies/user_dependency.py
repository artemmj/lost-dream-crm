from src.dao.user import UserDAO
from src.services.user import UserService
from src.dependencies.db_dependency import db_dependency


def get_user_service() -> UserService:
    """Фабрика сервиса (db — модульный синглтон)."""
    return UserService(user_dao=UserDAO(db_dependency))
