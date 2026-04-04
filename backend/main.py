"""
SwasthaLink Backend API
FastAPI application — slim entrypoint that mounts domain routers.
"""

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load environment variables before anything else
load_dotenv()

from core.config import FRONTEND_URL, ALLOWED_ORIGINS  # noqa: E402
from routes import all_routers  # noqa: E402
from services.gemini_service import check_gemini_health  # noqa: E402
from services.twilio_service import check_twilio_health  # noqa: E402
from services.s3_service import check_s3_health  # noqa: E402
from db.supabase_service import check_supabase_health  # noqa: E402

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App creation
# ---------------------------------------------------------------------------
app = FastAPI(
    title="SwasthaLink API",
    description="Medical discharge summary simplification with bilingual output and WhatsApp delivery",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all domain routers
for router in all_routers:
    app.include_router(router)


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    logger.exception(exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if os.getenv("DEBUG") == "true" else "An unexpected error occurred",
        },
    )


# ---------------------------------------------------------------------------
# Lifecycle events
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    logger.info("=" * 50)
    logger.info("SwasthaLink API Starting...")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Frontend URL: {FRONTEND_URL}")
    logger.info("=" * 50)
    logger.info(f"Gemini API: {check_gemini_health().get('status')}")
    logger.info(f"Twilio API: {check_twilio_health().get('status')}")
    logger.info(f"Supabase:   {check_supabase_health().get('status')}")
    logger.info(f"AWS S3:     {check_s3_health().get('status')}")
    logger.info("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("SwasthaLink API shutting down...")


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
        log_level="info",
    )
