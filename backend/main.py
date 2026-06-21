"""
ASTRA - AI-Powered Strategic Traffic Response & Analysis Platform
FastAPI Backend Entry Point
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.database import init_db
from backend.middleware.rate_limit import RateLimitMiddleware

# Import ALL models here so SQLAlchemy mapper can resolve all relationships
# before init_db() calls create_all()
from backend.models.user import User, UserRole  # noqa: F401
from backend.models.event import Event  # noqa: F401
from backend.models.prediction import Prediction  # noqa: F401
from backend.models.recommendation import Recommendation  # noqa: F401
from backend.models.road import Road, AuditLog  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    # Startup
    print("=" * 60)
    print(f"  ASTRA v{settings.APP_VERSION} Starting...")
    print(f"  Database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'configured'}")
    print("=" * 60)

    # Initialize database tables
    init_db()
    print("  ✓ Database tables initialized")

    # Load ML models (deferred - will be loaded on first prediction)
    print("  ✓ ML models will load on first prediction")
    print("  ✓ ASTRA is ready!")
    print("=" * 60)

    yield

    # Shutdown
    print("ASTRA shutting down...")


# Create FastAPI app
app = FastAPI(
    title="ASTRA API",
    description=(
        "AI-Powered Strategic Traffic Response & Analysis Platform\n\n"
        "Predict traffic congestion, recommend deployment strategies, "
        "rank affected locations, and explain every recommendation.\n\n"
        "Built for Bengaluru Traffic Police."
    ),
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ===== Middleware =====
# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.add_middleware(RateLimitMiddleware)

# Note: Audit middleware is added after routes to avoid import issues
# from backend.middleware.audit import AuditMiddleware
# app.add_middleware(AuditMiddleware)


# ===== Routes =====
from backend.routers import auth
app.include_router(auth.router)

# Import remaining routers if they exist
try:
    from backend.routers import predict
    app.include_router(predict.router)
except ImportError:
    print("  ⚠ Prediction routes not yet available")

try:
    from backend.routers import recommend
    app.include_router(recommend.router)
except ImportError:
    print("  ⚠ Recommendation routes not yet available")

try:
    from backend.routers import events
    app.include_router(events.router)
except ImportError:
    print("  ⚠ Event routes not yet available")

try:
    from backend.routers import dashboard
    app.include_router(dashboard.router)
except ImportError:
    print("  ⚠ Dashboard routes not yet available")

try:
    from backend.routers import explain
    app.include_router(explain.router)
except ImportError:
    print("  ⚠ Explain routes not yet available")

try:
    from backend.routers import history
    app.include_router(history.router)
except ImportError:
    print("  ⚠ History routes not yet available")

try:
    from backend.routers import chat
    app.include_router(chat.router)
except ImportError:
    print("  ⚠ Chat routes not yet available")


# ===== Health Check =====
@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/", tags=["System"])
async def root():
    """Root endpoint."""
    return {
        "app": "ASTRA - AI-Powered Strategic Traffic Response & Analysis Platform",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }
