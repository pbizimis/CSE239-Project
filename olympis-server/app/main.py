from contextlib import asynccontextmanager
from dataclasses import dataclass

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from rq import Queue

from app.campaigns.router import router as campaigns_router
from app.config import (
    API_DEBUG,
    API_ROOT_PATH,
    API_TITLE,
    API_VERSION,
    CORS_ALLOW_CREDENTIALS,
    CORS_ALLOW_HEADERS,
    CORS_ALLOW_METHODS,
    CORS_EXPOSE_HEADERS,
    CORS_ORIGINS,
)
from app.db.cache import Cache, init_cache
from app.db.database import Database, init_database
from app.db.queue import init_queue
from app.exceptions import BaseError
from app.logger import get_logger
from app.stores.router import router as stores_router
from app.user.router import router as user_router
from app.jobs.router import router as jobs_router

logger = get_logger(__name__)


@dataclass(slots=True)
class AppState:
    cache: Cache
    database: Database
    queue: Queue
    # storage: Any


async def init_app_state() -> AppState:
    logger.info("Initializing application state")
    try:
        cache = init_cache()
        logger.info("Cache initialized successfully")

        database = init_database()
        logger.info("Database initialized successfully")

        queue = init_queue()
        logger.info("Queue initialized successfully")

        # storage = await init_storage()
        return AppState(cache=cache, database=database, queue=queue)
    except Exception as e:
        logger.exception("Failed to initialize application state")
        raise


async def on_startup(app: FastAPI):
    logger.info("Starting application startup sequence")
    try:
        app_state: AppState = await init_app_state()
        app.state.app_state = app_state
        logger.info("Application startup completed successfully")
    except Exception as e:
        logger.exception("Application startup failed")
        raise


async def on_shutdown(app: FastAPI):
    logger.info("Starting application shutdown sequence")
    try:
        # Add any cleanup logic here
        logger.info("Application shutdown completed successfully")
    except Exception as e:
        logger.exception("Error during application shutdown")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application lifespan context manager started")
    await on_startup(app)
    yield
    await on_shutdown(app)


app = FastAPI(
    title=API_TITLE,
    debug=API_DEBUG,
    version=API_VERSION,
    root_path=API_ROOT_PATH,
    lifespan=lifespan,
)

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
    expose_headers=CORS_EXPOSE_HEADERS,
)

app.include_router(user_router, prefix="/user")
app.include_router(stores_router, prefix="/stores")

logger.info(f"Application initialized with title: {API_TITLE}, version: {API_VERSION}")


@app.exception_handler(BaseError)
async def app_exception_handler(request: Request, exc: BaseError):
    logger.exception(f"Application error occurred: {exc.code} - {exc.message}")
    body = {"detail": exc.message, "code": exc.code}
    return JSONResponse(status_code=exc.status_code, content=body)


@app.get("/healthcheck")
async def healthcheck() -> bool:
    logger.info("Health check requested")
    return True
