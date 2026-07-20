from oil_tracker.application.services.analysis_pipeline import timestamp_schedule


def test_timestamp_schedule_uses_time_interval():
    assert timestamp_schedule(0, 1, 2) == [0.0, 0.5, 1.0]
