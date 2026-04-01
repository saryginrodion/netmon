import argparse
import asyncio
from datetime import datetime, timedelta

import structlog
from netmon.collectors.activeudp.collector import ActiveUDPCollector
from netmon.util.setup_logging import setup_logging


async def main() -> None:
    setup_logging()
    logger = structlog.get_logger()

    parser = argparse.ArgumentParser(description="Active UDP Collector client")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Server address")
    parser.add_argument("--port", type=int, default=8001, help="Server port")
    parser.add_argument("--delay", type=float, default=5, help="Packets send delay (seconds)")
    parser.add_argument("--interval", type=float, default=15, help="Collect metrics interval (seconds)")
    parser.add_argument("--reconnect", type=float, default=15, help="Reconnect delay (seconds)")

    args = parser.parse_args()

    collector = ActiveUDPCollector(
        logger.bind(scope="ActiveUDPCollector"),
        args.host,
        args.port,
        timedelta(seconds=args.interval),
        timedelta(seconds=args.delay),
        timedelta(seconds=5),
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
