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


def test_the_spec_gives_the_exe_the_app_version():
    spec = script.SPEC.read_text(encoding="utf-8")
    assert "version=version_resource(VERSION) if WINDOWS else None" in spec
    assert '["project"]["version"]' in spec  # the one version, which tests/test_package.py ties to the code


def fake_package(folder: Path) -> Path:
    package = folder / "OilLevelTracker"
    (package / "_internal" / "oil_tracker" / "web" / "manual").mkdir(parents=True)
    (package / "OilLevelTracker.exe").write_bytes(b"exe")
    (package / script.MANUAL_IN_PACKAGE).write_text("manual", encoding="utf-8")
    return package


def test_the_release_zip_puts_the_install_guide_beside_the_app_folder(tmp_path):
    import zipfile
    from html.parser import HTMLParser

    archive = script.release_zip(fake_package(tmp_path), "9.8.7", tmp_path / "release")
    assert archive.name == "OilLevelTracker-9.8.7.zip"
    with zipfile.ZipFile(archive) as opened:
        names = opened.namelist()
        guide_info = opened.getinfo(script.GUIDE_NAME)
        guide = opened.read(script.GUIDE_NAME).decode("utf-8")
    assert sorted(names) == sorted([
        "설치 안내.html", "OilLevelTracker/OilLevelTracker.exe", "OilLevelTracker/" + script.MANUAL_IN_PACKAGE,
    ])
    assert guide_info.flag_bits & 0x800  # the Korean name is marked UTF-8, which Windows reads
    # one file that works on its own: styles inlined, the version filled in, links that lead somewhere
    assert "<!--STYLE-->" not in guide and "<!--VERSION-->" not in guide and "<link" not in guide
    assert "--brand:" in guide and "Oil Level Tracker 9.8.7 설치 안내" in guide and "OilLevelTracker-9.8.7.zip" in guide

    hrefs = []

    class Links(HTMLParser):
        def handle_starttag(self, tag, attrs):
            hrefs.extend(value for key, value in attrs if key == "href")

    Links().feed(guide)
    assert hrefs == ["OilLevelTracker/" + script.MANUAL_IN_PACKAGE] and hrefs[0] in names


def test_the_release_zip_needs_the_manual_the_guide_links_to(tmp_path):
    package = fake_package(tmp_path)
    (package / script.MANUAL_IN_PACKAGE).unlink()
    with pytest.raises(FileNotFoundError):
        script.release_zip(package, "9.8.7", tmp_path / "release")


def test_the_guides_manual_link_is_where_the_spec_ships_the_manual():
    # PyInstaller 6 puts the data under _internal/; the spec ships web/ as oil_tracker/web
    assert script.MANUAL_IN_PACKAGE.startswith("_internal/oil_tracker/web/")
    assert (ROOT / "src" / script.MANUAL_IN_PACKAGE.removeprefix("_internal/")).is_file()
