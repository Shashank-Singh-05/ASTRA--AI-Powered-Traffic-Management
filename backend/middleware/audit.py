"""ASTRA Audit Logging Middleware."""

import json
from datetime import datetime, timezone
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from backend.database import SessionLocal
from backend.models.road import AuditLog


class AuditMiddleware(BaseHTTPMiddleware):
    """Log all state-changing API requests for audit compliance."""

    # Methods that modify state
    AUDITABLE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

    # Paths to exclude from audit (e.g., health checks)
    EXCLUDE_PATHS = {"/health", "/api/dashboard/kpis", "/docs", "/openapi.json"}

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Only audit state-changing requests
        if request.method in self.AUDITABLE_METHODS:
            path = request.url.path
            if path not in self.EXCLUDE_PATHS:
                try:
                    await self._log_action(request, response)
                except Exception:
                    pass  # Don't break the request if audit logging fails

        return response

    async def _log_action(self, request: Request, response):
        """Write audit log entry to database."""
        # Extract user info from request state if available
        username = getattr(request.state, "username", None) if hasattr(request, "state") else None

        db = SessionLocal()
        try:
            log = AuditLog(
                username=username,
                action=f"{request.method} {request.url.path}",
                resource_type=self._extract_resource_type(request.url.path),
                details={"status_code": response.status_code},
                ip_address=request.client.host if request.client else None,
            )
            db.add(log)
            db.commit()
        finally:
            db.close()

    def _extract_resource_type(self, path: str) -> str:
        """Extract resource type from URL path."""
        parts = path.strip("/").split("/")
        if len(parts) >= 2:
            return parts[1]  # e.g., "events", "predict", "recommend"
        return "unknown"
