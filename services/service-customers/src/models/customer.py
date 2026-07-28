from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.models import Base, IDMixin, CreatedAtUpdatedAtMixin


class Customer(Base, IDMixin, CreatedAtUpdatedAtMixin):
    phone: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    first_name: Mapped[str | None] = mapped_column(String(63), nullable=False)
    last_name: Mapped[str | None] = mapped_column(String(63), nullable=False)
    middle_name: Mapped[str | None] = mapped_column(String(63), nullable=True)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, email={self.email})"
