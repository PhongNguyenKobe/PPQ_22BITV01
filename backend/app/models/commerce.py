from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    showtime_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("showtimes.id", ondelete="RESTRICT"), nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    subtotal_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, server_default=text("0"))
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, server_default=text("0"))
    promotion_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("promotions.id", ondelete="SET NULL"))
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'PENDING'"))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    showtime = relationship("Showtime", lazy="selectin")
    seats = relationship("BookingSeat", back_populates="booking", cascade="all, delete-orphan", lazy="selectin")
    payments = relationship("Payment", back_populates="booking", lazy="selectin")
    promotion = relationship("Promotion", lazy="selectin")


class BookingSeat(Base):
    __tablename__ = "booking_seats"
    __table_args__ = (UniqueConstraint("showtime_id", "seat_id", name="uq_booking_seats_showtime_seat"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    booking_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    showtime_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("showtimes.id", ondelete="RESTRICT"), nullable=False)
    seat_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("seats.id", ondelete="RESTRICT"), nullable=False)

    booking = relationship("Booking", back_populates="seats")
    seat = relationship("Seat", lazy="selectin")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    booking_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="RESTRICT"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'PENDING'"))
    transaction_id: Mapped[str | None] = mapped_column(String(150), unique=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    booking = relationship("Booking", back_populates="payments")


class SeatHold(Base):
    __tablename__ = "seat_holds"
    __table_args__ = (UniqueConstraint("showtime_id", "seat_id", name="uq_seat_holds_showtime_seat"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    showtime_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("showtimes.id", ondelete="CASCADE"), nullable=False)
    seat_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("seats.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class Promotion(Base):
    __tablename__ = "promotions"
    __table_args__ = (
        CheckConstraint("discount_value > 0", name="ck_promotions_discount_positive"),
        CheckConstraint("usage_limit IS NULL OR usage_limit >= 0", name="ck_promotions_usage_limit"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    discount_type: Mapped[str] = mapped_column(String(20), nullable=False)
    discount_value: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    max_discount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    min_order_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, server_default=text("0"))
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    usage_limit: Mapped[int | None] = mapped_column(Integer)
    used_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
