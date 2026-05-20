from enum import Enum


class CollectorStatus(Enum):
    active = "active"
    stopped = "stopped"
    failed = "failed"
