from backend.config import get_settings, load_environment

# Load .env before anything reads configuration (codebase-audit.md B1).
load_environment()

import logging  # noqa: E402

from fastapi import FastAPI, Request  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import JSONResponse  # noqa: E402
from slowapi.errors import RateLimitExceeded  # noqa: E402

from backend.routers import scan  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("chimerashield")

settings = get_settings()
if not settings.anthropic_api_key:
    logger.error("ANTHROPIC_API_KEY is not set. /api/scan/email will return 503 until it is configured.")

app = FastAPI(
    title="ChimeraShield API",
    description="AI-powered cybersecurity analysis backend",
    version="0.1.0",
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
    openapi_url=None if settings.is_production else "/openapi.json",
)

app.state.limiter = scan.limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    """Reject oversized API bodies before they are read or parsed.

    The precise 50 KB limit on the email body is enforced in the scan route; this
    coarse cap (4x, to allow for JSON escaping) stops multi-megabyte bodies early.
    """
    if request.url.path.startswith("/api/"):
        max_bytes = get_settings().max_email_bytes * 4
        length = request.headers.get("content-length")
        if length is not None and (not length.isdigit() or int(length) > max_bytes):
            logger.info("request_rejected reason=too_large path=%s", request.url.path)
            return JSONResponse(status_code=413, content={"detail": "Request is too large."})
    return await call_next(request)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    logger.warning("scan_rejected reason=rate_limited path=%s ip_hash=%s", request.url.path, scan._ip_hash(request))
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many scans in a short time. Please wait a minute and try again."},
    )


app.include_router(scan.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "ChimeraShield API", "version": "0.1.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}
