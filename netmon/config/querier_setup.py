import structlog
from netmon.config.configuration_model import StorageConfig
from netmon.influxdb3.conn import connect
from netmon.metrics_repository.influxdb3.querier import Influxdb3MetricQuerier
from netmon.metrics_repository.interface import MetricQuerier


async def querier_setup(conf: StorageConfig) -> MetricQuerier:
    logger = structlog.get_logger().bind(scope="Influxdb3MetricQuerier", host=conf.host, database=conf.database)
    querier = Influxdb3MetricQuerier(
        logger,
        connect(conf.host, conf.database, conf.token),
    )

    return querier
