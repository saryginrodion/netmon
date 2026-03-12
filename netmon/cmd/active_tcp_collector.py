import argparse
import asyncio
from datetime import datetime, timedelta
import logging

import structlog
from netmon.collectors.activetcp.collector import ActiveTCPCollector


def setup_logging() -> None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.CallsiteParameterAdder(
                {
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.LINENO,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                }
            ),
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )


async def main() -> None:
    setup_logging()
    logger = structlog.get_logger()

    parser = argparse.ArgumentParser(description="Active TCP Collector client")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Server address")
    parser.add_argument("--port", type=int, default=8001, help="Server port")
    parser.add_argument("--delay", type=float, default=5, help="Packets send delay (seconds)")
    parser.add_argument("--interval", type=float, default=15, help="Collect metrics interval (seconds)")
    parser.add_argument("--reconnect", type=float, default=15, help="Reconnect delay (seconds)")

    args = parser.parse_args()

    collector = ActiveTCPCollector(
        logger.bind(scope="ActiveTCPCollector"),
        args.host,
        args.port,
        timedelta(seconds=args.interval),
        timedelta(seconds=args.delay),
        timedelta(seconds=args.reconnect),
        timedelta(seconds=4),
        timedelta(seconds=4),
    )

    await collector.start_collector()

    while True:
        metrics = await collector.collect(datetime.now())
        for metric in metrics:
            if metric.rtt is not None:
                jitter = metric.rtt.maximum - metric.rtt.minimum
                logger.info("metric collected", jitter=jitter, rtt=metric.rtt.value, metrics=metric)
            await asyncio.sleep(args.interval)


if __name__ == "__main__":
    asyncio.run(main())
