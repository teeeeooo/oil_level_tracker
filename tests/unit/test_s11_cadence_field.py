from __future__ import annotations

from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
from tests.diagnostics import s11_cadence_field as cad


def _row(time, fill="UNKNOWN_REVIEW", oil=None, flags=""):
    return {"timestamp_sec": str(time), "fill_state": fill, "raw_oil_air_level_y": "" if oil is None else str(oil),
            "flags": flags}


def _base(first_full=24.0, end=63.0, step=0.5, late_full=None):
    rows = []
    t = 0.0
    while t <= 90.0:
        if t < first_full:
            rows.append(_row(t, "PARTIAL_VISIBLE", 700.0))
        elif t < end:
            rows.append(_row(t, "FULL_NO_INTERFACE", flags=cad.TOP_EXIT_FLAG if t == first_full else ""))
        elif late_full is not None and t >= late_full:
            rows.append(_row(t, "FULL_NO_INTERFACE"))
        else:
            rows.append(_row(t, "DRAINING_VISIBLE", 320.0))
        t = round(t + step, 6)
    return rows


def test_readings_pass_inside_every_frozen_window():
    readings = cad.readings(_base(), [_row(t / 2) for t in range(181)])
    assert readings["first_full_sec"] == 24.0 and readings["first_full_top_exit"] is True
    assert readings["episode_end_sec"] == 63.0
    assert all(readings[key] for key in ("c1", "c2", "c3", "c4", "c5"))


def test_readings_fail_outside_the_windows_and_on_a_hold_break():
    early = cad.readings(_base(first_full=21.5), None)
    assert early["c1"] is False and early["c5"] is None
    broken = _base()
    broken[80] = _row(40.0, "PARTIAL_VISIBLE", 500.0)
    result = cad.readings(broken, [_row(30.0, "FULL_WITH_FOAM")])
    assert result["c2"] is False and result["hold_breaks"] == [[40.0, "PARTIAL_VISIBLE", 500.0]]
    assert result["episode_end_sec"] == 40.0 and result["c3"] is False
    assert result["c5"] is False and result["accum_full_rows"] == 1
    late = cad.readings(_base(late_full=80.0), None)
    assert late["c4"] is False and late["late_full_rows"] > 0


def test_readings_without_full_fail_c1_c2_and_c3():
    result = cad.readings([_row(t / 2, "PARTIAL_VISIBLE", 700.0) for t in range(181)], None)
    assert result["first_full_sec"] is None
    assert (result["c1"], result["c2"], result["c3"], result["c4"]) == (False, False, False, True)


def test_timers_restore_the_wrapped_entry_points():
    original = OpenCvVideoReader.__dict__["read_at"]
    with cad.timers() as totals:
        assert OpenCvVideoReader.__dict__["read_at"] is not original
    assert OpenCvVideoReader.__dict__["read_at"] is original
    assert totals == {}
