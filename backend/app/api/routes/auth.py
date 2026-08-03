from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.security import create_access_token, verify_password, get_password_hash
from app.crud.user import create_user, get_user_by_identifier, get_user_by_id
from app.db.session import get_db
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    CheckIdentifierRequest,
    VerifyOtpRequest,
    ResendOtpRequest,
    RegisterResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from app.schemas.user import UserCreate, UserRead
from app.services.email import generate_otp, send_verification_email

router = APIRouter()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> RegisterResponse:
    try:
        user = await create_user(db, payload)
    except ValueError as exc:
        message = str(exc)
        if message == "EMAIL_EXISTS":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email đã được sử dụng") from None
        if message == "PHONE_EXISTS":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Số điện thoại đã được sử dụng") from None
        if message == "ROLE_NOT_FOUND":
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Vai trò mặc định không tìm thấy") from None
        raise

    # Sinh mã OTP và lưu vào DB
    otp = generate_otp()
    user.verification_code = otp
    user.verification_code_expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    db.add(user)
    await db.commit()

    # Gửi mã xác nhận qua email
    sent = send_verification_email(user.email, otp)
    if not sent:
        # Nếu gửi thất bại, chúng ta có thể ghi log, nhưng vẫn tiếp tục để người dùng có thể gửi lại
        pass

    return RegisterResponse(message="Mã xác thực OTP đã được gửi tới email của bạn.", email=user.email)


@router.post("/login", response_model=AuthResponse)
async def login(request: Request, db: AsyncSession = Depends(get_db)) -> AuthResponse:
    content_type = request.headers.get("content-type", "")

    identifier: str
    password: str

    if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        form = await request.form()
        identifier = str(form.get("username") or "").strip()
        password = str(form.get("password") or "")
    else:
        try:
            payload = LoginRequest.model_validate(await request.json())
        except (ValidationError, ValueError) as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="identifier and password are required",
            ) from exc
        identifier = payload.identifier
        password = payload.password

    user = await get_user_by_identifier(db, identifier)
    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email, số điện thoại hoặc mật khẩu không chính xác")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tài khoản đã bị khóa")

    # Chỉ yêu cầu xác thực is_verified đối với vai trò CUSTOMER
    is_customer = any(role.code == "CUSTOMER" for role in user.roles)
    if is_customer and not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="USER_NOT_VERIFIED"
        )

    access_token = create_access_token(subject=str(user.id), extra_claims={"roles": [role.code for role in user.roles]})
    return AuthResponse(access_token=access_token, user=UserRead.model_validate(user))


@router.get("/me", response_model=UserRead)
async def read_me(current_user=Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)


@router.post("/check-identifier")
async def check_identifier(payload: CheckIdentifierRequest, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_identifier(db, payload.identifier)
    if user:
        is_email = "@" in payload.identifier
        return {"exists": True, "type": "email" if is_email else "phone"}
    return {"exists": False}


@router.post("/verify-otp", response_model=AuthResponse)
async def verify_otp(payload: VerifyOtpRequest, db: AsyncSession = Depends(get_db)) -> AuthResponse:
    user = await get_user_by_identifier(db, payload.identifier)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy thông tin tài khoản")

    if user.is_verified:
        fresh_user = await get_user_by_id(db, user.id)
        access_token = create_access_token(subject=str(fresh_user.id), extra_claims={"roles": [role.code for role in fresh_user.roles]})
        return AuthResponse(access_token=access_token, user=UserRead.model_validate(fresh_user))

    if not user.verification_code or user.verification_code != payload.code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mã xác thực OTP không chính xác")

    # Kiểm tra hết hạn
    if user.verification_code_expires_at:
        expires_at = user.verification_code_expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expires_at:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mã xác thực OTP đã hết hạn")

    # Xác thực thành công
    user.is_verified = True
    user.verification_code = None
    user.verification_code_expires_at = None
    db.add(user)
    await db.commit()

    # Tải lại user tươi mới cùng với roles được selectinload để tránh lỗi MissingGreenlet
    fresh_user = await get_user_by_id(db, user.id)
    access_token = create_access_token(subject=str(fresh_user.id), extra_claims={"roles": [role.code for role in fresh_user.roles]})
    return AuthResponse(access_token=access_token, user=UserRead.model_validate(fresh_user))


@router.post("/resend-otp")
async def resend_otp(payload: ResendOtpRequest, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_identifier(db, payload.identifier)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy thông tin tài khoản")

    otp = generate_otp()
    user.verification_code = otp
    user.verification_code_expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    db.add(user)
    await db.commit()

    sent = send_verification_email(user.email, otp)
    if not sent:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Không thể gửi email OTP. Vui lòng thử lại sau.")

    return {"message": "Mã xác thực OTP mới đã được gửi tới email của bạn."}


@router.post("/forgot-password")
async def forgot_password(payload: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_identifier(db, payload.identifier)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy tài khoản với thông tin đã nhập")

    # Sinh mã OTP mới để khôi phục mật khẩu
    otp = generate_otp()
    user.verification_code = otp
    user.verification_code_expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    db.add(user)
    await db.commit()

    # Gửi email SMTP
    sent = send_verification_email(user.email, otp, email_type="forgot")
    if not sent:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Không thể gửi email chứa mã khôi phục. Vui lòng thử lại sau.")

    return {"message": "Mã xác thực OTP đã được gửi tới email khôi phục của bạn."}


@router.post("/reset-password")
async def reset_password(payload: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_identifier(db, payload.identifier)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy thông tin tài khoản")

    if not user.verification_code or user.verification_code != payload.code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mã xác thực OTP không chính xác")

    if user.verification_code_expires_at:
        expires_at = user.verification_code_expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expires_at:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mã xác thực OTP đã hết hạn")

    # Cập nhật mật khẩu mới và xóa mã xác thực
    user.password_hash = get_password_hash(payload.new_password)
    user.is_verified = True  # Nếu tài khoản chưa verify thì verify luôn
    user.verification_code = None
    user.verification_code_expires_at = None
    db.add(user)
    await db.commit()

    return {"message": "Đặt lại mật khẩu thành công. Vui lòng đăng nhập lại bằng mật khẩu mới."}


