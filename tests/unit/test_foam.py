from oil_tracker.adapters.vision.foam_front_detector import detect_bottom_connected_foam
from oil_tracker.adapters.vision.geometry_masks import build_mask_bundle
from oil_tracker.adapters.vision.preprocessing import preprocess
from tests.fixtures.synthetic import disconnected_bubbles_frame, foam_bottom_frame, glass_config


def detect(frame):
    glass = glass_config(); glass.detector_settings.foam_variance_threshold = 50; glass.detector_settings.foam_edge_density_threshold = .03; glass.detector_settings.foam_min_area_ratio = .005
    bundle = build_mask_bundle(frame, glass); pre = preprocess(bundle.crop, bundle.effective_mask, glass.detector_settings)
    return detect_bottom_connected_foam(pre.gray, pre.canny, bundle.effective_mask, glass.detector_settings)


def test_bottom_connected_foam_has_front():
    assert detect(foam_bottom_frame()).candidate is not None


def test_disconnected_bubbles_do_not_define_front():
    assert detect(disconnected_bubbles_frame()).candidate is None
