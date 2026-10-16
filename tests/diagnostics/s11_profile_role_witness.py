"""PWC-1 image-model preferences; no physical labels or production authority."""
from __future__ import annotations
from hashlib import sha256
import math
import numpy as np

MODELS = ('affine', 'corner', 'jump', 'separate_slopes')
ARMS = {'H1': 'jump', 'H2': 'separate_slopes'}
EPS = 1e-12  # normalized-MSE arithmetic equality, not a fitted operating point


def require(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def design(z: np.ndarray, model: str) -> np.ndarray:
    require(model in MODELS, 'unknown profile model')
    columns = [np.ones_like(z), z]
    if model in {'corner', 'separate_slopes'}:
        columns.append(np.abs(z))
    if model in {'jump', 'separate_slopes'}:
        columns.append(np.sign(z))
    return np.column_stack(columns)


def preference(errors: dict[str, list[float]], arm: str) -> str:
    require(arm in ARMS, 'unknown hypothesis')
    target = ARMS[arm]
    require(set(errors) == set(MODELS), 'incomplete model errors')
    require(all(len(v) == 2 and all(math.isfinite(x) and x >= 0 for x in v)
                for v in errors.values()), 'invalid prediction errors')
    def beats(a: str, b: str) -> bool:
        return all(x + EPS < y for x, y in zip(errors[a], errors[b], strict=True))
    if beats(target, 'affine') and beats(target, 'corner'):
        return 'JUMP_PREFERRED'
    if beats('corner', 'affine') and beats('corner', target):
        return 'CORNER_PREFERRED'
    return 'UNKNOWN'


def score_profile(rows: np.ndarray, values: np.ndarray, y: float,
                  length: int) -> dict:
    require(rows.ndim == values.ndim == 1 and len(rows) == len(values), 'invalid profile')
    require(np.all(np.isfinite(values)) and np.all(np.isfinite(rows)), 'nonfinite profile')
    z = (rows - y) / length
    errors, coefficients = {}, {}
    for model in MODELS:
        matrix = design(z, model)
        errors[model], coefficients[model] = [], []
        for parity in (0, 1):
            train = rows.astype(int) % 2 == parity
            test = ~train
            require(train.any() and test.any(), 'empty prediction fold')
            beta, _, rank, _ = np.linalg.lstsq(matrix[train], values[train], rcond=None)
            require(rank == matrix.shape[1], 'rank-deficient profile')
            error = float(np.mean((values[test] - matrix[test] @ beta) ** 2))
            errors[model].append(error)
            coefficients[model].append(beta.tolist())
    return {'rows': rows.tolist(), 'values': values.tolist(),
            'errors': errors, 'coefficients': coefficients}


def observe(gray: np.ndarray, visible: np.ndarray, *, origin: tuple[int, int],
            frame: int, index: int, source: str, y: float) -> dict:
    require(gray.ndim == 2 and gray.dtype == np.uint8, 'uint8 gray required')
    require(visible.shape == gray.shape and visible.dtype == bool, 'invalid visibility')
    require(math.isfinite(y) and type(index) is int and index >= 0, 'invalid candidate')
    height, width = gray.shape
    band = max(3, min(12, int(round(height * 0.01))))
    length = 3 * band + 1
    local = y - origin[1]
    rows = np.arange(math.floor(local) - length, math.ceil(local) + length + 1)
    rows = rows[np.abs(rows - local) >= 2]
    result = {'frame': frame, 'index': index, 'source': source, 'y': y,
              'origin': list(origin), 'shape': list(gray.shape), 'band': band,
              'length': length, 'sectors': [], 'errors': None,
              'preferences': {a: 'UNKNOWN' for a in ARMS},
              'status': 'UNAVAILABLE_CROP', 'native_path_created': False}
    if rows.min() < 0 or rows.max() >= height:
        return result
    for sector in range(5):
        x0, x1 = width * sector // 5, width * (sector + 1) // 5
        columns = np.flatnonzero(np.all(visible[rows, x0:x1], axis=0)) + x0
        if len(columns) < 2 or len(columns) / (x1 - x0) < 0.5:
            continue
        values = gray[np.ix_(rows, columns)].mean(axis=1) / 255.0
        scored = score_profile(rows + origin[1], values, y, length)
        result['sectors'].append({'sector': sector, 'columns': columns.tolist(), **scored})
    result['status'] = 'UNAVAILABLE_SUPPORT'
    if not result['sectors']:
        return result
    errors = {m: np.mean([s['errors'][m] for s in result['sectors']], axis=0).tolist()
              for m in MODELS}
    result.update(status='MEASURED', errors=errors,
                  preferences={a: preference(errors, a) for a in ARMS})
    return result


def decision_controls(measurements: list[dict], arm: str) -> list[dict]:
    """Adapter to diagnostic seams. No human-review argument exists here."""
    require(arm in ARMS, 'unknown hypothesis')
    controls = []
    seen = set()
    for row in measurements:
        key = (row['frame'], row['index'])
        require(key not in seen, 'duplicate exact candidate')
        seen.add(key)
        role = row['preferences'][arm]
        if role == 'UNKNOWN':
            continue
        controls.append({'id': f'PIXEL-{arm}-{key[0]}-{key[1]}',
                         'frame': key[0], 'index': key[1], 'source': row['source'], 'y': row['y'],
                         'review_label': 'OPPOSED' if role == 'CORNER_PREFERRED' else 'ACCEPTED',
                         'physical_positive': role == 'JUMP_PREFERRED', 'practical_only': False,
                         'label_basis': 'DIAGNOSTIC_PIXEL_MODEL_PREFERENCE_NOT_REVIEW_OR_PHYSICAL_TRUTH'})
    return controls
