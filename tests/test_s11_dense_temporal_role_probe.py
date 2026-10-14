import numpy as np
import pytest
from tests.diagnostics import s11_dense_temporal_role_probe as dto


@pytest.mark.parametrize("image", [None, np.zeros((2, 5), np.uint8),
    np.zeros((5, 5, 3), np.uint8), np.zeros((5, 5), np.int16),
    np.zeros((1500, 1500), np.uint8)])
def test_invalid_input(image):
    with pytest.raises(ValueError):
        dto.ordinal(image)


@pytest.mark.parametrize("n", [2, 3, 13])
def test_static_and_affine_invariance(n):
    rng = np.random.default_rng(17)
    image = rng.integers(10, 70, (31, 29), dtype=np.uint8)
    frames = [image*(1+i % 2)+i for i in range(n)]
    result = dto.measure(frames)
    assert result["frames"] == n
    assert np.nanmax(result["turnover"]) == 0
    assert np.isnan(result["turnover"][0]).all()


@pytest.mark.parametrize("frames", [[], [np.zeros((5, 5), np.uint8)],
    [np.zeros((5, 5), np.uint8), np.zeros((6, 5), np.uint8)]])
def test_frame_contract(frames):
    with pytest.raises(ValueError):
        dto.measure(frames)


def test_independent_integer_enumeration():
    rng = np.random.default_rng(7)
    frames = rng.integers(0, 256, (4, 11, 12), dtype=np.uint8)
    result = dto.measure(frames)["turnover"]
    for y in range(1, 10):
        for x in range(1, 11):
            count = 0
            for t in range(1, 4):
                for dy, dx in dto.OFFSETS:
                    before = int(frames[t-1, y+dy, x+dx])-int(frames[t-1, y, x])
                    after = int(frames[t, y+dy, x+dx])-int(frames[t, y, x])
                    count += np.sign(before) != np.sign(after)
            assert result[y, x] == count/24


@pytest.mark.parametrize("bad", [[[0, 0]], [[3, 3]], [], [[50, 50]]])
def test_censored_patch_not_zero(bad):
    field = dto.measure([np.zeros((20, 20), np.uint8)]*2)["turnover"]
    result = dto.sample_side(field, bad)
    assert result["status"] == "UNAVAILABLE"
    assert result["mean"] is None


def test_orientation_and_complete_population():
    field = np.zeros((40, 30)); field[20:] = 1
    result = dto.paired_score(field, [[15, 14]], [[15, 26]])
    assert result["score"] == 1
    assert dto.paired_score(field, [[15, 26]], [[15, 14]])["score"] == -1
