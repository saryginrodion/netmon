import argparse
import asyncio

import structlog
from netmon.collectors.activeudp.collector_server import ActiveUDPServer


async def main() -> None:
    logger = structlog.get_logger()

    parser = argparse.ArgumentParser(description="Active UDP Collector server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Server address")
    parser.add_argument("--port", type=int, default=8001, help="Port address")

    args = parser.parse_args()

    server = ActiveUDPServer(logger.bind(scope="ActiveUDPServer"))

    await server.start(args.host, args.port)

    # TODO: add Graceful shutdown
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
