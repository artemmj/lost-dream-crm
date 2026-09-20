import hashlib
import uuid
from dataclasses import dataclass, asdict


@dataclass
class CustomerCreatedEvent:
    """Событие создания клиента. PII заменены на хеши."""

    event_id: str
    customer_id: int
    email_hash: str
    created_at: str

    @classmethod
    def from_customer_dict(cls, customer: dict) -> "CustomerCreatedEvent":
        """Фабрика из словаря, который возвращает DAO"""
        raw_email = customer.get("email", "")
        # PII primitive: SHA-256 хеш вместо реального email
        email_hash = hashlib.sha256(raw_email.encode()).hexdigest()[:16]

        return cls(
            event_id=str(uuid.uuid4()),
            customer_id=customer["id"],
            email_hash=email_hash,
            created_at=str(customer["created_at"]),
        )

    def to_payload(self) -> dict:
        """Словарь для записи в JSONB колонку outbox.payload"""
        return asdict(self)
