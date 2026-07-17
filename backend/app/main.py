from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

app = FastAPI(title="CineAI API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
security = HTTPBearer(auto_error=False)

SECRET_KEY = "cineai-super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: str
    email: str


class UserRecord(BaseModel):
    email: str
    password: str
    role: str
    name: str


USERS = {
    "customer@gmail.com": UserRecord(
        email="customer@gmail.com",
        password="customer123",
        role="customer",
        name="Nguyễn Đăng Khách",
    ),
    "admin@cineai.vn": UserRecord(
        email="admin@cineai.vn",
        password="admin123",
        role="admin",
        name="Admin CineAI",
    ),
    "branch@cineai.vn": UserRecord(
        email="branch@cineai.vn",
        password="branch123",
        role="branch-admin",
        name="Sala Branch Manager",
    ),
}


def create_access_token(email: str, role: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": email, "role": role, "exp": expires_at}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(email: str, password: str) -> UserRecord | None:
    user = USERS.get(email)
    if not user or user.password != password:
        return None
    return user


def register_user(name: str, email: str, password: str) -> UserRecord:
    if email in USERS:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = UserRecord(email=email, password=password, role="customer", name=name)
    USERS[email] = user
    return user


def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)]):
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    email = payload.get("sub")
    role = payload.get("role")
    if not email or not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = USERS.get(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


def require_role(required_role: str):
    def dependency(user: Annotated[UserRecord, Depends(get_current_user)]):
        if user.role != required_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return user

    return dependency


class OrderItemCreate(BaseModel):
    product_id: str
    title: str
    quantity: int
    unit_price: float


class OrderItem(BaseModel):
    product_id: str
    title: str
    quantity: int
    unit_price: float
    total_price: float


class OrderCreateRequest(BaseModel):
    items: list[OrderItemCreate]


class OrderResponse(BaseModel):
    id: str
    user_email: str
    items: list[OrderItem]
    subtotal_amount: float
    total_amount: float
    status: str
    created_at: datetime


ORDERS: dict[str, OrderResponse] = {}


@contextmanager
def transaction():
    backup = ORDERS.copy()
    try:
        yield
    except Exception:
        ORDERS.clear()
        ORDERS.update(backup)
        raise


@app.get("/")
def root() -> dict:
    return {"message": "CineAI API is running"}


@app.post("/api/orders/checkout", response_model=OrderResponse)
def checkout_order(
    payload: OrderCreateRequest,
    user: Annotated[UserRecord, Depends(get_current_user)],
):
    if len(payload.items) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No order items provided")

    items = []
    for item in payload.items:
        if item.quantity <= 0 or item.unit_price < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid order item")
        items.append(
            OrderItem(
                product_id=item.product_id,
                title=item.title,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.quantity * item.unit_price,
            )
        )

    subtotal = sum(item.total_price for item in items)
    if subtotal <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid order total")

    with transaction():
        order_id = str(uuid4())
        order = OrderResponse(
            id=order_id,
            user_email=user.email,
            items=items,
            subtotal_amount=subtotal,
            total_amount=subtotal,
            status="PENDING",
            created_at=datetime.now(timezone.utc),
        )
        ORDERS[order_id] = order

    return order


@app.get("/api/orders/my", response_model=list[OrderResponse])
def get_my_orders(user: Annotated[UserRecord, Depends(get_current_user)]):
    return [order for order in ORDERS.values() if order.user_email == user.email]


@app.get("/api/orders/{order_id}", response_model=OrderResponse)
def get_order_by_id(order_id: str, user: Annotated[UserRecord, Depends(get_current_user)]):
    order = ORDERS.get(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.user_email != user.email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return order


def create_token_response(user: UserRecord) -> TokenResponse:
    token = create_access_token(user.email, user.role)
    return TokenResponse(access_token=token, token_type="bearer", role=user.role, email=user.email)


@app.post("/api/auth/login", response_model=TokenResponse)
@app.post("/api/v1/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest) -> TokenResponse:
    user = authenticate_user(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    return create_token_response(user)


@app.post("/api/auth/register", response_model=TokenResponse)
@app.post("/api/v1/auth/register", response_model=TokenResponse)
def register(payload: RegisterRequest) -> TokenResponse:
    user = register_user(payload.name, payload.email, payload.password)
    return create_token_response(user)


@app.get("/api/auth/me")
@app.get("/api/v1/auth/me")
def get_me(user: Annotated[UserRecord, Depends(get_current_user)]):
    return {"email": user.email, "role": user.role, "name": user.name}


@app.get("/api/v1/users/me")
def get_users_me(user: Annotated[UserRecord, Depends(get_current_user)]):
    return {"email": user.email, "role": user.role, "name": user.name}


@app.get("/api/admin/dashboard")
def admin_dashboard(user: Annotated[UserRecord, Depends(require_role("admin"))]):
    return {"message": "Admin access granted", "email": user.email}


@app.get("/api/branch-admin/dashboard")
def branch_dashboard(user: Annotated[UserRecord, Depends(require_role("branch-admin"))]):
    return {"message": "Branch admin access granted", "email": user.email}


@app.get("/api/customer/profile")
def customer_profile(user: Annotated[UserRecord, Depends(require_role("customer"))]):
    return {"message": "Customer access granted", "email": user.email}
