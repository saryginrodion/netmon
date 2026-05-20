from http import HTTPStatus
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from netmon.collectors.errors import CollectorNotFound

from .dto import APIError, ErrorCode


async def exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        APIError(
            message=str(exc),
            code=ErrorCode.UNKNOWN,
        ).model_dump(),
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
    )


async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        APIError(
            message=exc.detail,
            code=ErrorCode.UNKNOWN,
        ).model_dump(),
        status_code=exc.status_code,
    )

async def collector_not_found_exists_handler(_request: Request, exc: CollectorNotFound) -> JSONResponse:
    return JSONResponse(
        APIError(
            message="Collector not found",
            code=ErrorCode.COLLECTOR_NOT_FOUND,
        ).model_dump(),
        status_code=HTTPStatus.NOT_FOUND,
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(Exception, exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore
    app.add_exception_handler(CollectorNotFound, collector_not_found_exists_handler)  # type: ignore

