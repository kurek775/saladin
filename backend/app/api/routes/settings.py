"""Settings API — key validation endpoint for BYOK."""

import logging

from fastapi import APIRouter
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/settings", tags=["settings"])


class ValidateKeyRequest(BaseModel):
    provider: str
    key: str


class ValidateKeyResponse(BaseModel):
    valid: bool
    error: str = ""


@router.post("/validate-key", response_model=ValidateKeyResponse)
async def validate_key(data: ValidateKeyRequest):
    """Validate an API key by making a minimal API call (list models)."""
    provider = data.provider.lower().strip()
    key = data.key.strip()

    if not key:
        return ValidateKeyResponse(valid=False, error="Key is empty")

    try:
        if provider == "openai":
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {key}"},
                    timeout=10,
                )
                if resp.status_code == 200:
                    return ValidateKeyResponse(valid=True)
                return ValidateKeyResponse(valid=False, error=f"HTTP {resp.status_code}")

        elif provider == "anthropic":
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://api.anthropic.com/v1/models",
                    headers={
                        "x-api-key": key,
                        "anthropic-version": "2023-06-01",
                    },
                    timeout=10,
                )
                if resp.status_code == 200:
                    return ValidateKeyResponse(valid=True)
                return ValidateKeyResponse(valid=False, error=f"HTTP {resp.status_code}")

        elif provider == "google":
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"https://generativelanguage.googleapis.com/v1/models?key={key}",
                    timeout=10,
                )
                if resp.status_code == 200:
                    return ValidateKeyResponse(valid=True)
                return ValidateKeyResponse(valid=False, error=f"HTTP {resp.status_code}")

        else:
            return ValidateKeyResponse(valid=False, error=f"Unknown provider: {provider}")

    except Exception as e:
        logger.warning("Key validation error for %s: %s", provider, type(e).__name__)
        return ValidateKeyResponse(valid=False, error=str(e))


class SandboxModeResponse(BaseModel):
    mode: str  # "local" | "docker"


class SandboxModeUpdate(BaseModel):
    mode: str


@router.get("/sandbox-mode", response_model=SandboxModeResponse)
async def get_sandbox_mode():
    from app.config import settings
    return SandboxModeResponse(mode=settings.SANDBOX_MODE)


@router.put("/sandbox-mode", response_model=SandboxModeResponse)
async def set_sandbox_mode(data: SandboxModeUpdate):
    from app.config import settings
    if data.mode not in ("local", "docker"):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Mode must be 'local' or 'docker'")
    settings.SANDBOX_MODE = data.mode
    return SandboxModeResponse(mode=settings.SANDBOX_MODE)
