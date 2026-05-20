from typing import Annotated

from fastapi import APIRouter, Depends

from netmon.api.dto import (
    ExportQuery,
    HistoryQuery,
    MetricEntry,
    RealtimeQuery,
)


router = APIRouter()


@router.get("/history", description="Поиск метрик в истории")
async def history(
    query: Annotated[HistoryQuery, Depends()],
) -> list[MetricEntry]:
    # TODO: реализовать получение метрик из репозитория
    return []


@router.get("/realtime", description="Поиск метрик в реальном времени")
async def realtime(
    query: Annotated[RealtimeQuery, Depends()],
) -> list[MetricEntry]:
    # TODO: реализовать получение realtime-метрик
    return []


@router.get("/export", description="Экспорт метрик")
async def export(
    query: Annotated[ExportQuery, Depends()],
) -> list[MetricEntry]:
    # TODO: реализовать экспорт метрик в csv/json
    return []
