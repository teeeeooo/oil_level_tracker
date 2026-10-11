"""Independent enumeration oracle for the offline centre-conditioned sidecar."""
from dataclasses import asdict, replace
from itertools import product
import math
import numpy as np
import pytest
from oil_tracker.adapters.vision import oil_material_path as m


def profiles(seed=0, height=7):
    rng = np.random.default_rng(seed)
    result = []
    for i in range(5):
        score = rng.choice([0., .1, .3, .8], height).astype(np.float32)
        signed = rng.choice([-.2, -.04, .0, .04, .2], height).astype(np.float32)
        support = rng.choice([.3, .42, 1.], height).astype(np.float32)
        result.append(m._SectorProfile(i*4, (i+1)*4, score, signed, support, i))
    return result


def enumerate_paths(ps, seed, polarity, jump, center_index):
    """Enumerate every legal contiguous path, independently of DP recurrence."""
    best = {}
    rows = range(max(0, seed-jump), min(ps[0].score.size, seed+jump+1))
    for start in range(center_index+1):
        for stop in range(max(center_index+1, start+3), len(ps)+1):
            choices = [[y for y in rows if float(p.score[y]) >= .09
                        and p.support[y] >= .42 and polarity*float(p.signed[y]) >= .025]
                       for p in ps[start:stop]]
            for path in product(*choices):
                if any(abs(a-b) > jump for a,b in zip(path, path[1:])):
                    continue
                score = 0.
                for p,y in zip(ps[start:stop], path):
                    score += float(p.score[y]) + .08*min(1., abs(float(p.signed[y]))/.20)
                key = path[center_index-start]
                value = (len(path), score)
                if key not in best or value > best[key]:
                    best[key] = value
    return best


@pytest.mark.parametrize("case", range(40))
def test_dp_matches_complete_enumeration(case):
    ps = profiles(case)
    for ci in range(5):
        for polarity in (-1, 1):
            best, _ = m._center_conditioned_paths(3, ps, ci, polarity, 2)
            expected = enumerate_paths(ps, 3, polarity, 2, ci)
            assert set(best) == set(expected)
            for y, state in best.items():
                assert len(state[1]) == expected[y][0]
                assert state[0] == pytest.approx(expected[y][1], rel=0, abs=1e-14)
                assert state[1][state[4].index(ci)] == y
                assert all(abs(a-b) <= 2 for a,b in zip(state[1],state[1][1:]))


def flat_profiles():
    return [m._SectorProfile(i*4,(i+1)*4,np.full(7,.4,np.float32),
            np.full(7,.2,np.float32),np.ones(7,np.float32),i) for i in range(5)]


def test_complete_capture_deterministic_nonmutating_and_provenance():
    ps = flat_profiles()
    before = [(p.score.tobytes(),p.signed.tobytes(),p.support.tobytes()) for p in ps]
    a = m.diagnose_center_path_alternatives(ps)
    assert a.status == "COMPLETE" and a.alternatives
    assert asdict(a) == asdict(m.diagnose_center_path_alternatives(ps))
    assert before == [(p.score.tobytes(),p.signed.tobytes(),p.support.tobytes()) for p in ps]
    for r in a.alternatives:
        if r.status == "PATH":
            assert len(r.rows) == 5 and r.polarity == 1
            assert r.rows[2] == r.center_row
            assert r.passes_path_median_checks
            assert all(s.contrast_channel == "unavailable" for s in r.samples)
        else:
            assert r.status == "CENTER_INELIGIBLE" and r.polarity == -1


def test_preserves_float32_support_boundary_semantics():
    ps = [replace(p,support=np.full(7,.42,np.float32)) for p in flat_profiles()]
    old = m._polarity_path_for_seed(3,ps,polarity=1,maximum_jump=2,capture_diagnostics=True)
    best, _ = m._center_conditioned_paths(3,ps,2,1,2)
    assert old is not None and best


@pytest.mark.parametrize("budget", [{"max_records":1}, {"max_transitions":1}])
def test_budget_returns_no_partial_success(budget):
    a = m.diagnose_center_path_alternatives(flat_profiles(),**budget)
    assert a.status == "UNAVAILABLE" and not a.alternatives


def test_missing_center_does_not_shift_to_neighbor():
    ps = [p for p in flat_profiles() if p.sector_index != 2]
    a = m.diagnose_center_path_alternatives(ps)
    assert a.status == "UNAVAILABLE" and "missing_center" in a.reason


def test_local_center_can_be_eligible_but_unreachable():
    ps = flat_profiles()
    for i in (1,3):
        ps[i] = replace(ps[i], signed=np.full(7,-.2,np.float32))
    best, _ = m._center_conditioned_paths(3,ps,2,1,2)
    assert not best and m._center_node_ok(ps[2],3,1)


def test_median_failure_is_not_silently_dropped():
    ps = [replace(p,score=np.full(7,.10,np.float32)) for p in flat_profiles()]
    best, _ = m._center_conditioned_paths(3,ps,2,1,2)
    r = m._center_alternative(3,1,3,"PATH",best[3],ps)
    assert r.status == "PATH" and r.passes_path_median_checks is False


@pytest.mark.parametrize("value", [np.nan, np.inf, -np.inf])
def test_nonfinite_profile_is_invalid_not_negative(value):
    ps = flat_profiles(); ps[0].signed[0] = value
    with pytest.raises(ValueError,match="finite"):
        m.diagnose_center_path_alternatives(ps)


