from http import HTTPStatus
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

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


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(Exception, exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore

