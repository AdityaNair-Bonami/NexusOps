from fastapi import Depends, HTTPException, status
from .security import get_current_user_payload
from typing import List

class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, token_data: dict = Depends(get_current_user_payload)):
        user_role = token_data.get("role")
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access Denied: Required roles {self.allowed_roles}. Your role: {user_role}"
            )
        return True