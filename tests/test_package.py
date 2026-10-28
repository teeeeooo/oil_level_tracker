import tomllib
from pathlib import Path

import oil_tracker


def test_package_version_matches_pyproject():
    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    project = tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]
    assert oil_tracker.__version__ == project["version"]
