import structlog
from netmon.config.configuration_model import StorageConfig
from netmon.influxdb3.conn import connect
from netmon.metrics_repository.influxdb3.saver import Influxdb3MetricsSaver
from netmon.metrics_repository.interface import MetricsSaver


async def saver_setup(conf: StorageConfig) -> MetricsSaver:
    logger = structlog.get_logger().bind(scope="Influxdb3MetricSaver", host=conf.host, database=conf.database)
    saver = Influxdb3MetricsSaver(
        logger,
        connect(conf.host, conf.database, conf.token),
    )

    return saver
