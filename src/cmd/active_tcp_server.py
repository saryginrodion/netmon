import argparse
import asyncio

import structlog
from collectors.activetcp.collector_server import ActiveTCPServer


async def main() -> None:
    logger = structlog.get_logger()

    parser = argparse.ArgumentParser(description="Active TCP Collector server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Server address")
    parser.add_argument("--port", type=int, default=8001, help="Port address")

    args = parser.parse_args()

    server = ActiveTCPServer(logger.bind(scope="ActiveTCPServer"))

    await server.start_server(args.host, args.port)

    # TODO: add Graceful shutdown
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
