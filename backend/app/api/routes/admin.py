from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.security import require_admin, require_branch_admin
from app.db.session import get_db
from app.schemas.movie import MovieRead
from app.schemas.admin import AdminStatsResponse, BranchRead, UserRoleUpdate, AdminUserRead
from app.models.user import User

router = APIRouter()


# ============================================================
# ADMIN - ONLY SUPER ADMIN ACCESS
# ============================================================

@router.get("/stats", response_model=AdminStatsResponse, dependencies=[Depends(require_admin)])
async def get_admin_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> AdminStatsResponse:
    """
    Get admin dashboard statistics (SUPER_ADMIN only)
    - Total branches, movies, users
    - Revenue analytics
    - Active showtimes
    """
    # TODO: Fetch from database
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
    """
    List all users with optional role filter (SUPER_ADMIN only)
    - Filter by role: CUSTOMER, ADMIN, BRANCH_ADMIN, STAFF
    - Paginated results
    """
    # TODO: Fetch users from database with pagination
    return {"total": 0, "users": []}


@router.put("/users/{user_id}/role", response_model=AdminUserRead, dependencies=[Depends(require_admin)])
async def update_user_role(
    user_id: UUID,
    payload: UserRoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> AdminUserRead:
    """
    Update user role (SUPER_ADMIN only)
    - Assign roles: CUSTOMER, ADMIN, BRANCH_ADMIN, STAFF
    - Assign branch for BRANCH_ADMIN and STAFF
    """
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    # TODO: Update user role in database
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete user account (SUPER_ADMIN only)
    - Soft delete (mark as inactive)
    - Preserve user data for auditing
    """
    # TODO: Soft delete user
    pass


# ============================================================
# MOVIE MANAGEMENT - ADMIN & BRANCH_ADMIN
# ============================================================

@router.post("/movies", response_model=MovieRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
async def create_movie(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> MovieRead:
    """
    Create new movie (SUPER_ADMIN only)
    - Add movie from TMDB or manual entry
    - Set genres, duration, age rating
    - Upload poster and trailer
    """
    # TODO: Create movie in database
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid movie data")


@router.put("/movies/{movie_id}", response_model=MovieRead, dependencies=[Depends(require_admin)])
async def update_movie(
    movie_id: UUID,
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> MovieRead:
    """
    Update movie information (SUPER_ADMIN only)
    - Edit title, description, duration
    - Change genres, rating
    - Update poster/trailer URLs
    """
    # TODO: Update movie in database
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")


@router.delete("/movies/{movie_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
async def delete_movie(
    movie_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete movie (SUPER_ADMIN only)
    - Soft delete to preserve booking history
    - Archive movie data
    """
    # TODO: Soft delete movie
    pass


# ============================================================
# SHOWTIME MANAGEMENT - BRANCH_ADMIN & STAFF
# ============================================================

@router.post("/showtimes", dependencies=[Depends(require_branch_admin)])
async def create_showtime(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create new showtime (BRANCH_ADMIN & STAFF)
    - Assign movie, auditorium, time
    - Set ticket price
    - Open for bookings
    """
    # TODO: Create showtime
    pass


@router.put("/showtimes/{showtime_id}", dependencies=[Depends(require_branch_admin)])
async def update_showtime(
    showtime_id: UUID,
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update showtime (BRANCH_ADMIN & STAFF)
    - Change time, price
    - Modify auditorium
    - Update status (OPEN, CANCELLED)
    """
    # TODO: Update showtime
    pass


@router.delete("/showtimes/{showtime_id}", dependencies=[Depends(require_branch_admin)])
async def delete_showtime(
    showtime_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete/Cancel showtime (BRANCH_ADMIN & STAFF)
    - Cancel future showtimes
    - Refund existing bookings
    """
    # TODO: Delete showtime
    pass


# ============================================================
# BRANCH MANAGEMENT - SUPER_ADMIN
# ============================================================

@router.get("/branches", dependencies=[Depends(require_admin)])
async def list_branches(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all cinema branches (SUPER_ADMIN)
    """
    # TODO: Fetch branches
    return []


@router.post("/branches", dependencies=[Depends(require_admin)])
async def create_branch(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create new cinema branch (SUPER_ADMIN)
    - Add location, phone, address
    - Set operating hours
    - Add auditoriums
    """
    # TODO: Create branch
    pass


@router.put("/branches/{branch_id}", dependencies=[Depends(require_admin)])
async def update_branch(
    branch_id: UUID,
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update branch information (SUPER_ADMIN)
    """
    # TODO: Update branch
    pass


@router.delete("/branches/{branch_id}", dependencies=[Depends(require_admin)])
async def delete_branch(
    branch_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete branch (SUPER_ADMIN)
    """
    # TODO: Delete branch
    pass


# ============================================================
# BOOKING MANAGEMENT - BRANCH_ADMIN & STAFF
# ============================================================

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
    """
    List bookings for branch (BRANCH_ADMIN & STAFF)
    - Filter by date range, status
    - View revenue per showtime
    """
    # TODO: Fetch branch bookings
    return {"total": 0, "bookings": []}


@router.put("/bookings/{booking_id}/cancel", dependencies=[Depends(require_branch_admin)])
async def cancel_booking(
    booking_id: UUID,
    reason: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel booking and refund (BRANCH_ADMIN & STAFF)
    """
    # TODO: Cancel booking and process refund
    pass


# ============================================================
# PAYMENT MANAGEMENT - ADMIN ONLY
# ============================================================

@router.get("/payments", dependencies=[Depends(require_admin)])
async def list_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all payments (SUPER_ADMIN)
    - Filter by status: PENDING, SUCCESS, FAILED, REFUNDED
    - Payment analytics
    """
    # TODO: Fetch payments
    return {"total": 0, "payments": []}


@router.post("/payments/{payment_id}/refund", dependencies=[Depends(require_admin)])
async def refund_payment(
    payment_id: UUID,
    reason: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Process refund for payment (SUPER_ADMIN)
    """
    # TODO: Process refund
    pass


# ============================================================
# REPORTS & ANALYTICS - ADMIN ONLY
# ============================================================

@router.get("/reports/revenue", dependencies=[Depends(require_admin)])
async def get_revenue_report(
    start_date: str,
    end_date: str,
    group_by: str = Query("day", regex="day|week|month"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Revenue report by date range (SUPER_ADMIN)
    - Group by day, week, or month
    - Show payment methods breakdown
    """
    # TODO: Generate revenue report
    return {}


@router.get("/reports/occupancy", dependencies=[Depends(require_admin)])
async def get_occupancy_report(
    start_date: str,
    end_date: str,
    branch_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Seat occupancy report (SUPER_ADMIN & BRANCH_ADMIN)
    - Occupancy rate per showtime
    - Popular showtimes
    """
    # TODO: Generate occupancy report
    return {}


@router.get("/reports/top-movies", dependencies=[Depends(require_admin)])
async def get_top_movies(
    start_date: str,
    end_date: str,
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Top movies by bookings (SUPER_ADMIN)
    - Most booked movies
    - Revenue per movie
    """
    # TODO: Get top movies
    return []
