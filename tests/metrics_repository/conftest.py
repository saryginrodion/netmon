from pathlib import Path
import pytest

from netmon.metrics_repository.json_saver import JSONMetricsSaver

@pytest.fixture
def json_file_path(tmp_path: Path) -> Path:
    return tmp_path / "test_file.json"

@pytest.fixture
def json_saver(json_file_path: Path) -> JSONMetricsSaver:
    return JSONMetricsSaver(json_file_path)
