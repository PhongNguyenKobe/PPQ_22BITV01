# Role-Based Access Control (RBAC) Rules

## User Roles

### CUSTOMER (Default)
- Browse movies and showtimes
- Search and filter movies
- Create bookings
- View own bookings and payment history
- Cancel own bookings
- Update own profile
- View own e-tickets

**Endpoints:**
```
GET /api/v1/movies
GET /api/v1/movies/{id}
GET /api/v1/movies/{id}/showtimes
POST /api/v1/bookings
GET /api/v1/bookings
GET /api/v1/bookings/{id}
POST /api/v1/payments/process
GET /api/v1/payments/{id}
GET /api/v1/users/me
PUT /api/v1/users/me
```

### STAFF (Cinema Staff)
- All CUSTOMER permissions
- View branch showtimes
- Check seat availability in real-time
- Help customers complete bookings
- Cancel bookings with reason
- View branch revenue and occupancy
- Process refunds

**Additional Endpoints:**
```
GET /api/v1/admin/showtimes
GET /api/v1/admin/bookings (branch only)
PUT /api/v1/admin/bookings/{id}/cancel
GET /api/v1/admin/reports/occupancy
```

### BRANCH_ADMIN (Cinema Manager)
- All STAFF permissions
- Create and manage showtimes for their branch
- View all branch bookings and revenue
- Manage branch staff accounts
- Edit branch information
- Add/remove auditoriums
- Create promotions for the branch
- Generate branch reports

**Additional Endpoints:**
```
POST /api/v1/admin/showtimes
PUT /api/v1/admin/showtimes/{id}
DELETE /api/v1/admin/showtimes/{id}
GET /api/v1/admin/bookings
PUT /api/v1/admin/bookings/{id}/cancel
GET /api/v1/admin/reports/revenue (branch)
GET /api/v1/admin/reports/occupancy (branch)
PUT /api/v1/admin/branches/{id}
```

### SUPER_ADMIN (System Administrator)
- All permissions
- Manage all users (create, update, delete, assign roles)
- Create, update, delete movies
- Create, update, delete branches
- View system-wide analytics
- Manage payment methods
- Process refunds
- Generate system reports
- System configuration

**Additional Endpoints:**
```
GET /api/v1/admin/users
PUT /api/v1/admin/users/{id}/role
DELETE /api/v1/admin/users/{id}
POST /api/v1/admin/movies
PUT /api/v1/admin/movies/{id}
DELETE /api/v1/admin/movies/{id}
POST /api/v1/admin/branches
DELETE /api/v1/admin/branches/{id}
GET /api/v1/admin/payments
POST /api/v1/admin/payments/{id}/refund
GET /api/v1/admin/reports/*
```

## Access Control Implementation

### Method 1: Dependency Injection (FastAPI)
```python
from app.core.permissions import require_admin, require_branch_admin

@router.post("/admin/movies")
async def create_movie(
    payload: dict,
    current_user: User = Depends(require_admin)
):
    # Only SUPER_ADMIN can access
    pass
```

### Method 2: Manual Check
```python
async def create_showtime(
    current_user: User = Depends(get_current_user)
):
    # Check role
    if not any(r.code in ["BRANCH_ADMIN", "SUPER_ADMIN"] for r in current_user.roles):
        raise HTTPException(status_code=403, detail="Permission denied")
```

### Method 3: Decorator Pattern (Future)
```python
@require_role("BRANCH_ADMIN")
async def create_showtime(current_user: User):
    pass
```

## Database Implementation

### roles table
```
id | code | name | description
1  | CUSTOMER | Khách hàng | Regular user
2  | STAFF | Nhân viên | Cinema staff
3  | BRANCH_ADMIN | Quản lý chi nhánh | Branch manager
4  | SUPER_ADMIN | Quản trị viên | System admin
```

### user_roles table (M2M)
```
user_id | role_id | branch_id | assigned_at
UUID    | INT     | UUID      | TIMESTAMP
```

## Frontend Implementation (Nuxt 3)

### Composable useAuth
```typescript
const { currentUser } = useAuth()

const canEditMovie = computed(() => 
  currentUser.value?.role === 'admin'
)

const canViewBranchBookings = computed(() => 
  ['admin', 'branch-admin', 'staff'].includes(currentUser.value?.role)
)
```

### Route Protection
```typescript
// middleware/admin.ts
defineRouteMiddleware((to, from) => {
  const userStore = useUserStore()
  if (to.path.startsWith('/admin') && userStore.currentUser?.role !== 'admin') {
    return navigateTo('/products')
  }
})
```

## Permission Matrix

```
Feature                 | Customer | Staff | Branch Admin | Super Admin
------------------------+----------+-------+-------------+-------------
Browse Movies           | ✓        | ✓     | ✓           | ✓
Make Booking            | ✓        | ✓     | ✓           | ✓
View Own Bookings       | ✓        | ✓     | ✓           | ✓
Cancel Own Booking      | ✓        | ✓     | ✓           | ✓
View Branch Bookings    | ✗        | ✓     | ✓           | ✓
Cancel Any Booking      | ✗        | ✓     | ✓           | ✓
Create Showtime         | ✗        | ✗     | ✓           | ✓
Edit Showtime           | ✗        | ✗     | ✓           | ✓
Delete Showtime         | ✗        | ✗     | ✓           | ✓
Create Movie            | ✗        | ✗     | ✗           | ✓
Edit Movie              | ✗        | ✗     | ✗           | ✓
Delete Movie            | ✗        | ✗     | ✗           | ✓
Manage Users            | ✗        | ✗     | ✗           | ✓
Assign Roles            | ✗        | ✗     | ✗           | ✓
View Reports            | ✗        | ✓     | ✓           | ✓
Refund Payments         | ✗        | ✗     | ✓           | ✓
Manage Branches         | ✗        | ✗     | ✗           | ✓
```

## Security Best Practices

1. **Always validate role on backend** - Never trust frontend role
2. **Use JWT tokens with role claims** - Include roles in JWT payload
3. **Implement rate limiting** - Prevent brute force attacks
4. **Audit logging** - Log all admin actions
5. **Encryption** - Use HTTPS for all requests
6. **Session timeout** - Auto-logout after inactivity
7. **Multi-factor authentication** - For admin accounts
8. **Branch isolation** - Staff can only access their branch data
