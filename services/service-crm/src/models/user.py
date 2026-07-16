from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models import Base, CreatedAtUpdatedAtMixin


class User(Base, CreatedAtUpdatedAtMixin):
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    first_name: Mapped[str | None] = mapped_column(String(63), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(63), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, email={self.email})"
