"""ASGI middleware that enforces request payload size limits."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class PayloadLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_bytes: int = 200_000):
        """Initialize request body size guard with a maximum number of bytes."""
        super().__init__(app)
        self.max_bytes = max_bytes

    async def dispatch(self, request, call_next):
        """Reject requests larger than `max_bytes` with HTTP 413."""
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > self.max_bytes:
                    return JSONResponse(
                        status_code=413,
                        content={
                            "detail": f"Payload too large. Maximum allowed is {self.max_bytes} bytes."
                        },
                    )
            except ValueError:
                pass

        body = await request.body()
        if len(body) > self.max_bytes:
            return JSONResponse(
                status_code=413,
                content={"detail": f"Payload too large. Maximum allowed is {self.max_bytes} bytes."},
            )

        request._body = body
        return await call_next(request)
