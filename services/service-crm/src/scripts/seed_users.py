"""
Скрипт для заполнения БД тестовыми пользователями.
Запускается: python -m src.scripts.seed_users
"""

import asyncio
import logging
from typing import List

from src.dependencies.db_dependency import DBDependency
from src.dao.user import UserDAO

logger = logging.getLogger(__name__)


# Тестовые пользователи (без id - генерируется автоматически)
TEST_USERS = [
    {
        "email": "admin@crm.local",
        "password_hash": "$2b$12$LJ3m4ys3Lk0TSwHCpNqr0uYgVMW8QHqZsCJRqxFvK3jHPzBzHQHXK",
        "first_name": "Admin",
        "last_name": "User",
        "is_active": True,
        "is_banned": False,
        "is_superuser": True,
        "is_verified": True,
    },
    {
        "email": "john.doe@example.com",
        "password_hash": "$2b$12$LJ3m4ys3Lk0TSwHCpNqr0uYgVMW8QHqZsCJRqxFvK3jHPzBzHQHXK",
        "first_name": "John",
        "last_name": "Doe",
        "is_active": True,
        "is_banned": False,
        "is_superuser": False,
        "is_verified": True,
    },
    {
        "email": "jane.smith@example.com",
        "password_hash": "$2b$12$LJ3m4ys3Lk0TSwHCpNqr0uYgVMW8QHqZsCJRqxFvK3jHPzBzHQHXK",
        "first_name": "Jane",
        "last_name": "Smith",
        "is_active": True,
        "is_banned": False,
        "is_superuser": False,
        "is_verified": True,
    },
    {
        "email": "bob.johnson@example.com",
        "password_hash": "$2b$12$LJ3m4ys3Lk0TSwHCpNqr0uYgVMW8QHqZsCJRqxFvK3jHPzBzHQHXK",
        "first_name": "Bob",
        "last_name": "Johnson",
        "is_active": True,
        "is_banned": False,
        "is_superuser": False,
        "is_verified": False,
    },
    {
        "email": "alice.williams@example.com",
        "password_hash": "$2b$12$LJ3m4ys3Lk0TSwHCpNqr0uYgVMW8QHqZsCJRqxFvK3jHPzBzHQHXK",
        "first_name": "Alice",
        "last_name": "Williams",
        "is_active": True,
        "is_banned": False,
        "is_superuser": False,
        "is_verified": True,
    },
    {
        "email": "inactive@crm.local",
        "password_hash": "$2b$12$LJ3m4ys3Lk0TSwHCpNqr0uYgVMW8QHqZsCJRqxFvK3jHPzBzHQHXK",
        "first_name": "Inactive",
        "last_name": "User",
        "is_active": False,
        "is_banned": False,
        "is_superuser": False,
        "is_verified": False,
    },
    {
        "email": "banned@crm.local",
        "password_hash": "$2b$12$LJ3m4ys3Lk0TSwHCpNqr0uYgVMW8QHqZsCJRqxFvK3jHPzBzHQHXK",
        "first_name": "Banned",
        "last_name": "User",
        "is_active": False,
        "is_banned": True,
        "is_superuser": False,
        "is_verified": False,
    },
    {
        "email": "manager@crm.local",
        "password_hash": "$2b$12$LJ3m4ys3Lk0TSwHCpNqr0uYgVMW8QHqZsCJRqxFvK3jHPzBzHQHXK",
        "first_name": "Test",
        "last_name": "Manager",
        "is_active": True,
        "is_banned": False,
        "is_superuser": False,
        "is_verified": True,
    },
    {
        "email": "sarah.connor@example.com",
        "password_hash": "$2b$12$LJ3m4ys3Lk0TSwHCpNqr0uYgVMW8QHqZsCJRqxFvK3jHPzBzHQHXK",
        "first_name": "Sarah",
        "last_name": "Connor",
        "is_active": True,
        "is_banned": False,
        "is_superuser": False,
        "is_verified": True,
    },
    {
        "email": "mike.brown@example.com",
        "password_hash": "$2b$12$LJ3m4ys3Lk0TSwHCpNqr0uYgVMW8QHqZsCJRqxFvK3jHPzBzHQHXK",
        "first_name": "Mike",
        "last_name": "Brown",
        "is_active": True,
        "is_banned": False,
        "is_superuser": False,
        "is_verified": False,
    },
    {
        "email": "emily.davis@example.com",
        "password_hash": "$2b$12$LJ3m4ys3Lk0TSwHCpNqr0uYgVMW8QHqZsCJRqxFvK3jHPzBzHQHXK",
        "first_name": "Emily",
        "last_name": "Davis",
        "is_active": True,
        "is_banned": False,
        "is_superuser": False,
        "is_verified": True,
    },
    {
        "email": "unverified@crm.local",
        "password_hash": "$2b$12$LJ3m4ys3Lk0TSwHCpNqr0uYgVMW8QHqZsCJRqxFvK3jHPzBzHQHXK",
        "first_name": "Unverified",
        "last_name": "User",
        "is_active": True,
        "is_banned": False,
        "is_superuser": False,
        "is_verified": False,
    },
]


