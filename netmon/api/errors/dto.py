from pydantic import BaseModel
from enum import StrEnum


class ErrorCode(StrEnum):
    COLLECTOR_EXISTS = "COLLECTOR_EXISTS"
    INVALID_INTERVAL = "INVALID_INTERVAL"
    UNKNOWN = "UNKNOWN"


class APIError(BaseModel):
    code: ErrorCode
    message: str
