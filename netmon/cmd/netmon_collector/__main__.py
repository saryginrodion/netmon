import argparse
import asyncio
from pathlib import Path
import shutil

import structlog
from netmon.util.setup_logging import setup_logging

_DEFAULT_CONFIG_NAME = "netmon.yaml"


def generate_default_config():
    logger = structlog.get_logger().bind(action="generate_default_configa")

    src = Path(__file__).parent / "netmon.yaml"  # source in cmd/netmon_collector/
    dst = Path.cwd() / "netmon.yaml"  # destination in working directory

    if dst.exists():
        logger.info("netmon.yaml already exists. Move it to generate default config", path=str(dst))
        return

    try:
        shutil.copy(src, dst)
        logger.info("Default netmon.yaml generated", path=str(dst))
    except Exception as e:
        logger.error("Failed to copy netmon.yaml", error=str(e))


async def main() -> None:
    setup_logging()
    logger = structlog.get_logger()

    parser = argparse.ArgumentParser(description="Collects all data from")
    parser.add_argument(
        "--genconfig",
        action=argparse.BooleanOptionalAction,
        default=False,
        help=f"Generate default configuration at ./{_DEFAULT_CONFIG_NAME} and do nothing",
    )
    parser.add_argument("--config", type=str, default=_DEFAULT_CONFIG_NAME, help="Configuration file")

    args = parser.parse_args()

    if args.genconfig:
        return generate_default_config()


if __name__ == "__main__":
    asyncio.run(main())
