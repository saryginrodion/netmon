from fastapi import APIRouter

from netmon.api.dto import (
    CollectorSettings,
    CollectorSettingsPatch,
    ServiceSettings,
)


router = APIRouter()


@router.get("", description="Получить настройки сервиса")
async def get_settings() -> ServiceSettings:
    # TODO: реализовать получение настроек сервиса
    return ServiceSettings(save_interval=0.0)


@router.get(
    "/collectors/{name}",
    description="Получить настройки определенного коллектора",
)
async def get_collector(name: str) -> CollectorSettings:
    # TODO: реализовать получение настроек коллектора по имени
    return CollectorSettings(
        name=name,
        type="activetcp",  # type: ignore[arg-type]
        is_active=False,
    )


@router.post(
    "/collectors",
    description="Создать новый коллектор",
    responses={409: {"description": "Коллектор с таким именем уже занят"}},
)
async def create_collector(body: CollectorSettings) -> CollectorSettings:
    # TODO: реализовать создание коллектора (409 если имя занято)
    return body


@router.patch(
    "/collectors/{name}",
    description="Обновить настройки коллектора",
    responses={409: {"description": "Коллектор с таким именем уже занят"}},
)
async def update_collector(
    name: str,
    body: CollectorSettingsPatch,
) -> CollectorSettings:
    # TODO: реализовать обновление настроек коллектора
    return CollectorSettings(
        name=name,
        type=body.type or "activetcp",  # type: ignore[arg-type]
        is_active=body.is_active if body.is_active is not None else False,
        destination_ip=body.destination_ip,
        send_delay=body.send_delay,
        loss_timeout=body.loss_timeout,
        payload_size=body.payload_size,
    )
