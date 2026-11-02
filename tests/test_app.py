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
