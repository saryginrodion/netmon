from .errors.handlers import register_exception_handlers
from .routers import metrics, settings
from fastapi import FastAPI


def initialize_app(app: FastAPI) -> FastAPI:
    app.include_router(metrics.router, prefix="/api/metrics")
    app.include_router(settings.router, prefix="/api/settings")

    register_exception_handlers(app)

    return app
