from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.permissions import require_admin, require_branch_admin
from app.db.session import get_db
from app.schemas.movie import MovieRead
from app.schemas.admin import AdminStatsResponse, BranchRead, UserRoleUpdate, AdminUserRead
from app.models.user import User

router = APIRouter()

@router.get("/stats", response_model=AdminStatsResponse, dependencies=[Depends(require_admin)])
async def get_admin_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> AdminStatsResponse:
    return AdminStatsResponse(
        totalBranches=5,
        totalMovies=12,
        totalUsers=1250,
        totalRevenue=125000000,
        revenueChartData=[]
    )

@router.get("/users", dependencies=[Depends(require_admin)])
async def list_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    role: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return {"total": 0, "users": []}

@router.put("/users/{user_id}/role", response_model=AdminUserRead, dependencies=[Depends(require_admin)])
async def update_user_role(
    user_id: UUID,
    payload: UserRoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> AdminUserRead:
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pass

@router.post("/movies", response_model=MovieRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
async def create_movie(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> MovieRead:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid movie data")

@router.put("/movies/{movie_id}", response_model=MovieRead, dependencies=[Depends(require_admin)])
async def update_movie(
    movie_id: UUID,
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> MovieRead:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

@router.delete("/movies/{movie_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
async def delete_movie(
    movie_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pass

@router.post("/showtimes", dependencies=[Depends(require_branch_admin)])
async def create_showtime(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pass

@router.put("/showtimes/{showtime_id}", dependencies=[Depends(require_branch_admin)])
async def update_showtime(
    showtime_id: UUID,
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pass

@router.delete("/showtimes/{showtime_id}", dependencies=[Depends(require_branch_admin)])
async def delete_showtime(
    showtime_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pass

@router.get("/branches", dependencies=[Depends(require_admin)])
async def list_branches(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return []

@router.post("/branches", dependencies=[Depends(require_admin)])
async def create_branch(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pass

@router.put("/branches/{branch_id}", dependencies=[Depends(require_admin)])
async def update_branch(
    branch_id: UUID,
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pass

@router.delete("/branches/{branch_id}", dependencies=[Depends(require_admin)])
async def delete_branch(
    branch_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pass

@router.get("/bookings", dependencies=[Depends(require_branch_admin)])
async def list_branch_bookings(
    start_date: str | None = None,
    end_date: str | None = None,
    status: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return {"total": 0, "bookings": []}

@router.put("/bookings/{booking_id}/cancel", dependencies=[Depends(require_branch_admin)])
async def cancel_booking(
    booking_id: UUID,
    reason: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pass

@router.get("/payments", dependencies=[Depends(require_admin)])
async def list_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return {"total": 0, "payments": []}

@router.post("/payments/{payment_id}/refund", dependencies=[Depends(require_admin)])
async def refund_payment(
    payment_id: UUID,
    reason: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pass

@router.get("/reports/revenue", dependencies=[Depends(require_admin)])
async def get_revenue_report(
    start_date: str,
    end_date: str,
    group_by: str = Query("day", pattern="day|week|month"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return {}

@router.get("/reports/occupancy", dependencies=[Depends(require_admin)])
async def get_occupancy_report(
    start_date: str,
    end_date: str,
    branch_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return {}

@router.get("/reports/top-movies", dependencies=[Depends(require_admin)])
async def get_top_movies(
    start_date: str,
    end_date: str,
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return []
