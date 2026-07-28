from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.admin import BranchDetailRead, BranchRead

router = APIRouter()


@router.get("", response_model=list[BranchRead])
async def read_branches(db: AsyncSession = Depends(get_db)) -> list[BranchRead]:
    """Public endpoint để lấy danh sách rạp chiếu."""
    result = await db.execute(text("SELECT id, code, name, city FROM branches ORDER BY name ASC"))
    return [BranchRead(id=row.id, code=row.code, name=row.name, city=row.city) for row in result]


@router.get("/{branch_id}", response_model=BranchDetailRead)
async def read_branch(branch_id: UUID, db: AsyncSession = Depends(get_db)) -> BranchDetailRead:
    branch = (await db.execute(text("""
        SELECT id, code, name, city, address_line, district, phone, latitude, longitude
        FROM branches WHERE id = :id AND is_active = TRUE
    """), {"id": str(branch_id)})).mappings().first()
    if branch is None:
        raise HTTPException(status_code=404, detail="Branch not found")
    rows = (await db.execute(text("""
        SELECT s.id, s.movie_id, s.auditorium_id, s.starts_at, s.ends_at,
               s.status, s.booking_closes_at, s.base_price,
               a.name AS screen_name, m.title, m.original_title, m.description,
               m.duration_min, m.release_date, m.age_rating, m.language,
               m.trailer_url, m.poster_url, m.status AS movie_status,
               m.created_at, m.updated_at
        FROM showtimes s
        JOIN auditoriums a ON a.id = s.auditorium_id
        JOIN movies m ON m.id = s.movie_id
        WHERE a.branch_id = :id AND s.status = 'OPEN' AND s.booking_closes_at > NOW()
        ORDER BY s.starts_at
    """), {"id": str(branch_id)})).mappings().all()
    movies = {}
    showtimes = []
    for row in rows:
        movies[str(row["movie_id"])] = {
            "id": row["movie_id"], "title": row["title"], "original_title": row["original_title"],
            "description": row["description"], "duration_min": row["duration_min"],
            "release_date": row["release_date"], "age_rating": row["age_rating"],
            "language": row["language"], "trailer_url": row["trailer_url"],
            "poster_url": row["poster_url"], "status": row["movie_status"],
            "created_at": row["created_at"], "updated_at": row["updated_at"], "genres": [],
        }
        showtimes.append({
            "id": row["id"], "movie_id": row["movie_id"], "auditorium_id": row["auditorium_id"],
            "starts_at": row["starts_at"], "ends_at": row["ends_at"], "status": row["status"],
            "booking_closes_at": row["booking_closes_at"], "base_price": row["base_price"],
            "branch_name": branch["name"], "screen_name": row["screen_name"],
        })
    return BranchDetailRead(**branch, movies=list(movies.values()), showtimes=showtimes)

