from contextlib import asynccontextmanager
import asyncio
from datetime import datetime, timezone, timedelta
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import settings
from app.core.seat_events import seat_events
from app.crud.booking import cleanup_expired_reservations
from app.db.session import AsyncSessionLocal
from app.models.commerce import Booking, SeatHold, NotificationOutbox
from app.models.user import User
from app.services.email import send_transactional_email
from sqlalchemy import select


async def cleanup_expired_seats(stop: asyncio.Event) -> None:
    while not stop.is_set():
        try:
            async with AsyncSessionLocal() as db:
                showtime_ids = set((await db.execute(
                    select(SeatHold.showtime_id).where(SeatHold.expires_at <= datetime.now(timezone.utc))
                )).scalars().all())
                showtime_ids.update((await db.execute(
                    select(Booking.showtime_id).where(
                        Booking.status == "PENDING",
                        Booking.expires_at.is_not(None),
                        Booking.expires_at <= datetime.now(timezone.utc),
                    )
                )).scalars().all())
                await cleanup_expired_reservations(db)
                await db.commit()
            for showtime_id in showtime_ids:
                await seat_events.broadcast(showtime_id, "SEATS_UPDATED")
        except Exception:
            # The next cycle retries; request handling must remain available.
            pass
        try:
            await asyncio.wait_for(stop.wait(), timeout=15)
        except TimeoutError:
            continue


async def process_notification_outbox(stop: asyncio.Event) -> None:
    def render_msg(event_type: str, payload: dict) -> tuple[str, str]:
        if event_type == "TICKET_ISSUED":
            return "Vé CineAI đã được phát hành", f"Thanh toán thành công. Mã đặt vé: {payload.get('ticket_code')}."
        if event_type == "PAYMENT_RECONCILIATION_REQUIRED":
            return "Giao dịch CineAI đang được kiểm tra", "Khoản thanh toán đã được ghi nhận sau khi giữ chỗ hết hạn. CineAI đang đối soát và sẽ hoàn tiền nếu không thể cấp vé."
        return "Thông báo từ CineAI", str(payload)

    while not stop.is_set():
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(NotificationOutbox)
                    .where(NotificationOutbox.status == "PENDING", NotificationOutbox.available_at <= datetime.now(timezone.utc))
                    .order_by(NotificationOutbox.created_at)
                    .limit(10)
                    .with_for_update(skip_locked=True)
                )
                items = result.scalars().all()
                for item in items:
                    user = await db.get(User, item.user_id)
                    subject, body = render_msg(item.event_type, item.payload)
                    sent = False
                    if user and user.email:
                        try:
                            sent = await asyncio.to_thread(send_transactional_email, user.email, subject, body)
                        except Exception:
                            pass
                    item.attempts += 1
                    if sent:
                        item.status = "SENT"
                        item.sent_at = datetime.now(timezone.utc)
                        item.last_error = None
                    elif item.attempts >= 5:
                        item.status = "FAILED"
                        item.last_error = "Delivery failed after five attempts"
                    else:
                        item.available_at = datetime.now(timezone.utc) + timedelta(minutes=2 ** item.attempts)
                        item.last_error = "Delivery failed; retry scheduled"
                await db.commit()
        except Exception:
            pass
        try:
            await asyncio.wait_for(stop.wait(), timeout=15)
        except TimeoutError:
            continue


@asynccontextmanager
async def lifespan(app: FastAPI):
    stop = asyncio.Event()
    task1 = asyncio.create_task(cleanup_expired_seats(stop))
    task2 = asyncio.create_task(process_notification_outbox(stop))
    try:
        yield
    finally:
        stop.set()
        await asyncio.gather(task1, task2, return_exceptions=True)


app = FastAPI(title=settings.app_name, lifespan=lifespan)
uploads_dir = Path(__file__).resolve().parents[1] / "uploads"
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    # Nuxt tự chuyển sang 3001, 3002... khi cổng 3000 đang được dùng.
    # Chỉ nới cho loopback local; production origins vẫn lấy từ cấu hình.
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    return {"message": "PPQ API is running"}


@app.get("/health")
async def health():
    return {"status": "ok"}
