"""
Authentication module for the experimentation platform
"""
import os
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

load_dotenv()

# Load valid tokens from environment variables
_valid_tokens_str = os.getenv('VALID_TOKENS', 'test-token-123,demo-token-456')
VALID_TOKENS = set(_valid_tokens_str.split(','))

# Load token to client_id mapping from environment variables
_token_client_id_str = os.getenv('TOKEN_CLIENT_ID_MAP', 'test-token-123:1,demo-token-456:2')
token_client_id_map = {}
for mapping in _token_client_id_str.split(','):
    token, client_id = mapping.split(':')
    token_client_id_map[token.strip()] = int(client_id.strip())

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
