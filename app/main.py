import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.api.routers import activities, buildings, organizations, search
from app.core.exceptions import AppException, BadRequestError, ConflictError, NotFoundError


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Organizations API",
        description="REST API для справочника организаций, зданий и видов деятельности. Все эндпоинты требуют заголовок `X-API-Key`.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url=None,
    )

    @app.exception_handler(NotFoundError)
    def handle_not_found(_request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": exc.message, "code": exc.code or "NOT_FOUND"},
        )

    @app.exception_handler(BadRequestError)
    def handle_bad_request(_request: Request, exc: BadRequestError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.message, "code": exc.code or "BAD_REQUEST"},
        )

    @app.exception_handler(ConflictError)
    def handle_conflict(_request: Request, exc: ConflictError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": exc.message, "code": exc.code or "CONFLICT"},
        )

    @app.exception_handler(AppException)
    def handle_app_exception(_request: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.message, "code": exc.code or "ERROR"},
        )

    @app.exception_handler(Exception)
    def handle_unhandled(_request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )

    app.include_router(organizations.router, prefix="/api/v1")
    app.include_router(buildings.router, prefix="/api/v1")
    app.include_router(activities.router, prefix="/api/v1")
    app.include_router(search.router, prefix="/api/v1")

    return app


app = create_app()

