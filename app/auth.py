"""
Authentication module for the experimentation platform
"""
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Valid tokens and client_ids (can be moved to environment variables or database)
VALID_TOKENS = {
    "test-token-123",
    "demo-token-456",
}

token_client_id_map = {
    "test-token-123" : 1,
    "demo-token-456" : 2
}

# Create security scheme
security = HTTPBearer()


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """
    Verify Bearer token from Authorization header

    Args:
        credentials: HTTP credentials from Authorization header (extracted by HTTPBearer)

    Returns:
        The client_id if valid

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

    return token_client_id_map[token]
