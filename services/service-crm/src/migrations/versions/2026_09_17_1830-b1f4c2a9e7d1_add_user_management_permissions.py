"""add user management permissions

Добавляет коды пермишенов для управления пользователями
(get_user, list_users, update_user, delete_user) и выдаёт их роли admin.

Revision ID: b1f4c2a9e7d1
Revises: 6adb23601b73
Create Date: 2026-09-17 18:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b1f4c2a9e7d1"
down_revision: Union[str, Sequence[str], None] = "6adb23601b73"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

permissions_table = sa.table(
    "permissions",
    sa.column("id", sa.Integer),
    sa.column("code", sa.String),
    sa.column("description", sa.String),
)

roles_table = sa.table(
    "roles",
    sa.column("id", sa.Integer),
    sa.column("name", sa.String),
)

role_permissions_table = sa.table(
    "role_permissions",
    sa.column("role_id", sa.Integer),
    sa.column("permission_id", sa.Integer),
)

# Коды пермишенов на управление пользователями
USER_MANAGEMENT_PERMISSIONS = [
    ("get_user", "Просмотр пользователя по ID"),
    ("list_users", "Просмотр списка пользователей"),
    ("update_user", "Редактирование пользователя"),
    ("delete_user", "Удаление пользователя"),
]


def upgrade() -> None:
    """Добавить пермишены управления пользователями и выдать их админу."""
    # Вставляем пермишены (идемпотентно)
    op.execute(
        """
        INSERT INTO permissions (code, description)
        VALUES %s
        ON CONFLICT (code) DO NOTHING
        """
        % ", ".join(
            f"('{code}', '{description}')"
            for code, description in USER_MANAGEMENT_PERMISSIONS
        )
    )

    # Выдаём все пермишены управления пользователями роли admin
    op.execute(
        """
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT r.id, p.id
        FROM roles r
        CROSS JOIN permissions p
        WHERE r.name = 'admin'
          AND p.code IN ('get_user', 'list_users', 'update_user', 'delete_user')
        ON CONFLICT DO NOTHING
        """
    )


def downgrade() -> None:
    """Удалить пермишены управления пользователями."""
    op.execute(
        """
        DELETE FROM role_permissions
        WHERE permission_id IN (
            SELECT id FROM permissions
            WHERE code IN ('get_user', 'list_users', 'update_user', 'delete_user')
        )
        """
    )
    op.execute(
        """
        DELETE FROM permissions
        WHERE code IN ('get_user', 'list_users', 'update_user', 'delete_user')
        """
    )
