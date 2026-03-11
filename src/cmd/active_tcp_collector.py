import argparse
import asyncio
from datetime import timedelta
import logging

import structlog
from collectors.activetcp.collector import ActiveTCPCollector


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
        wrapper_class=structlog.make_filtering_bound_logger(logging.NOTSET),
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
    parser.add_argument("--delay", type=int, default=5, help="Packets send delay (seconds)")
    parser.add_argument("--interval", type=int, default=60, help="Collect metrics interval (seconds)")
    parser.add_argument("--reconnect", type=int, default=15, help="Reconnect delay (seconds)")

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

    await collector.run_collector()


if __name__ == "__main__":
    asyncio.run(main())
