from typing import Annotated
from fastapi import APIRouter, Depends
from netmon.api.dependencies.ids import COLLECTORS_MANAGER
from netmon.api.dependencies.registry import DI_REGISTRY
from netmon.api.dto.settings import SetCollectorSettingsBody
from netmon.collectors.errors import CollectorNotFound
from netmon.collectors.info import CollectorInfo
from netmon.collectors.manager import CollectorsManager

router = APIRouter()

collectors_manager = DI_REGISTRY.get(COLLECTORS_MANAGER)


@router.get("/")
async def index() -> str:
    return "Hello from Settings router!"


@router.get("/collectors/{collector_name}")
async def collector_info(
    collector_name: str,
    manager: Annotated[CollectorsManager, Depends(collectors_manager)],
) -> CollectorInfo:
    collectors = await manager.collectors()

    for collector in collectors:
        if collector.name == collector_name:
            return collector

    raise CollectorNotFound()


@router.post("/collectors/{collector_name}")
async def set_collector_settings(
    collector_name: str,
    body: SetCollectorSettingsBody,
    manager: Annotated[CollectorsManager, Depends(collectors_manager)],
) -> None:
    await manager.set_collector_active(collector_name, body.is_active)


@router.get("/collectors")
async def all_collectors_info(
    manager: Annotated[CollectorsManager, Depends(collectors_manager)],
) -> list[CollectorInfo]:
    return await manager.collectors()
