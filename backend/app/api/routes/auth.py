from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.security import create_access_token, verify_password
from app.crud.user import create_user, get_user_by_identifier
from app.db.session import get_db
from app.schemas.auth import AuthResponse, LoginRequest
from app.schemas.user import UserCreate, UserRead

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> AuthResponse:
    try:
        user = await create_user(db, payload)
    except ValueError as exc:
        message = str(exc)
        if message == "EMAIL_EXISTS":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists") from None
        if message == "PHONE_EXISTS":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone already exists") from None
        if message == "ROLE_NOT_FOUND":
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Default role not found") from None
        raise

    access_token = create_access_token(subject=str(user.id), extra_claims={"roles": [role.code for role in user.roles]})
    return AuthResponse(access_token=access_token, user=UserRead.model_validate(user))


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> AuthResponse:
    user = await get_user_by_identifier(db, payload.identifier)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")

    access_token = create_access_token(subject=str(user.id), extra_claims={"roles": [role.code for role in user.roles]})
    return AuthResponse(access_token=access_token, user=UserRead.model_validate(user))


@router.get("/me", response_model=UserRead)
async def read_me(current_user=Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)
