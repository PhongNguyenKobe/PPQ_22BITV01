from fastapi import APIRouter

from app.api.routes.admin import router as admin_router
from app.api.routes.auth import router as auth_router
from app.api.routes.branches import router as branches_router
from app.api.routes.movies import router as movies_router
from app.api.routes.showtimes import router as showtimes_router
from app.api.routes.users import router as users_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(branches_router, prefix="/branches", tags=["branches"])
api_router.include_router(movies_router, prefix="/movies", tags=["movies"])
api_router.include_router(showtimes_router, prefix="/showtimes", tags=["showtimes"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])

