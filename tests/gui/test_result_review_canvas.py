from __future__ import annotations

import gc

from PySide6.QtGui import QColor, QImage

from oil_tracker.ui.widgets.result_review_canvas import ResultReviewCanvas
from review_raster_fixtures import solid_image


def test_canvas_displays_detached_qimage_and_preserves_source_dimensions(qtbot):
    canvas = ResultReviewCanvas()
    qtbot.addWidget(canvas)
    image = solid_image(320, 240, (10, 20, 30))
    canvas.set_image(image)
    image.fill(QColor(90, 100, 110))
    del image
    gc.collect()
    retained = canvas.image()
    assert canvas.source_image_size.width() == 320
    assert canvas.source_image_size.height() == 240
    color = retained.pixelColor(0, 0)
    assert (color.red(), color.green(), color.blue()) == (10, 20, 30)
    assert not canvas.label.pixmap().isNull()


def test_canvas_message_and_empty_state_remove_stale_pixmap(qtbot):
    canvas = ResultReviewCanvas()
    qtbot.addWidget(canvas)
    canvas.set_image(solid_image(80, 60))
    assert not canvas.label.pixmap().isNull()
    canvas.set_message("새 장면 없음")
    assert canvas.source_image_size.isEmpty()
    assert canvas.image().isNull()
    assert canvas.label.pixmap().isNull()
    assert canvas.label.text() == "새 장면 없음"
    canvas.set_image(None)
    assert "표시할" in canvas.label.text()


def test_canvas_replaces_general_and_debug_images_without_retaining_stale_snapshot(qtbot):
    canvas = ResultReviewCanvas()
    qtbot.addWidget(canvas)
    canvas.set_image(solid_image(320, 240, (1, 2, 3)))
    first = canvas.image()
    canvas.set_image(solid_image(640, 360, (4, 5, 6)))
    second = canvas.image()
    assert first.size() != second.size()
    assert canvas.source_image_size == second.size()
    color = second.pixelColor(0, 0)
    assert (color.red(), color.green(), color.blue()) == (4, 5, 6)


def test_resize_keeps_pixmap_aspect_ratio(qtbot):
    canvas = ResultReviewCanvas()
    qtbot.addWidget(canvas)
    canvas.resize(500, 500)
    canvas.show()
    canvas.set_image(solid_image(400, 200))
    qtbot.wait(10)
    pixmap = canvas.label.pixmap()
    assert not pixmap.isNull()
    assert abs((pixmap.width() / pixmap.height()) - 2.0) < 0.02
    assert pixmap.width() <= canvas.label.width()
    assert pixmap.height() <= canvas.label.height()


def test_canvas_is_read_only_and_has_no_raster_or_filesystem_api(qtbot):
    canvas = ResultReviewCanvas()
    qtbot.addWidget(canvas)
    assert not hasattr(canvas, "geometryChanged")
    assert not hasattr(canvas, "zeroLineChanged")
    assert not hasattr(canvas, "set_review_frame")
    assert not hasattr(canvas, "set_debug_frame")
    assert not hasattr(canvas, "refresh_overlay")
    assert not hasattr(canvas, "save_png")
    assert not hasattr(canvas, "rendered_image")


def test_close_releases_image_and_pixmap_references(qtbot):
    canvas = ResultReviewCanvas()
    qtbot.addWidget(canvas)
    canvas.set_image(solid_image(320, 240))
    canvas.close()
    qtbot.wait(1)
    assert canvas.image().isNull()
    assert canvas.source_image_size.isEmpty()
    assert canvas.label.pixmap().isNull()
