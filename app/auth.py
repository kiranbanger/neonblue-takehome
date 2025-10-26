"""
Authentication module for the experimentation platform
"""
from fastapi import HTTPException, Header, status
from typing import Optional

# Valid tokens (can be moved to environment variables or database)
VALID_TOKENS = {
    "test-token-123",
    "demo-token-456",
}


async def verify_token(authorization: Optional[str] = Header(None)) -> str:
    """
    Verify Bearer token from Authorization header
    
    Args:
        authorization: Authorization header value
        
    Returns:
        The token if valid
        
    Raises:
        HTTPException: If token is missing or invalid
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )

    # Extract token from "Bearer <token>" format
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )

    token = parts[1]
    if token not in VALID_TOKENS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    return token

