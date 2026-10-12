"""Source-only position review figure; predictions are deliberately not loaded."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    base = Path(__file__).resolve().parent
    source = base / 'native-at-50.png'
    expected = '280b7869a81edfde722fafc85017fdf45dd6e799978cb6c46b7b9769249a635b'
    assert hashlib.sha256(source.read_bytes()).hexdigest() == expected
    frame = cv2.imread(str(source))
    x0, y0, x1, y1 = 454, 244, 704, 478
    zoom = 3
    crop = cv2.resize(frame[y0:y1, x0:x1], None, fx=zoom, fy=zoom,
                      interpolation=cv2.INTER_NEAREST)
    canvas = np.full((crop.shape[0] + 122, crop.shape[1] + 250, 3), 25, np.uint8)
    canvas[56:56 + crop.shape[0], :crop.shape[1]] = crop
    label = lambda text, xy, color=(240, 240, 240), size=.62: cv2.putText(
        canvas, text, xy, cv2.FONT_HERSHEY_SIMPLEX, size, color, 1, cv2.LINE_AA)
    label('Source only: f1499 at 50.016633 s | 3x nearest-neighbour view', (10, 22), size=.58)
    label('Dashed vertical guide: source X=578', (10, 45), size=.58)
    center = (578 - x0) * zoom
    for yy in range(56, 56 + crop.shape[0], 20):
        cv2.line(canvas, (center, yy), (center, min(yy + 7, 55 + crop.shape[0])),
                 (235, 235, 235), 1)
    intervals = [('A', 'Foam upper', 323, 338, (255, 220, 30)),
                 ('B', 'Oil upper', 421, 435, (50, 165, 255))]
    for name, role, lo, hi, color in intervals:
        top, bottom = 56 + (lo - y0) * zoom, 56 + (hi - y0 + 1) * zoom - 1
        # Brackets near the fixed column; no colored fill hides source pixels.
        left, right = center - 39, center + 39
        cv2.rectangle(canvas, (left, top), (right, bottom), color, 2)
        cv2.line(canvas, (right + 4, (top + bottom) // 2),
                 (crop.shape[1] + 7, (top + bottom) // 2), color, 1)
        label(f'{name}: {role}', (crop.shape[1] + 13, (top + bottom) // 2 - 7), color)
        label(f'Y {lo}..{hi}', (crop.shape[1] + 13, (top + bottom) // 2 + 20), color)
    label('Proposed ranges, not exact Y or detector predictions.', (10, canvas.shape[0] - 37))
    label('Review only at the dashed center; roles are already confirmed.', (10, canvas.shape[0] - 13), size=.58)
    args.output.mkdir(parents=True, exist_ok=False)
    image = args.output / 'position-review.png'
    assert cv2.imwrite(str(image), canvas)
    request = {
        'schema': 's11-public-source-position-review-v1', 'status': 'PENDING_USER_JUDGMENT',
        'source_image_sha256': expected, 'frame_index': 1499,
        'timestamp_sec': 50.01663333333334, 'source_x': 578,
        'figure': {'file': image.name, 'sha256': hashlib.sha256(image.read_bytes()).hexdigest(),
                   'crop_source_xyxy': [x0, y0, x1, y1], 'scale': zoom,
                   'interpolation': 'nearest', 'source_origin_in_figure': [0, 56]},
        'proposed_ranges': [
            {'id': name, 'role': role, 'source_rows_inclusive': [lo, hi],
             'source_y_cell_bounds': [lo - .5, hi + .5]}
            for name, role, lo, hi, _ in intervals],
        'exposure': 'Prepared after baseline inspection. Agent-proposed source ranges are exposed adjudication, not blind holdout or exact truth. The figure reads source pixels only; no detector outputs or scores are drawn.',
        'question': '중앙 점선에서 A 범위가 Foam 상단, B 범위가 Oil 상단을 각각 포함하나요? 역할은 이미 확인됐으며, 이번 질문은 다음 실험에서 사용할 위치 범위를 고정하기 위한 것입니다. 정확한 한 픽셀을 고를 필요는 없습니다.',
        'answer_verbatim': None,
        'scope': 'Only this native frame and fixed source column; no unique edge, neighboring-frame truth or resampled-point accuracy. Do not score proposed ranges as human-confirmed before a reply.',
        'renderer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (args.output / 'position-review.json').write_text(json.dumps(request, ensure_ascii=False, indent=2) + '\n')
    print(image)


if __name__ == '__main__':
    main()
