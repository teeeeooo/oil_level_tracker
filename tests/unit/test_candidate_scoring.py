import numpy as np

from oil_tracker.adapters.vision.candidate_scorer import CandidateScoreContext, score_candidates
from oil_tracker.adapters.vision.preprocessing import PreprocessResult
from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind
from oil_tracker.domain.recipe import DetectorSettings


def context(glare=False):
    h, w = 100, 100
    zeros = np.zeros((h, w), np.uint8); mask = np.full((h, w), 255, np.uint8)
    sobel = zeros.copy(); sobel[50] = 255
    horizontal = zeros.copy(); horizontal[50, 20:80] = 255
    blurred = np.full((h, w), 100, np.uint8); blurred[50:] = 180
    glare_mask = zeros.copy();
    if glare: glare_mask[48:53] = 255
    pre = PreprocessResult(blurred, blurred, blurred, sobel.astype(np.float32), sobel, horizontal, horizontal, glare_mask)
    return CandidateScoreContext(pre, mask, mask, zeros, DetectorSettings(minimum_final_confidence=.1, minimum_horizontal_coverage=.1, minimum_region_contrast=.01))


def test_candidate_scoring_selects_evidenced_row():
    c = BoundaryCandidate("sobel", BoundaryKind.OIL_AIR, 50)
    result = score_candidates([c], context(False))[0]
    assert result.final_score > .1
    assert not result.rejected


def test_glare_penalty_rejects_candidate():
    c = BoundaryCandidate("sobel", BoundaryKind.OIL_AIR, 50)
    result = score_candidates([c], context(True))[0]
    assert result.rejected
    assert result.reject_reason == "glare_overlap"
