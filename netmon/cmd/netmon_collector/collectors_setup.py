import structlog
from netmon.cmd.netmon_collector.collector_configuration_models import ActiveTCPConfig, ActiveUDPConfig
from netmon.cmd.netmon_collector.configuration_model import NetmonConfig
from netmon.collectors.activetcp.collector import ActiveTCPCollector
from netmon.collectors.activeudp.collector import ActiveUDPCollector
from netmon.collectors.interface import MetricsCollector


async def _active_tcp_setup(conf: ActiveTCPConfig, netmon_conf: NetmonConfig) -> ActiveTCPCollector:
    logger = structlog.get_logger().bind(scope=conf.type, addr=conf.addr, port=conf.port)

    collector = ActiveTCPCollector(
        logger,
        str(conf.addr),
        conf.port,
        netmon_conf.collect_interval,
        conf.packet_send_delay,
        conf.reconnect_interval,
        conf.read_timeout,
        conf.write_timeout,
    )

    await collector.start_collector()
    return collector


async def _active_udp_setup(conf: ActiveUDPConfig, netmon_conf: NetmonConfig) -> ActiveUDPCollector:
    logger = structlog.get_logger().bind(scope=conf.type, addr=conf.addr, port=conf.port)

    collector = ActiveUDPCollector(
        logger,
        str(conf.addr),
        conf.port,
        netmon_conf.collect_interval,
        conf.packet_send_delay,
        conf.read_timeout,
    )

    await collector.start_collector()
    return collector


_REGISTRY = {
    "activetcp": _active_tcp_setup,
    "activeudp": _active_udp_setup,
}


async def setup_collectors(configuration: NetmonConfig) -> list[MetricsCollector]:
    logger = structlog.get_logger().bind(action="setup_collectors")
    collectors = []

    for collector_conf in configuration.collectors:
        if collector_conf.type not in _REGISTRY:
            e = Exception("can not find this type of collector in _REGISTRY")
            logger.exception("failed to setup collectors", error=str(e))
            raise e

        collector = await _REGISTRY[collector_conf.type](collector_conf, configuration)
        logger.info("setup collector successfully", collector_type=collector_conf.type)
        collectors.append(collector)

    return collectors
