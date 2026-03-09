from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from funlogin.core.database import Base


class QQBinding(Base):
    __tablename__ = "qq_bindings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    openid: Mapped[str] = mapped_column(String(128), nullable=False)
    unionid: Mapped[str] = mapped_column(String(128), default="")
    nickname: Mapped[str] = mapped_column(String(128), default="")
    avatar_url: Mapped[str] = mapped_column(String(512), default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (UniqueConstraint("openid", name="uq_qq_openid"),)


class WeChatBinding(Base):
    __tablename__ = "wechat_bindings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    openid: Mapped[str] = mapped_column(String(128), nullable=False)
    unionid: Mapped[str] = mapped_column(String(128), default="")
    nickname: Mapped[str] = mapped_column(String(128), default="")
    avatar_url: Mapped[str] = mapped_column(String(512), default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (UniqueConstraint("openid", name="uq_wechat_openid"),)


class PhoneBinding(Base):
    __tablename__ = "phone_bindings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (UniqueConstraint("phone", name="uq_phone"),)
