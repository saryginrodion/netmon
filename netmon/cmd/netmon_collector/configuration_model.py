from datetime import timedelta
from pathlib import Path
from pydantic import BaseModel

from netmon.cmd.netmon_collector.collector_configuration_models import CollectorConfig


class StorageConfig(BaseModel):
    file_path: Path


class NetmonConfig(BaseModel):
    collect_interval: timedelta

    storage: StorageConfig

    collectors: list[CollectorConfig]
