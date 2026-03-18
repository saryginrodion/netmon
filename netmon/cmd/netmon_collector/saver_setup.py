from netmon.cmd.netmon_collector.configuration_model import StorageConfig
from netmon.metrics_repository.interface import MetricsSaver
from netmon.metrics_repository.json_saver import JSONMetricsSaver


async def saver_setup(conf: StorageConfig) -> MetricsSaver:
    saver = JSONMetricsSaver(conf.file_path)
    return saver
