from __future__ import annotations

import pytest


@pytest.mark.parametrize("enabled", [False, True])
@pytest.mark.parametrize("cost_first,rgb,top_exit,contest,fast_rise,colocation", [
    (False, False, False, False, False, False), (True, False, False, False, False, False),
    (False, True, False, False, False, False), (False, False, True, False, False, False),
    (False, False, False, True, False, False), (False, False, True, True, False, False),
    (False, False, False, False, True, False), (False, False, True, False, True, False),
    (False, False, False, False, False, True), (False, False, True, True, False, True),
])
def test_gui_comparison_mode_reaches_every_detector_entry(qtbot, monkeypatch, tmp_path, enabled, cost_first, rgb,
                                                          top_exit, contest, fast_rise, colocation):
    monkeypatch.setenv("MPLCONFIGDIR", str(tmp_path / "mpl"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    import oil_tracker.bootstrap as bootstrap
    monkeypatch.setattr(bootstrap, "configure_logging", lambda: None)
    window = bootstrap.build_main_window(
        initial_full_observation=enabled, cost_first_assignment=cost_first, candidate_rgb=rgb, top_exit_full=top_exit,
        fill_owner_contest=contest, fast_rise_association=fast_rise, fill_owner_colocation=colocation,
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
    assert ("Oil RGB 비교" in window.windowTitle()) is rgb
    assert ("상단 이탈 FULL 비교" in window.windowTitle()) is top_exit
    assert ("채움 주인 경쟁 비교" in window.windowTitle()) is contest
    assert ("빠른 상승 연결 비교" in window.windowTitle()) is fast_rise
    assert ("채움 주인 동일 위치 비교" in window.windowTitle()) is colocation
    assert all(("+initial-full-observation-v2" in detector.version) is enabled for detector in detectors)
    assert all(detector._observation_sequence_resolver._oil.config.initial_full_observation_enabled is enabled for detector in detectors)
    for detector in detectors:
        resolver = detector._observation_sequence_resolver
        assert resolver._oil.config.cost_first_assignment_enabled is cost_first
        assert resolver._oil.config.candidate_rgb_enabled is rgb
        assert resolver._oil.config.top_exit_full_enabled is top_exit
        assert resolver._oil.config.fill_owner_contest_enabled is contest
        assert resolver._oil.config.fast_rise_association_enabled is fast_rise
        assert resolver._oil.config.fill_owner_colocation_enabled is colocation
        assert (detector._frame_result_projector._candidate_rgb is not None) is rgb
        for version in (detector.version, resolver.version, resolver._oil.version):
            assert ("+cost-first-assignment-v1" in version) is cost_first
            assert ("+candidate-rgb-v1" in version) is rgb
            assert ("+top-exit-full-v3" in version) is top_exit
            assert ("+fill-owner-contest-v1" in version) is contest
            assert ("+fast-rise-association-v1" in version) is fast_rise
            assert ("+fill-owner-colocation-v1" in version) is colocation


@pytest.mark.parametrize("args,expected", [
    ([], {}),
    (["--oil-top-exit-full"], {"top_exit_full": True}),
    (["--initial-full-observation", "--oil-top-exit-full"],
     {"initial_full_observation": True, "top_exit_full": True}),
    (["--initial-full-observation"], {"initial_full_observation": True}),
    (["--oil-cost-first-assignment"], {"cost_first_assignment": True}),
    (["--initial-full-observation", "--oil-cost-first-assignment"],
     {"initial_full_observation": True, "cost_first_assignment": True}),
    (["--oil-candidate-rgb"], {"candidate_rgb": True}),
    (["--initial-full-observation", "--oil-candidate-rgb"],
     {"initial_full_observation": True, "candidate_rgb": True}),
    (["--oil-fill-owner-contest"], {"fill_owner_contest": True}),
    (["--initial-full-observation", "--oil-top-exit-full", "--oil-fill-owner-contest"],
     {"initial_full_observation": True, "top_exit_full": True, "fill_owner_contest": True}),
    (["--oil-fast-rise-association"], {"fast_rise_association": True}),
    (["--initial-full-observation", "--oil-top-exit-full", "--oil-fast-rise-association"],
     {"initial_full_observation": True, "top_exit_full": True, "fast_rise_association": True}),
    (["--oil-fill-owner-colocation"], {"fill_owner_colocation": True}),
    (["--initial-full-observation", "--oil-top-exit-full", "--oil-fill-owner-contest", "--oil-fill-owner-colocation"],
     {"initial_full_observation": True, "top_exit_full": True, "fill_owner_contest": True,
      "fill_owner_colocation": True}),
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


@pytest.mark.parametrize("args", [
    ["--oil-cost-first-assignment", "--oil-candidate-rgb"],
    ["--oil-fill-owner-contest", "--oil-cost-first-assignment"],
    ["--oil-fill-owner-contest", "--oil-candidate-rgb"],
    ["--oil-fast-rise-association", "--oil-cost-first-assignment"],
    ["--oil-fast-rise-association", "--oil-candidate-rgb"],
    ["--oil-fill-owner-colocation", "--oil-cost-first-assignment"],
    ["--oil-fill-owner-colocation", "--oil-candidate-rgb"],
])
def test_main_disallows_stacked_candidate_comparisons(monkeypatch, args):
    from oil_tracker import __main__ as entry
    monkeypatch.setattr(entry.sys, "argv", ["oil-tracker", *args])
    with pytest.raises(SystemExit) as error:
        entry.main()
    assert error.value.code == 2
