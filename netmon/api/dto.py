from enum import StrEnum
from typing import Literal, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Общие схемы
# ---------------------------------------------------------------------------


class ErrorCodeEnum(StrEnum):
    """Коды ошибок API."""

    COLLECTOR_EXISTS = "COLLECTOR_EXISTS"
    INCORRECT_INTERVAL = "INCORRECT_INTERVAL"


class Error(BaseModel):
    """Ошибка API."""

    code: ErrorCodeEnum
    message: str


# ---------------------------------------------------------------------------
# Метрики
# ---------------------------------------------------------------------------


MetricType = Literal[
    "rtt",
    "jitter",
    "latency_from",
    "latency_to",
    "bytes_sent",
    "bytes_received",
    "packet_loss",
]


class Filter(BaseModel):
    """Схема для фильтров метрик."""

    collectors: list[str] = Field(
        default_factory=list,
        description="Имена коллекторов. Пустой список — игнорировать фильтр",
    )
    destination_ips: list[str] = Field(
        default_factory=list,
        description="IP адреса целей теста. Пустой список — игнорировать фильтр",
    )
    metric_types: list[MetricType] = Field(
        default_factory=list,
        description="Типы метрик. Пустой список — игнорировать фильтр",
    )


class MetricValue(BaseModel):
    """Аккумулированное значение метрики."""

    accumulated: float
    min: float
    max: float
    aggregated_count: int


class MetricEntry(BaseModel):
    """Метрика в какой-то момент времени."""

    origin: str
    timestamp: float
    rtt: MetricValue
    latency_from: MetricValue
    latency_to: MetricValue
    packet_loss: Optional[float] = None
    bytes_sent: Optional[int] = None
    bytes_received: Optional[int] = None


# ---------------------------------------------------------------------------
# Query-параметры эндпоинтов метрик
# ---------------------------------------------------------------------------


class HistoryQuery(Filter):
    """Параметры запроса GET /metrics/history."""

    from_timestamp: float
    to_timestamp: float


class RealtimeQuery(Filter):
    """Параметры запроса GET /metrics/realtime.

    Можно указать либо `interval`, либо пару `from_timestamp` / `to_timestamp`.
    """

    interval: Optional[float] = None
    from_timestamp: Optional[float] = None
    to_timestamp: Optional[float] = None


class ExportTypeEnum(StrEnum):
    CSV = "csv"
    JSON = "json"


class ExportQuery(Filter):
    """Параметры запроса GET /metrics/export."""

    export_type: ExportTypeEnum
    from_timestamp: float
    to_timestamp: float


# ---------------------------------------------------------------------------
# Настройки сервиса и коллекторов
# ---------------------------------------------------------------------------


class CollectorTypeEnum(StrEnum):
    ACTIVE_TCP = "activetcp"
    ACTIVE_UDP = "activeudp"
    ACTIVE_QUIC = "activequic"
    PASSIVE_TCP = "passivetcp"


class CollectorSettings(BaseModel):
    """Настройки коллектора."""

    name: str
    type: CollectorTypeEnum
    is_active: bool

    # Поля для active-коллекторов
    destination_ip: Optional[str] = None
    send_delay: Optional[float] = None
    loss_timeout: Optional[float] = None
    payload_size: Optional[int] = None


class CollectorSettingsPatch(BaseModel):
    """Опциональные поля для PATCH /settings/collectors/<name>."""

    name: Optional[str] = None
    type: Optional[CollectorTypeEnum] = None
    is_active: Optional[bool] = None

    destination_ip: Optional[str] = None
    send_delay: Optional[float] = None
    loss_timeout: Optional[float] = None
    payload_size: Optional[int] = None


class ServiceSettings(BaseModel):
    """Настройки сервиса (GET /settings)."""

    save_interval: float