def test_seed_starvation_is_not_falsely_repaired():
    ps = []
    for i,y in enumerate([120,100,80,60,40]):
        score=np.zeros(160,np.float32); signed=score.copy(); score[y]=1.; signed[y]=.2
        ps.append(m._SectorProfile(i*4,(i+1)*4,score,signed,np.ones(160,np.float32),i))
    a = m.diagnose_center_path_alternatives(ps)
    assert a.status == "COMPLETE" and a.seeds == () and a.alternatives == ()


def test_scalar_and_production_candidate_authority_are_absent():
    a = m.diagnose_center_path_alternatives(flat_profiles())
    assert not hasattr(a,"selected")
    assert all(not hasattr(r,"candidate_y") and not hasattr(r,"selected") for r in a.alternatives)


def test_provenance_channels_and_scales_are_exact():
    ps = [replace(p,contrast_channel=np.ones(7,np.uint8),
                  contrast_scale=np.full(7,6,np.uint8)) for p in flat_profiles()]
    a = m.diagnose_center_path_alternatives(ps)
    for r in a.alternatives:
        for s in r.samples:
            assert s.start_x == 4*s.sector_index and s.stop_x == 4*(s.sector_index+1)
            assert s.strength == float(ps[s.sector_index].score[s.local_y])
            assert (s.contrast_channel,s.contrast_scale_px) == ("blurred_gray_dynamic_range",6)


def test_default_generator_never_calls_offline_extension(monkeypatch):
    from oil_tracker.adapters.vision.preprocessing import preprocess
    from oil_tracker.domain.recipe import DetectorSettings
    def forbidden(*args, **kwargs):
        raise AssertionError("Offline diagnostic entered production generation")
    monkeypatch.setattr(m,"diagnose_center_path_alternatives",forbidden)
    frame=np.full((120,120,3),145,np.uint8); frame[60:]=70
    mask=np.full((120,120),255,np.uint8)
    pre=preprocess(frame,mask,DetectorSettings())
    assert m.generate_material_path_candidates(pre,mask,None,crop_origin_y=0,diagnostic_paths={})


def test_trial_cannot_overwrite_completed_evidence(tmp_path):
    from scripts import s11_center_path_trial as trial
    path=tmp_path/"readout.json"; path.write_text("preserve")
    with pytest.raises(FileExistsError): trial.run(tmp_path,tmp_path)
    assert path.read_text()=="preserve"


def test_trial_rejects_repurposed_source_set_before_loading(tmp_path):
    from scripts import s11_center_path_trial as trial
    trial.save(tmp_path/"preflight.json",{"samples":["sample3"]})
    with pytest.raises(ValueError,match="Unexpected source set"):
        trial.run(tmp_path,tmp_path)


def test_trial_calls_existing_admission_guard(tmp_path,monkeypatch):
    from scripts import s11_center_path_trial as trial
    samples=("sample4","sample5","sample6","sample7")
    trial.save(tmp_path/"preflight.json",{"samples":samples})
    def guard(actual):
        assert actual==samples
        raise RuntimeError("admission checked before raster work")
    monkeypatch.setattr(trial,"require_corpus_access",guard)
    with pytest.raises(RuntimeError,match="admission checked"):
        trial.run(tmp_path,tmp_path)


def test_preparation_blocks_retired_source_via_shared_guard(tmp_path,monkeypatch):
    from scripts import s11_center_path_trial as trial
    from tests.diagnostics.s11_corpus_access import RestrictedCorpusUseError
    monkeypatch.delenv("OIL_TRACKER_SAMPLE3_PURPOSE",raising=False)
    monkeypatch.setattr(trial,"load",lambda path:{"preflight":{"cases":[{"video":"sample/sample3.mp4"}]}})
    with pytest.raises(RestrictedCorpusUseError,match="QUARANTINED"):
        trial.prepare(tmp_path,tmp_path/"must-not-exist")
    assert not (tmp_path/"must-not-exist").exists()


def test_trial_baseline_is_pre_extension_from_non_repo_cwd(tmp_path, monkeypatch):
    from scripts import s11_center_path_trial as trial
    monkeypatch.chdir(tmp_path)
    original = trial.baseline_source()
    current = (trial.ROOT / trial.SOURCE).read_bytes()
    assert current.startswith(original)
    assert len(original) < len(current)
    assert b"def diagnose_center_path_alternatives(" not in original


def test_trial_missing_historical_object_fails_closed(tmp_path, monkeypatch):
    from scripts import s11_center_path_trial as trial
    monkeypatch.setattr(trial, "ROOT", tmp_path)
    with pytest.raises(RuntimeError, match="historical Git object"):
        trial.baseline_source()


def test_trial_rejects_baseline_digest_drift(monkeypatch):
    from scripts import s11_center_path_trial as trial
    monkeypatch.setattr(trial, "BASE_SOURCE_SHA256", "0" * 64)
    with pytest.raises(ValueError, match="baseline source hash mismatch"):
        trial.baseline_source()


def test_trial_checks_frozen_baseline_before_raster_work(tmp_path):
    from scripts import s11_center_path_trial as trial
    from pathlib import Path
    trial.save(tmp_path / "preflight.json", {
        "samples": ["sample4", "sample5", "sample6", "sample7"],
        "candidate_source_sha256": trial.sha(trial.ROOT / trial.SOURCE),
        "runner_sha256": trial.sha(Path(trial.__file__)),
        "inputs": {}, "baseline_source_sha256": "0" * 64,
    })
    with pytest.raises(ValueError, match="Frozen P1 baseline"):
        trial.run(tmp_path, tmp_path)
