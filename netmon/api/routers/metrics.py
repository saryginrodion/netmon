from typing import Annotated
from fastapi import APIRouter, Depends

from netmon.api.dto.metrics import HistoryBody, LastBody
from netmon.entities.base_metric_entry import BaseMetricEntry
from netmon.metrics_repository.interface import MetricQuerier
from netmon.api.dependencies.ids import METRIC_QUERIER
from netmon.api.dependencies.registry import DI_REGISTRY

router = APIRouter()

metric_querier = DI_REGISTRY.get(METRIC_QUERIER)

@router.get("/")
async def index() -> str:
    return "Hello from metrics router!"

@router.post("/history", description="Query metrics in history")
async def history(
        body: HistoryBody,
        querier: Annotated[MetricQuerier, Depends(metric_querier)],
    ) -> list[BaseMetricEntry]:
    result = await querier.history_metrics(body.filters, body.interval)

    return list(result)

@router.post("/last", description="Query last metrics within interval")
async def last(
        body: LastBody,
        querier: Annotated[MetricQuerier, Depends(metric_querier)],
    ) -> list[BaseMetricEntry]:
    result = await querier.last_metrics(body.filters, body.interval)

    return list(result)
