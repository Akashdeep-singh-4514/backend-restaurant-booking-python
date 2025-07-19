# src/middlewares/request_logging_middleware.py
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from src.config import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log incoming HTTP requests and their responses.
    Logs method, URL, status code, and response time.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = logger  # Use the pre-configured logger

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        request_id = request.headers.get(
            "X-Request-ID"
        )  # Optional: If clients send a request ID

        log_extra = {
            "http.method": request.method,
            "http.url": str(request.url),
            "http.client_host": request.client.host if request.client else "N/A",
            "request_id": request_id,
        }

        # Log request details
        self.logger.info(
            f"Incoming Request: {request.method} {request.url}", extra=log_extra
        )

        try:
            response = await call_next(request)
        except Exception as e:
            # Handle exceptions that occur during request processing
            process_time = time.time() - start_time
            log_extra["http.status_code"] = 500  # Assume 500 for unhandled exceptions
            log_extra["response_time_ms"] = round(process_time * 1000)
            self.logger.error(
                f"Request processing failed: {request.method} {request.url} | Error: {e}",
                extra=log_extra,
                exc_info=True,  # exc_info=True logs traceback
            )
            # Re-raise the exception or return an error response
            raise  # Re-raise to let FastAPI's default exception handler or other handlers take over

        process_time = time.time() - start_time
        response_time_ms = round(process_time * 1000)

        # Log response details
        log_extra["http.status_code"] = response.status_code
        log_extra["response_time_ms"] = response_time_ms

        log_level = self.logger.info  # Default level

        if response.status_code >= 500:
            log_level = self.logger.error
        elif response.status_code >= 400:
            log_level = self.logger.warning
        elif response.status_code >= 300:
            log_level = self.logger.info  # Redirects
        elif response.status_code >= 200:
            log_level = self.logger.info  # Success

        log_level(
            f"Outgoing Response: {request.method} {request.url} | Status: {response.status_code} | Time: {response_time_ms}ms",
            extra=log_extra,
        )

        return response


# --- IMPORTANT NOTE ON LOGGING REQUEST/RESPONSE BODIES ---
# Logging request and response bodies can be tricky and resource-intensive,
# especially for large payloads. It can also expose sensitive data.
# If you need to log bodies, consider:
# 1. Only doing it for specific endpoints or under certain debug conditions.
# 2. Redacting sensitive information.
# 3. Reading the request body only once (FastAPI/Starlette handles this carefully,
#    as request.body() consumes the stream). You might need to use a Request object
#    that pre-reads the body, or re-wrap the body stream.
# For responses, you might need to read the response stream before returning it,
# then recreate the response. This is more complex.
# For now, we'll stick to logging metadata.
