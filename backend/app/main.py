"""
Riverdale Connect - Main Application Entry Point
FastAPI backend for pre-handover project governance
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.rate_limiter import RateLimiterMiddleware

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Pre-handover Project Governance Application",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# NOTE: Middleware is applied in reverse registration order (last added = outermost).
# Desired order (outermost → innermost):
#   Rate limiter → Logging → Security headers → GZip → CORS → Route handler

# CORS must be innermost so it runs on every actual response (including error responses)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compress responses before security headers are injected
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add security headers to every response
app.add_middleware(SecurityHeadersMiddleware)

# Log every request/response with timing
app.add_middleware(LoggingMiddleware)

# Rate-limit per IP (outermost – rejects early before any other processing)
app.add_middleware(RateLimiterMiddleware)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint - Health check"""
    return {
        "message": "Riverdale Connect API",
        "version": settings.APP_VERSION,
        "status": "operational",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
