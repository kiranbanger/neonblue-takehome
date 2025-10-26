"""
Authentication module for the experimentation platform
"""
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Valid tokens (can be moved to environment variables or database)
VALID_TOKENS = {
    "test-token-123",
    "demo-token-456",
}

# Create security scheme
security = HTTPBearer()


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Verify Bearer token from Authorization header

    Args:
        credentials: HTTP credentials from Authorization header (extracted by HTTPBearer)

    Returns:
        The token if valid

    Raises:
        HTTPException: If token is invalid
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials"
        )

    token = credentials.credentials

    if token not in VALID_TOKENS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    return token

