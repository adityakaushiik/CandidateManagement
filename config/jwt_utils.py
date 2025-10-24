from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, Any, Optional, List

import jwt as pyjwt
from fastapi import HTTPException
from starlette import status

from config.config import get_settings
from utils.common_constants import UserRoles


def create_access_token(data: dict, expires_delta_in_days: Optional[float] = 2) -> str:
    settings = get_settings()
    to_encode = data.copy()

    # Set the Expiry Date
    expire = datetime.now() + timedelta(days=expires_delta_in_days)
    to_encode.update({"exp": expire})

    return pyjwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )


def verify_jwt(token: str) -> Dict[str, Any]:
    """
    Verify JWT token and return decoded payload
    """
    settings = get_settings()

    try:
        payload = pyjwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except pyjwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_auth(roles: Optional[List[UserRoles]] = None):
    """Decorator to require authentication and optionally check roles"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request object from function arguments
            request = kwargs.get("request")

            print(request.headers)

            if not request:
                request = next((arg for arg in args if isinstance(arg, Request)), None)

            if not request:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Request object not found",
                )

            # Check for Authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authorization header missing",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Validate Bearer token format
            try:
                scheme, token = auth_header.split()
                if scheme.lower() != "bearer":
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid authentication scheme",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authorization header format",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Verify JWT token and get payload
            payload = verify_jwt(token)

            # Check roles if specified
            if roles:
                payload_roles = payload.get("roles", [])
                # Convert payload roles to ints
                try:
                    payload_role_ids = {int(r) for r in payload_roles}
                except Exception:
                    payload_role_ids = set()
                required_role_ids = {role.value for role in roles}
                if payload_role_ids.isdisjoint(required_role_ids):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Insufficient permissions",
                    )

            # Add user info to request state
            request.state.user = payload

            return await func(*args, **kwargs)

        return wrapper

    return decorator
