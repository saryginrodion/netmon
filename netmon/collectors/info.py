from pydantic import BaseModel
from netmon.collectors.collector_status import CollectorStatus


class CollectorInfo(BaseModel):
    name: str
    status: CollectorStatus
