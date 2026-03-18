import argparse
import asyncio

import structlog
from netmon.util.setup_logging import setup_logging


async def main() -> None:
    setup_logging()
    logger = structlog.get_logger()

    parser = argparse.ArgumentParser(description="Collects all data from")
    parser.add_argument("--gen-defaul-config", action=argparse.BooleanOptionalAction, help="Generate default configuration and do nothing")
    parser.add_argument("--config", type=str, default="netmon.yaml", help="Configuration file")

    pass


if __name__ == "__main__":
    asyncio.run(main())
