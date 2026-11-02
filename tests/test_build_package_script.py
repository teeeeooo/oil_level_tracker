import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_package", ROOT / "scripts" / "build_package.py")
script = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(script)


def test_the_folder_state_has_each_file_once(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "x.dll").write_bytes(b"1")
    (tmp_path / "y.txt").write_bytes(b"2")
    try:
        (tmp_path / "link").symlink_to(tmp_path / "y.txt")
    except OSError:
        pass  # Windows without the right to make links: nothing to leave out
    state = script.folder_state(tmp_path)
    assert sorted(state) == ["a/x.dll", "y.txt"]
    (tmp_path / "y.txt").write_bytes(b"3")
    assert script.folder_state(tmp_path)["y.txt"] != state["y.txt"]


def test_the_spec_ships_the_web_folder_where_the_package_reads_it():
    from oil_tracker import bootstrap

    spec = script.SPEC.read_text(encoding="utf-8")
    assert '"oil_tracker/web"' in spec
    assert bootstrap.WEB_FOLDER.relative_to(ROOT / "src").as_posix() == "oil_tracker/web"
    assert 'name="OilLevelTracker"' in spec and "console=False" in spec
    assert (ROOT / "packaging" / "OilLevelTracker.ico").is_file()


@pytest.mark.parametrize("page", script.PAGES)
def test_the_checked_pages_exist(page):
    assert (ROOT / "src" / "oil_tracker" / page.removeprefix("/")).is_file()
