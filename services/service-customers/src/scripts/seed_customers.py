"""
Скрипт для заполнения БД тестовыми клиентами.
Запускается: python -m src.scripts.seed_customers
"""

import asyncio
import logging

from src.dependencies.db_dependency import DBDependency
from src.dao.customer import CustomerDAO

logger = logging.getLogger(__name__)


# Тестовые клиенты
TEST_CUSTOMERS = [
    {
        "email": "vip@customer.local",
        "phone": "+1234567890",
        "password_hash": "$2b$12$LJ3m4ys3Lk0TSwHCpNqr0uYgVMW8QHqZsCJRqxFvK3jHPzBzHQHXK",
        "first_name": "VIP",
        "last_name": "Client",
        "middle_name": "Important",
    },
    {
        "email": "john.customer@example.com",
        "phone": "+1987654321",
        "password_hash": "$2b$12$LJ3m4ys3Lk0TSwHCpNqr0uYgVMW8QHqZsCJRqxFvK3jHPzBzHQHXK",
        "first_name": "John",
        "last_name": "Customer",
        "middle_name": "Michael",
    },
    {
        "email": "jane.client@example.com",
        "phone": "+1122334455",
        "password_hash": "$2b$12$LJ3m4ys3Lk0TSwHCpNqr0uYgVMW8QHqZsCJRqxFvK3jHPzBzHQHXK",
        "first_name": "Jane",
        "last_name": "Client",
        "middle_name": "Elizabeth",
    },
    {
        "email": "bob.buyer@example.com",
        "phone": "+1555666777",
        "password_hash": "$2b$12$LJ3m4ys3Lk0TSwHCpNqr0uYgVMW8QHqZsCJRqxFvK3jHPzBzHQHXK",
        "first_name": "Bob",
        "last_name": "Buyer",
        "middle_name": "Robert",
    },
    {
        "email": "alice.shopper@example.com",
        "phone": "+1444333222",
        "password_hash": "$2b$12$LJ3m4ys3Lk0TSwHCpNqr0uYgVMW8QHqZsCJRqxFvK3jHPzBzHQHXK",
        "first_name": "Alice",
        "last_name": "Shopper",
        "middle_name": "Marie",
    },
    {
        "email": "corporate@business.local",
        "phone": "+1800100200",
        "password_hash": "$2b$12$LJ3m4ys3Lk0TSwHCpNqr0uYgVMW8QHqZsCJRqxFvK3jHPzBzHQHXK",
        "first_name": "Corporate",
        "last_name": "Business",
        "middle_name": "LTD",
    },
    {
        "email": "mike.retail@example.com",
        "phone": "+1666777888",
        "password_hash": "$2b$12$LJ3m4ys3Lk0TSwHCpNqr0uYgVMW8QHqZsCJRqxFvK3jHPzBzHQHXK",
        "first_name": "Mike",
        "last_name": "Retail",
        "middle_name": "David",
    },
    {
        "email": "emily.wholesale@example.com",
        "phone": "+1777888999",
        "password_hash": "$2b$12$LJ3m4ys3Lk0TSwHCpNqr0uYgVMW8QHqZsCJRqxFvK3jHPzBzHQHXK",
        "first_name": "Emily",
        "last_name": "Wholesale",
        "middle_name": "Ann",
    },
    {
        "email": "sarah.enterprise@example.com",
        "phone": "+1888999000",
        "password_hash": "$2b$12$LJ3m4ys3Lk0TSwHCpNqr0uYgVMW8QHqZsCJRqxFvK3jHPzBzHQHXK",
        "first_name": "Sarah",
        "last_name": "Enterprise",
        "middle_name": "Jane",
    },
    {
        "email": "tech@startup.local",
        "phone": "+1999000111",
        "password_hash": "$2b$12$LJ3m4ys3Lk0TSwHCpNqr0uYgVMW8QHqZsCJRqxFvK3jHPzBzHQHXK",
        "first_name": "Tech",
        "last_name": "Startup",
        "middle_name": "Innovations",
    },
    {
        "email": "partner@business.local",
        "phone": "+1222333444",
        "password_hash": "$2b$12$LJ3m4ys3Lk0TSwHCpNqr0uYgVMW8QHqZsCJRqxFvK3jHPzBzHQHXK",
        "first_name": "Partner",
        "last_name": "Business",
        "middle_name": "And",
    },
    {
        "email": "support@company.local",
        "phone": "+1333444555",
        "password_hash": "$2b$12$LJ3m4ys3Lk0TSwHCpNqr0uYgVMW8QHqZsCJRqxFvK3jHPzBzHQHXK",
        "first_name": "Support",
        "last_name": "Company",
        "middle_name": "Customer",
    },
]


