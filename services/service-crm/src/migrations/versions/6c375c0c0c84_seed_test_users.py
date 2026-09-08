"""seed test users

Revision ID: 6c375c0c0c84
Revises: 6c375c0c0c83
Create Date: 2026-07-28 12:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import table, column, Integer, String, Boolean, DateTime


# revision identifiers, used by Alembic.
revision: str = "6c375c0c0c84"
down_revision: Union[str, Sequence[str], None] = "6c375c0c0c83"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Определяем таблицу для операций
user_table = table(
    "user",
    column("id", Integer),
    column("email", String),
    column("password_hash", String),
    column("first_name", String),
    column("last_name", String),
    column("is_active", Boolean),
    column("is_banned", Boolean),
    column("is_superuser", Boolean),
    column("is_verified", Boolean),
    column("created_at", DateTime),
    column("updated_at", DateTime),
)


# Тестовые пользователи с новым хешем для пароля "admin"
TEST_USERS = [
    {
        "email": "admin@crm.local",
        "password_hash": "$2b$12$9o9avflc4Ql1/C1S2Y8h5uYJDBkchJgy3YCFlIAO94UdTK9IwWjqS",
        "first_name": "Admin",
        "last_name": "User",
        "is_active": True,
        "is_banned": False,
        "is_superuser": True,
        "is_verified": True,
    },
    {
        "email": "john.doe@example.com",
        "password_hash": "$2b$12$9o9avflc4Ql1/C1S2Y8h5uYJDBkchJgy3YCFlIAO94UdTK9IwWjqS",
        "first_name": "John",
        "last_name": "Doe",
        "is_active": True,
        "is_banned": False,
        "is_superuser": False,
        "is_verified": True,
    }
]


def upgrade() -> None:
    """Upgrade schema."""
    # Вставляем тестовых пользователей
    op.bulk_insert(user_table, TEST_USERS)


def downgrade() -> None:
    """Downgrade schema."""
    # Удаляем только тестовых пользователей
    emails = [user["email"] for user in TEST_USERS]
    op.execute(
        user_table.delete().where(user_table.c.email.in_(emails))
    )
