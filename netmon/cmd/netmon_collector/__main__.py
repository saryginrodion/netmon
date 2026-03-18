import argparse
import asyncio
from datetime import datetime
import shutil
from pathlib import Path

import structlog
import yaml

from netmon.cmd.netmon_collector.collectors_setup import setup_collectors
from netmon.cmd.netmon_collector.configuration_model import NetmonConfig
from netmon.cmd.netmon_collector.saver_setup import saver_setup
from netmon.collectors.mergecollector.collector import MergeCollector
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
        generate_default_config()
        return

    logger.info("parsing config", config_path=args.config)

    with open(args.config, "r") as f:
        config_dict = yaml.safe_load(f)

    config = NetmonConfig.model_validate(config_dict)  # type: ignore
    logger.info("config parsed")

    collectors = await setup_collectors(config)
    merge_collector = MergeCollector(logger.bind(scope="MergeCollector"), collectors)
    logger.info("collectors setup")

    saver = await saver_setup(config.storage)
    logger.info("metrics saver setup")

    # TODO: Change to running MetricsAggregator
    while True:
        try:
            metrics = list(await merge_collector.collect(datetime.now()))
            await saver.save_metrics(metrics)
            logger.info("collected metrics", entries_count=len(metrics))
            await asyncio.sleep(config.collect_interval.total_seconds())
        except Exception as e:
            logger.exception("exception in collect and save loop", error=str(e))


if __name__ == "__main__":
    asyncio.run(main())
