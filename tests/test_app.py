import pytest

from oil_tracker import app


def test_the_close_question_replaces_pywebviews_own_words():
    localization = pytest.importorskip("webview.localization")
    assert set(app.CLOSE_QUESTION) <= set(localization.original_localization)


def test_the_video_window_opens_again_where_it_was_left(tmp_path):
    place = tmp_path / "settings" / app.VIDEO_WINDOW_FILE
    assert app.load_place(place) == {}
    app.save_place(place, {"x": -1500, "y": 40, "width": 1600, "height": 900})
    assert app.load_place(place) == {"x": -1500, "y": 40, "width": 1600, "height": 900}
    place.write_text('{"x": 10, "y": "20", "width": 300, "height": 900, "z": 1}', encoding="utf-8")
    assert app.load_place(place) == {"x": 10}  # a bad value is dropped; a window smaller than the minimum is not kept
    place.write_text("not json", encoding="utf-8")
    assert app.load_place(place) == {}


def test_a_saved_place_off_every_screen_is_not_used(tmp_path):
    class Screen:
        def __init__(self, x, y, width, height):
            self.x, self.y, self.width, self.height = x, y, width, height

    class Webview:
        screens = [Screen(0, 0, 1920, 1080), Screen(-1920, 0, 1920, 1080)]

    window = app.VideoWindow(Webview(), lambda: "http://127.0.0.1:1", tmp_path / "w.json")
    assert window._on_a_screen(-1500, 40, 1280, 800)       # the second monitor
    assert window._on_a_screen(100, 100, 1280, 800)
    assert not window._on_a_screen(4000, 100, 1280, 800)   # a monitor that is gone
    assert not window._on_a_screen(100, 1070, 1280, 800)   # the title bar off the bottom
    assert not window._on_a_screen(None, None, 1280, 800)


def test_the_log_keeps_what_the_console_shows(tmp_path, monkeypatch):
    crashes = []
    monkeypatch.setattr(app.faulthandler, "enable", crashes.append)
    monkeypatch.setattr(app.sys, "stderr", None)  # a windowed build
    log = app.start_log(tmp_path / "settings")
    app.sys.stderr.write("Traceback (most recent call last):\n")
    log.close()
    lines = (tmp_path / "settings" / app.LOG_FILE).read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith("--- ") and "start: " in lines[0] and "(source)" in lines[0]
    assert lines[1] == "Traceback (most recent call last):"
    assert crashes == [log]


def test_a_long_log_is_kept_once_as_the_old_log(tmp_path, monkeypatch):
    monkeypatch.setattr(app.faulthandler, "enable", lambda log: None)
    monkeypatch.setattr(app.sys, "stderr", None)
    (tmp_path / app.LOG_FILE).write_text("x" * (app.LOG_ROLL_BYTES + 1), encoding="utf-8")
    app.start_log(tmp_path).close()
    assert (tmp_path / app.LOG_OLD).stat().st_size == app.LOG_ROLL_BYTES + 1
    assert (tmp_path / app.LOG_FILE).read_text(encoding="utf-8").startswith("--- ")


def test_the_console_still_shows_it(tmp_path, monkeypatch):
    import io

    console = io.StringIO()
    monkeypatch.setattr(app.faulthandler, "enable", lambda log: None)
    monkeypatch.setattr(app.sys, "stderr", console)
    app.start_log(tmp_path)
    app.sys.stderr.write("line\n")
    assert console.getvalue() == "line\n"


def test_no_log_when_the_folder_cannot_be_written(tmp_path, monkeypatch):
    (tmp_path / "file").write_text("", encoding="utf-8")
    console = object()
    monkeypatch.setattr(app.sys, "stderr", console)
    assert app.start_log(tmp_path / "file" / "settings") is None
    assert app.sys.stderr is console


def test_the_debugging_port_only_when_asked():
    assert app.debug_port({}) is None
    assert app.debug_port({app.DEBUG_PORT_VARIABLE: "9333"}) == 9333
    assert app.debug_port({app.DEBUG_PORT_VARIABLE: "x"}) is None
    assert app.debug_port({app.DEBUG_PORT_VARIABLE: "70000"}) is None
