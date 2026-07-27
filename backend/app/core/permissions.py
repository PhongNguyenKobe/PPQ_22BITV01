from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User


class PermissionDenied(HTTPException):
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to require SUPER_ADMIN role
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # Check if user has SUPER_ADMIN role
    has_admin_role = any(role.code == "SUPER_ADMIN" for role in current_user.roles)
    
    if not has_admin_role:
        raise PermissionDenied("Only super admins can access this resource")
    
    return current_user


async def require_branch_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to require BRANCH_ADMIN or SUPER_ADMIN role
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # Check if user has BRANCH_ADMIN or SUPER_ADMIN role
    has_required_role = any(
        role.code in ["BRANCH_ADMIN", "SUPER_ADMIN"] 
        for role in current_user.roles
    )
    
    if not has_required_role:
        raise PermissionDenied("Only branch admins can access this resource")
    
    return current_user


async def require_staff(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to require STAFF, BRANCH_ADMIN or SUPER_ADMIN role
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # Check if user has STAFF, BRANCH_ADMIN or SUPER_ADMIN role
    has_required_role = any(
        role.code in ["STAFF", "BRANCH_ADMIN", "SUPER_ADMIN"] 
        for role in current_user.roles
    )
    
    if not has_required_role:
        raise PermissionDenied("Only staff members can access this resource")
    
    return current_user


async def require_customer(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to require CUSTOMER role (or any authenticated user)
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    return current_user
