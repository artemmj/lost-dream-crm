from dataclasses import dataclass, asdict
import hashlib


@dataclass
class CustomerCreatedEvent:
    event_id: str
    customer_id: int
    email_hash: str  # PII primitive: хеш вместо email
    created_at: str

    @classmethod
    def from_customer_dict(cls, customer: dict, event_id: str) -> "CustomerCreatedEvent":
        return cls(
            event_id=event_id,
            customer_id=customer["id"],
            email_hash=hashlib.sha256(customer["email"].encode()).hexdigest()[:16],
            created_at=customer["created_at"].isoformat(),
        )

    def to_payload(self) -> dict:
        return asdict(self)
