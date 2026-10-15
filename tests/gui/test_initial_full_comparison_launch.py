from __future__ import annotations

import pytest


@pytest.mark.parametrize("enabled", [False, True])
@pytest.mark.parametrize("cost_first", [False, True])
def test_gui_comparison_mode_reaches_every_detector_entry(qtbot, monkeypatch, tmp_path, enabled, cost_first):
    monkeypatch.setenv("MPLCONFIGDIR", str(tmp_path / "mpl"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    import oil_tracker.bootstrap as bootstrap
    monkeypatch.setattr(bootstrap, "configure_logging", lambda: None)
    window = bootstrap.build_main_window(
        initial_full_observation=enabled, cost_first_assignment=cost_first,
    )
    qtbot.addWidget(window)
    detectors = (
        window.preview_controller.use_case.detector,
        window.analysis_controller.analyze_use_case.pipeline.detector,
        window.preflight_coordinator.controller.use_case.detector_factory(),
        window.redetection_service.detector_factory(),
    )
    assert ("초기 FULL 관측 비교" in window.windowTitle()) is enabled
    assert ("Oil cost-first 비교" in window.windowTitle()) is cost_first
    assert all(("+initial-full-observation-v2" in detector.version) is enabled for detector in detectors)
    assert all(detector._observation_sequence_resolver._oil.config.initial_full_observation_enabled is enabled for detector in detectors)
    for detector in detectors:
        resolver = detector._observation_sequence_resolver
        assert resolver._oil.config.cost_first_assignment_enabled is cost_first
        for version in (detector.version, resolver.version, resolver._oil.version):
            assert ("+cost-first-assignment-v1" in version) is cost_first


@pytest.mark.parametrize("args,expected", [
    ([], {}),
    (["--initial-full-observation"], {"initial_full_observation": True}),
    (["--oil-cost-first-assignment"], {"cost_first_assignment": True}),
    (["--initial-full-observation", "--oil-cost-first-assignment"],
     {"initial_full_observation": True, "cost_first_assignment": True}),
])
def test_main_launch_flag_selects_the_real_bootstrap_mode(qapp, monkeypatch, args, expected):
    from oil_tracker import __main__ as entry
    calls = []

    class Window:
        def show(self):
            calls.append("show")

    def build(**kwargs):
        calls.append(kwargs)
        return Window()

    monkeypatch.setattr(entry, "build_main_window", build)
    monkeypatch.setattr(entry.QApplication, "exec", lambda self: 17)
    monkeypatch.setattr(entry.sys, "argv", ["oil-tracker", *args])
    assert entry.main() == 17
    assert calls == [expected, "show"]
