from dataclasses import asdict, FrozenInstanceError, replace
import json
from types import SimpleNamespace

import numpy as np
import pytest

from oil_tracker.adapters.vision.oil_interface_diagnostics import measure_oil_interfaces
from oil_tracker.adapters.vision.oil_interface_witness import MAX_PEAKS, SIGMA_FLOOR
from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind
from tests.unit.test_oil_interface_diagnostics import _native_path
from tests.diagnostics.s11_interface_witness_probe import _candidate_measurement


def measure(gray, *, paths=None, origin=(0, 0), candidates=None, **kwargs):
    sink = []
    args = dict(gray=gray, effective_mask=np.ones_like(gray), glare_mask=np.zeros_like(gray),
                material_map=np.ones_like(gray, dtype=float), static_map=None,
                crop_origin=origin, frame_index=27, material_paths=paths)
    args.update(kwargs)
    candidates = candidates or [BoundaryCandidate("test", BoundaryKind.OIL_AIR, 100+origin[1])]
    old = measure_oil_interfaces(candidates, **args)
    new = measure_oil_interfaces(candidates, **args, witness_sink=sink,
                                 glass_id="test-glass", canny=np.zeros_like(gray))
    assert old == new
    json.dumps(asdict(sink[0]), allow_nan=False)
    return sink[0]


def test_step_and_stripe_have_explicit_context_without_deciding_identity():
    step = np.full((200, 200), 180, dtype=np.uint8); step[100:] = 80
    stripe = np.full_like(step, 180); stripe[100:106] = 80
    a,b = measure(step),measure(stripe)
    for w in (a,b):
        assert w.observability.status == "NOT_EVALUATED"
        assert w.candidates[0].decision == "NOT_EVALUATED"
        assert w.candidates[0].contour.localization_uncertainty_px is None
        with pytest.raises(FrozenInstanceError):w.candidates[0].canonical_y = 5
    sa,sb = [w.candidates[0].sectors[2].centers[0].scales[0] for w in (a,b)]
    assert sa.signed_delta == pytest.approx(-100/255)
    assert sb.signed_delta == pytest.approx(sa.signed_delta)
    assert sa.normalization_denominator == pytest.approx(SIGMA_FLOOR)
    assert sa.normalized_delta == pytest.approx(-100)
    assert sa.bands[3].gray_mean - sa.bands[2].gray_mean == pytest.approx(-100/255)
    assert sb.bands[3].gray_mean - sb.bands[2].gray_mean == pytest.approx(0)


@pytest.mark.parametrize("shift", [-24, 24])
def test_real_curve_translation_and_polarity_reversal_preserve_local_peak_geometry(shift):
    path = _native_path(); candidate = BoundaryCandidate("material_path", BoundaryKind.OIL_AIR, 173)
    def render(p, invert=False):
        gray=np.full((200,200), 180, dtype=np.uint8)
        for s in p.evidence.diagnostic_samples:gray[s.local_y:,s.start_x:s.stop_x]=80
        return 255-gray if invert else gray
    moved = replace(path, candidate_y=173+shift, evidence=replace(path.evidence,
        diagnostic_samples=tuple(replace(s,local_y=s.local_y+shift) for s in path.evidence.diagnostic_samples)))
    a=measure(render(path), paths={0:path}, origin=(11,73), candidates=[candidate])
    b=measure(render(moved,True), paths={0:moved}, origin=(11,73), candidates=[replace(candidate,y=173+shift)])
    for sa,sb in zip(a.candidates[0].sectors,b.candidates[0].sectors):
        aa,bb=sa.centers[0].scales[0],sb.centers[0].scales[0]
        assert bb.peak_hull_source_y == tuple(y+shift for y in aa.peak_hull_source_y)
        assert bb.signed_delta == pytest.approx(-aa.signed_delta)
        assert aa.localization_status == bb.localization_status == "single_peak"
    assert a.candidates[0].contour.sector_source_y_range == (165,181)
    assert a.candidates[0].contour.localization_uncertainty_px is None


