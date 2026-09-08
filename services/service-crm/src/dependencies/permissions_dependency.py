from fastapi import Depends

from src.dependencies.db_dependency import DBDependency
from src.dao.permissions import PermissionDAO
from src.dao.roles import RoleDAO
from src.dao.user_roles import UserRoleDAO
from src.services.permissions import PermissionService
from src.services.roles import RoleService
from src.services.user_role import UserRoleService


def get_permission_service(
    db: DBDependency = Depends(DBDependency),
) -> PermissionService:
    """Фабрика сервиса пермишенов"""
    return PermissionService(permission_dao=PermissionDAO(db))


def get_role_service(
    db: DBDependency = Depends(DBDependency),
) -> RoleService:
    """Фабрика сервиса ролей"""
    return RoleService(role_dao=RoleDAO(db))


def get_user_role_service(
    db: DBDependency = Depends(DBDependency),
) -> UserRoleService:
    """Фабрика сервиса назначения ролей пользователям"""
    return UserRoleService(user_role_dao=UserRoleDAO(db))
