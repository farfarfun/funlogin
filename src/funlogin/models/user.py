from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from funlogin.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_utcnow, onupdate=_utcnow
    )


class UserCredential(Base):
    __tablename__ = "user_credentials"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    identifier: Mapped[str] = mapped_column(String(255), nullable=False)
    secret_hash: Mapped[str] = mapped_column(String(255), default="")

    __table_args__ = (
        UniqueConstraint("type", "identifier", name="uq_credential_type_identifier"),
    )
