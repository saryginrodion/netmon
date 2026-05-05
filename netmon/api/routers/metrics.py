from typing import Annotated
from fastapi import APIRouter, Depends

from netmon.api.dependencies.ids import METRIC_QUERIER
from netmon.api.dependencies.registry import DI_REGISTRY

router = APIRouter()

metric_querier = DI_REGISTRY.get(METRIC_QUERIER)

@router.get("/")
async def index() -> str:
    return "Hello from metrics router!"

@router.get("/dependency")
async def dependency(querier: Annotated[str, Depends(metric_querier)]) -> str:
    return querier
