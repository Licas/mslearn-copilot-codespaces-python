"""Rate limiting middleware for the FastAPI app."""

from collections import defaultdict, deque
from math import ceil
from threading import Lock
from time import monotonic
from typing import Deque, Iterable

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class SlidingWindowRateLimiter:
    """Track request timestamps per client in a sliding window."""

    def __init__(self, max_requests: int = 10, window_seconds: int = 60) -> None:
        if max_requests <= 0:
            raise ValueError("max_requests must be greater than zero.")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be greater than zero.")

        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, Deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, client_key: str) -> tuple[bool, int]:
        """Record a request and return whether it is allowed."""
        now = monotonic()
        cutoff = now - self.window_seconds

        with self._lock:
            bucket = self._requests[client_key]
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()

            if len(bucket) >= self.max_requests:
                retry_after = max(1, ceil(self.window_seconds - (now - bucket[0])))
                return False, retry_after

            bucket.append(now)
            return True, 0

    def reset(self) -> None:
        """Clear all tracked request timestamps."""
        with self._lock:
            self._requests.clear()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Return HTTP 429 when a client exceeds the configured request window."""

    def __init__(
        self,
        app,
        limiter: SlidingWindowRateLimiter,
        excluded_paths: Iterable[str] | None = None,
    ) -> None:
        super().__init__(app)
        self.limiter = limiter
        self.excluded_paths = set(excluded_paths or ())

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path in self.excluded_paths or path.startswith("/ui"):
            return await call_next(request)

        client_host = request.client.host if request.client and request.client.host else "anonymous"
        allowed, retry_after = self.limiter.check(client_host)
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again later."},
                headers={"Retry-After": str(retry_after)},
            )

        return await call_next(request)
