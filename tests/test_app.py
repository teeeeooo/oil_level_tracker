import pytest

from oil_tracker import app


def test_the_close_question_replaces_pywebviews_own_words():
    localization = pytest.importorskip("webview.localization")
    assert set(app.CLOSE_QUESTION) <= set(localization.original_localization)
