import uuid
from datetime import UTC, datetime

import pytest
import pytest_asyncio
from sqlalchemy import select

from src.dao.customer import CustomerDAO
from src.dao.outbox_dao import OutboxDAO
from src.dependencies.db_dependency import DBDependency
from src.models.customer import Customer
from src.models.outbox_event import OutboxEvent
from src.services.customer import CustomerCreateDTO, CustomerService


@pytest_asyncio.fixture
async def db_dependency():
    dependency = DBDependency()
    try:
        yield dependency
    finally:
        await dependency.close()


@pytest.mark.asyncio
async def test_register_customer_creates_customer_and_atomic_outbox_event(
    db_dependency,
):
    """Создание клиента должно быть атомарно с сохранением события в outbox."""
    customer_id = uuid.uuid4().hex[:8]
    email = f"demo-{customer_id}@example.com"
    customer_dao = CustomerDAO(db_dependency)
    outbox_dao = OutboxDAO(db_dependency)
    service = CustomerService(customer_dao, outbox_dao)

    dto = CustomerCreateDTO(
        email=email,
        phone=f"+100{customer_id}",
        password_hash="hashed-password",
        first_name="Demo",
        last_name="Customer",
        middle_name="Kafka",
    )

    created = await service.register_customer(dto)

    async with db_dependency.read_only_scope() as session:
        customer = await session.get(Customer, created.id)
        event = await session.execute(
            select(OutboxEvent).where(
                OutboxEvent.aggregate_type == "customer",
                OutboxEvent.aggregate_id == created.id,
                OutboxEvent.event_type == "customer.created.v1",
            )
        )
        event = event.scalar_one()

        assert customer is not None
        assert customer.email == email
        assert event.payload["customer_id"] == created.id
        assert event.payload["email_hash"]
        assert event.payload["created_at"] == created.created_at.isoformat().replace("T", " ")
        assert event.processed_at is None


@pytest.mark.asyncio
async def test_outbox_relay_marks_event_processed_after_batch(db_dependency):
    """DAO должен помечать опубликованные события без изменения бизнес-данных."""
    outbox_dao = OutboxDAO(db_dependency)
    event_id = uuid.uuid4()
    now = datetime.now(UTC)

    async with db_dependency.session_scope() as session:
        session.add(
            OutboxEvent(
                id=event_id,
                aggregate_type="customer",
                aggregate_id=999999,
                event_type="customer.created.v1",
                payload={"event_id": str(event_id), "customer_id": 999999},
                created_at=now,
            )
        )

    await outbox_dao.mark_processed([event_id])

    async with db_dependency.read_only_scope() as session:
        event = await session.get(OutboxEvent, event_id)

        assert event is not None
        assert event.processed_at is not None
