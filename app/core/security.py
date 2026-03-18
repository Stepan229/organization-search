from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from app.core.config import Settings, get_settings

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(
    api_key: str | None = Depends(_api_key_header),
    settings: Settings = Depends(get_settings),
) -> None:
    if not settings.api_key or not api_key or api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