async def seed_users(force: bool = False) -> dict:
    """
    Заполнение БД тестовыми пользователями.

    Args:
        force: Если True, пытается создать даже существующих пользователей

    Returns:
        dict со статистикой создания
    """
    db = DBDependency()
    user_dao = UserDAO(db)

    created = []
    skipped = []
    failed = []

    logger.info(f"Starting seed: {len(TEST_USERS)} test users")

    for user_data in TEST_USERS:
        try:
            if not force:
                # Проверяем существование перед созданием
                exists = await user_dao.email_exists(user_data["email"])
                if exists:
                    skipped.append(user_data["email"])
                    logger.debug(f"User already exists: {user_data['email']}")
                    continue

            # Создаём пользователя — теперь возвращается словарь
            user_dict = await user_dao.create(**user_data)

            # Работаем со словарём, не с объектом
            created.append(user_dict["email"])
            logger.info(f"✅ Created: {user_dict['email']} (ID: {user_dict['id']})")

        except Exception as e:
            failed.append({"email": user_data["email"], "error": str(e)})
            logger.error(f"❌ Failed to create {user_data['email']}: {e}")

    # Вывод статистики
    logger.info("=" * 50)
    logger.info("Seed completed:")
    logger.info(f"  ✅ Created: {len(created)}")
    logger.info(f"  ⏭️  Skipped: {len(skipped)}")
    logger.info(f"  ❌ Failed: {len(failed)}")

    if created:
        logger.info(f"Created users: {', '.join(created)}")

    if failed:
        logger.error(f"Failed users: {failed}")

    # Выводим тестовые аккаунты для входа
    logger.info("\n📋 Test accounts for login:")
    logger.info("  Superuser: admin@crm.local / admin123")
    logger.info("  Active: john.doe@example.com / admin123")
    logger.info("  Inactive: inactive@crm.local / admin123")
    logger.info("  Banned: banned@crm.local / admin123")
    logger.info("  Unverified: unverified@crm.local / admin123")

    return {
        "created": len(created),
        "skipped": len(skipped),
        "failed": len(failed),
        "created_emails": created,
        "skipped_emails": skipped,
        "failed_details": failed,
    }


async def verify_seed() -> bool:
    """Проверяет, что тестовые пользователи созданы"""
    db = DBDependency()
    user_dao = UserDAO(db)

    total = await user_dao.count()
    active = len(await user_dao.get_active_users())

    logger.info(f"Database state: {total} total users, {active} active")

    # Проверяем наличие ключевых пользователей
    required_emails = ["admin@crm.local", "john.doe@example.com"]
    for email in required_emails:
        if not await user_dao.email_exists(email):
            logger.error(f"Required user missing: {email}")
            return False

    logger.info("✅ All required users present")
    return True


def main():
    """Точка входа для запуска скрипта"""
    import argparse

    parser = argparse.ArgumentParser(description="Seed test users into database")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force create users even if they exist (will fail on duplicates)",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Only verify that required users exist, don't create",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )

    args = parser.parse_args()

    # Настройка логирования
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if args.verify:
        success = asyncio.run(verify_seed())
        exit(0 if success else 1)
    else:
        result = asyncio.run(seed_users(force=args.force))
        if result["failed"]:
            exit(1)


if __name__ == "__main__":
    main()
