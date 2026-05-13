import argparse
from contextlib import asynccontextmanager
import shutil
from pathlib import Path

from fastapi import FastAPI
import structlog
import uvicorn
import yaml

from netmon.api.app import initialize_app
from netmon.api.dependencies.ids import COLLECTORS_MANAGER, METRIC_QUERIER
from netmon.api.dependencies.registry import DI_REGISTRY
from netmon.cmd.netmon_collector.collectors_setup import setup_collectors
from netmon.cmd.netmon_collector.configuration_model import NetmonConfig
from netmon.cmd.netmon_collector.querier_setup import querier_setup
from netmon.cmd.netmon_collector.saver_setup import saver_setup
from netmon.collectors.manager import CollectorsManager
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


def must_load_config(logger: structlog.BoundLogger, config_path: str) -> NetmonConfig:
    logger.info("parsing config", config_path=config_path)

    with open(config_path, "r") as f:
        config_dict = yaml.safe_load(f)

    return NetmonConfig.model_validate(config_dict)  # type: ignore


def main() -> None:
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

    config = must_load_config(logger, args.config)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        collectors = await setup_collectors(config)
        saver = await saver_setup(config.storage)
        querier = await querier_setup(config.storage)
        manager = CollectorsManager(
            logger=logger.bind(scope="CollectorsManager"),
            collectors=collectors,
            metric_saver=saver,
            collection_interval=config.collect_interval,
        )
        manager.start_collection()

        DI_REGISTRY.register(COLLECTORS_MANAGER, manager)
        DI_REGISTRY.register(METRIC_QUERIER, querier)

        yield

    app = FastAPI(title="Netmon API", lifespan=lifespan)

    initialize_app(app)

    uvicorn.run(app, host="0.0.0.0", port=config.api.port)


if __name__ == "__main__":
    main()