def test_flat_profile_no_peak_and_bounded_competing_plateaus():
    flat=measure(np.full((200,200),120,dtype=np.uint8))
    assert flat.candidates[0].sectors[0].centers[0].scales[0].localization_status == "no_peak"
    stripe=np.full((200,200),80,dtype=np.uint8)
    for y in (94,98,102,106):stripe[y:y+2]=180
    w=measure(stripe)
    scale=w.candidates[0].sectors[2].centers[0].scales[-1]
    assert scale.peak_count_before_truncation > MAX_PEAKS
    assert len(scale.peaks)==MAX_PEAKS
    assert scale.peaks_truncated
    assert scale.localization_status=="truncated"
    assert list(p.source_y for p in scale.peaks)==sorted(p.source_y for p in scale.peaks)
    assert all(p.plateau_source_y_range[1]>p.plateau_source_y_range[0] for p in scale.peaks)


@pytest.mark.parametrize("missing",["mask","glare","material","static","crop"])
def test_missing_channels_remain_explicit_and_finite(missing):
    gray=np.full((200,200),180,dtype=np.uint8);gray[100:]=80
    args={}
    if missing=="mask":args['effective_mask']=np.zeros_like(gray)
    if missing=="glare":args['glare_mask']=np.ones_like(gray)
    if missing=="material":args['material_map']=np.full_like(gray,np.nan,dtype=float)
    if missing=="crop":args['candidates']=[BoundaryCandidate('test',BoundaryKind.OIL_AIR,0.5)]
    w=measure(gray,**args);band=w.candidates[0].sectors[0].centers[0].scales[0].bands[0]
    if missing in {'mask','glare','crop'}:
        assert band.gray_mean is None
        assert band.normal_alignment is None
    if missing=='material':assert band.material_mean is None and not band.material_available
    if missing=='static':assert band.static_overlap is None and not band.static_available
    if missing=='mask':assert w.observability.visible_fraction is None
    if missing=='crop':assert band.clipped_local_y_range != band.local_y_range


def test_rejected_duplicate_fractional_identity_and_permutation():
    gray=np.full((200,200),180,dtype=np.uint8);gray[100:]=80
    candidates=[BoundaryCandidate('same',BoundaryKind.OIL_AIR,173.5,rejected=True),
                BoundaryCandidate('same',BoundaryKind.OIL_AIR,173.5),
                BoundaryCandidate('outside',BoundaryKind.OIL_AIR,float('inf'))]
    w=measure(gray,candidates=candidates,origin=(11,73))
    assert [c.candidate_input_index for c in w.candidates]==[0,1,2]
    assert w.candidates[0].rejected and not w.candidates[1].rejected
    assert w.candidates[0].sectors[0].centers[0].sampling_center_local_y==101
    assert w.candidates[2].canonical_y is None and not w.candidates[2].sectors
    swapped=measure(gray,candidates=candidates[::-1],origin=(11,73))
    assert swapped.candidates[-1].rejected
    assert swapped.candidates[-1].sectors==w.candidates[0].sectors


def test_probe_missing_material_conflict_is_not_zero():
    diagnostic={'canonical_y':1,'candidate_input_index':0,'sectors':[]}
    candidate=SimpleNamespace(features={},penalties={},source='test',rejected=False,final_score=0)
    assert _candidate_measurement(diagnostic,candidate,1).material_texture_conflict is None
    candidate.features['material_texture_conflict']=0.0
    assert _candidate_measurement(diagnostic,candidate,1).material_texture_conflict==0.0


def test_debug_none_never_captures_witness(monkeypatch):
    from oil_tracker.adapters.vision import oil_interface_witness as owner
    from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
    from tests.test_oil_detector_integration import glass, oil_frame
    def forbidden(*args, **kwargs):
        raise AssertionError("witness invoked with debug disabled")
    monkeypatch.setattr(owner, "build_interface_witness", forbidden)
    detection, artifacts = OpenCvPhaseDetector().detect(oil_frame(130), glass(), 1, 0.5, debug=False)
    assert artifacts is None
    assert "oil_interface_witness" not in detection.debug_metrics


def test_gradient_normal_alignment_and_saturation_have_defined_denominators():
    horizontal = np.zeros((200,200), dtype=np.uint8); horizontal[100:] = 255
    w = measure(horizontal)
    assert w.observability.saturation_fraction == 1
    # The excluded center edge does not invent alignment in flat side bands.
    band = w.candidates[0].sectors[2].centers[0].scales[0].bands[0]
    assert band.normal_alignment is None
    assert band.gradient_valid_pixel_count > 0
    vertical = np.tile(np.arange(200,dtype=np.uint8), (200,1))
    v = measure(vertical).candidates[0].sectors[2].centers[0].scales[0].bands[0]
    assert v.gradient_magnitude == pytest.approx(1/255)
    assert v.normal_alignment == pytest.approx(0)
