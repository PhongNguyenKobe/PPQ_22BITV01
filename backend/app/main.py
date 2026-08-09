from contextlib import asynccontextmanager
import asyncio
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import settings
from app.core.seat_events import seat_events
from app.crud.booking import cleanup_expired_reservations
from app.db.session import AsyncSessionLocal
from app.models.commerce import Booking, SeatHold
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    stop = asyncio.Event()
    task = asyncio.create_task(cleanup_expired_seats(stop))
    try:
        yield
    finally:
        stop.set()
        await task


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