async def seed_customers(force: bool = False) -> dict:
    """
    Заполнение БД тестовыми клиентами.

    Args:
        force: Если True, пытается создать даже существующих клиентов

    Returns:
        dict со статистикой создания
    """
    db = DBDependency()
    customer_dao = CustomerDAO(db)

    created = []
    skipped = []
    failed = []

    logger.info(f"Starting seed: {len(TEST_CUSTOMERS)} test customers")

    for customer_data in TEST_CUSTOMERS:
        try:
            if not force:
                # Проверяем существование перед созданием
                exists = await customer_dao.email_exists(customer_data["email"])
                if exists:
                    skipped.append(customer_data["email"])
                    logger.debug(f"Customer already exists: {customer_data['email']}")
                    continue

            # Создаём клиента — возвращается словарь
            customer_dict = await customer_dao.create(**customer_data)

            # Работаем со словарём
            created.append(customer_dict["email"])
            logger.info(
                f"✅ Created: {customer_dict['first_name']} {customer_dict['last_name']} "
                f"({customer_dict['email']}, ID: {customer_dict['id']})"
            )

        except Exception as e:
            failed.append({"email": customer_data["email"], "error": str(e)})
            logger.error(f"❌ Failed to create {customer_data['email']}: {e}")

    # Вывод статистики
    logger.info("=" * 50)
    logger.info("Seed completed:")
    logger.info(f"  ✅ Created: {len(created)}")
    logger.info(f"  ⏭️  Skipped: {len(skipped)}")
    logger.info(f"  ❌ Failed: {len(failed)}")

    if created:
        logger.info(f"Created customers: {', '.join(created)}")

    if failed:
        logger.error(f"Failed customers: {failed}")

    # Выводим тестовые аккаунты
    logger.info("\n📋 Test customer accounts:")
    logger.info("  VIP: vip@customer.local / admin123")
    logger.info("  Regular: john.customer@example.com / admin123")
    logger.info("  Corporate: corporate@business.local / admin123")
    logger.info("  Tech: tech@startup.local / admin123")

    return {
        "created": len(created),
        "skipped": len(skipped),
        "failed": len(failed),
        "created_emails": created,
        "skipped_emails": skipped,
        "failed_details": failed,
    }


async def verify_seed() -> bool:
    """Проверяет, что тестовые клиенты созданы"""
    db = DBDependency()
    customer_dao = CustomerDAO(db)

    total = await customer_dao.count()
    logger.info(f"Database state: {total} total customers")

    # Проверяем наличие ключевых клиентов
    required_emails = [
        "vip@customer.local",
        "john.customer@example.com",
        "corporate@business.local",
    ]
    for email in required_emails:
        if not await customer_dao.email_exists(email):
            logger.error(f"Required customer missing: {email}")
            return False

    logger.info("✅ All required customers present")
    return True


def main():
    """Точка входа для запуска скрипта"""
    import argparse

    parser = argparse.ArgumentParser(description="Seed test customers into database")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force create customers even if they exist (will fail on duplicates)",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Only verify that required customers exist, don't create",
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
        result = asyncio.run(seed_customers(force=args.force))
        if result["failed"]:
            exit(1)


if __name__ == "__main__":
    main()
