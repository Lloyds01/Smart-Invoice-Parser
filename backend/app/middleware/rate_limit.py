"""ASGI middleware implementing in-memory fixed-window IP rate limiting."""

from __future__ import annotations

import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class FixedWindowRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 60):
        """Initialize fixed-window per-IP limiter with requests-per-minute threshold."""
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.hits: dict[str, deque[float]] = defaultdict(deque)

    def _client_ip(self, request) -> str:
        """Resolve client IP from X-Forwarded-For (first hop) or socket address."""
        # Trust first X-Forwarded-For hop when present. In production,
        # restrict trusted proxy sources to avoid spoofing.
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client and request.client.host:
            return request.client.host
        return "unknown"

    async def dispatch(self, request, call_next):
        """Apply fixed-window rate checks and return HTTP 429 when limit is exceeded."""
        ip = self._client_ip(request)
        now = time.time()
        window_start = now - 60

        bucket = self.hits[ip]
        while bucket and bucket[0] < window_start:
            bucket.popleft()

        if len(bucket) >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again later."},
            )

        bucket.append(now)
        return await call_next(request)
