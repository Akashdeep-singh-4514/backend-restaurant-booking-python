# src/app.py
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from src.config import DatabaseConfig, logger
from src.controllers import api_router  # Import the API router
from src.middlewares import (  # Import the request logging middleware
    RequestLoggingMiddleware,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager for startup and shutdown events.
    """
    logger.info("Application starting up...")
    try:
        # --- Startup Events ---
        # 1. Initialize Database Engine (it's initialized on first call to get_engine)
        DatabaseConfig.get_engine()
        # 2. Run Database Migrations (uncomment when Alembic is fully set up)
        # await run_migrations()
        # 3. Start Background Scheduler (uncomment when APScheduler is configured)
        # scheduler_thread = Thread(target=run_scheduler, daemon=True)
        # scheduler_thread.start()

        logger.info("Application startup complete.")
        yield  # Application is ready to receive requests

    except Exception as e:
        logger.error(f"Error during application startup: {e}", exc_info=True)
        # Re-raise the exception to prevent the application from starting if startup fails
        raise
    finally:
        # --- Shutdown Events ---
        logger.info("Application shutting down...")
        # 1. Dispose of Database Connections
        await DatabaseConfig.disconnect_db()
        # 2. Shutdown Scheduler
        # if scheduler.running:
        #     scheduler.shutdown(wait=True)
        #     logger.info("Scheduler shut down.")
        logger.info("Application shutdown complete.")


# Initialize FastAPI application
app = FastAPI(
    title="Little Lemon API",
    description="Professional FastAPI project for Little Lemon restaurant.",
    version=os.getenv("__VERSION__", "0.1.0"),  # Can read from __init__.py or env
    lifespan=lifespan,
)

# CORS Middleware Configuration
# IMPORTANT: In production, narrow down `allow_origins` to your specific frontend domains.
# Do NOT use ["*"] in production for allow_origins unless you explicitly know the risks.
origins = os.getenv("CORS_ALLOW_ORIGINS", "http://localhost, http://127.0.0.1").split(
    ", "
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Request Logging Middleware
app.add_middleware(RequestLoggingMiddleware)


# Custom Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler for Pydantic validation errors to return consistent format.
    """
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")

    error_message = "; ".join(errors)
    logger.warning(f"Validation error on {request.url}: {error_message}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "message": f"{error_message}",
            "status": False,
            "data": None,
        },
    )


@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    """
    Custom handler for Pydantic validation errors from models.
    """
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")

    error_message = "; ".join(errors)
    logger.warning(f"Model validation error on {request.url}: {error_message}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "message": f"{error_message}",
            "status": False,
            "data": None,
        },
    )


# Health Check Endpoint
@app.get("/", tags=["Health Check"])
async def check_health():
    """
    Checks if the service is healthy and running.
    """
    logger.info("Health check endpoint accessed.")
    return {"message": "Service is healthy!", "version": app.version}


# Include API Router (we'll define this later)
app.include_router(api_router, prefix="/api")
