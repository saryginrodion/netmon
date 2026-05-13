from netmon.cmd.netmon_collector.configuration_model import StorageConfig
from netmon.metrics_repository.dummy.querier import DummyMetricQuerier
from netmon.metrics_repository.interface import MetricQuerier


async def querier_setup(conf: StorageConfig) -> MetricQuerier:
    saver = DummyMetricQuerier()

    return saver
