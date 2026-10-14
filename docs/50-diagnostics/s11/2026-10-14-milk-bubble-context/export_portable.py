"""Package the frozen milk review without any external asset dependencies."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def uri(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    if out.exists():
        raise ValueError("output already exists")
    base = Path(__file__).resolve().parent
    verification = json.loads((base / "verification.json").read_text(encoding="utf-8"))
    root = base.parents[3]
    for name, digest in verification["pins"].items():
        if sha(root / name) != digest:
            raise ValueError(f"frozen input changed: {name}")
    plan = json.loads((base / "plan.json").read_text(encoding="utf-8"))
    locator = base.parent / "2026-10-14-native-milk-review/location.png"
    if sha(locator) != plan["inputs"][str(locator.relative_to(root))]:
        raise ValueError("locator changed")
    atlas = cv2.imread(str(base / "native-atlas.png"))
    readout = json.loads((base / "readout.json").read_text(encoding="utf-8"))
    # Same three anchor buttons as the frozen viewer. No new crop or time window.
    offsets = [0, 12, 24]
    tiles = []
    for i in offsets:
        item = readout["frames"][i]
        x0, y0, x1, y1 = item["atlas_xyxy"]
        crop = atlas[y0:y1, x0:x1]
        if hashlib.sha256(crop.tobytes()).hexdigest() != item["crop_bgr_sha256"]:
            raise ValueError("atlas crop changed")
        enlarged = crop.repeat(2, axis=0).repeat(2, axis=1)
        tile = np.full((enlarged.shape[0] + 56, enlarged.shape[1], 3), 248, np.uint8)
        tile[56:] = enlarged
        title = f"f{item['frame_index']} / {item['timestamp_sec']:.6f}s"
        cv2.putText(tile, title, (12, 34), cv2.FONT_HERSHEY_SIMPLEX, .75, (35, 35, 35), 1, cv2.LINE_AA)
        tiles.append(tile)
    out.mkdir(parents=True)
    strip = out / "remote-contact-sheet.png"
    if not cv2.imwrite(str(strip), np.concatenate(tiles, axis=1)):
        raise ValueError("contact sheet write failed")
    saved = cv2.imread(str(strip))
    for column, i in enumerate(offsets):
        item = readout["frames"][i]
        pixels = saved[56::2, column * 520:(column + 1) * 520:2]
        if hashlib.sha256(pixels.tobytes()).hexdigest() != item["crop_bgr_sha256"]:
            raise ValueError("contact sheet pixels differ")

    html = (base / "review.html").read_text(encoding="utf-8")
    replacements = {
        'src="../2026-10-14-native-milk-review/location.png"': f'src="{uri(locator)}"',
        "atlas.src='native-atlas.png'": f"atlas.src='{uri(base / 'native-atlas.png')}'",
        '<p><a href="../2026-10-14-milk-bubble-context.md">검토 범위·판정 기록</a></p>':
            '<p id="scope">검토 범위: 기존 1039–1063 프레임, 같은 고정 영역. '
            '마지막 프레임의 687만 큰 거품의 상단으로 확인됐습니다. 시간상 동일 개체 여부는 미판정입니다.</p>',
    }
    for old, new in replacements.items():
        if html.count(old) != 1:
            raise ValueError(f"unexpected viewer template: {old}")
        html = html.replace(old, new)
    fallback = ('<section style="margin-top:24px"><p>처음 · 중간 · 마지막 프레임 비교 '
                '(재생이 지원되지 않는 환경에서도 표시됩니다)</p>'
                f'<img id="static-comparison" src="{uri(strip)}" '
                'style="width:100%;max-width:1560px;image-rendering:pixelated" '
                'alt="1039, 1051, 1063 프레임의 동일 영역 원본 비교"></section>')
    html = html.replace("<script>\n", fallback + "\n<script>\n", 1)
    html = html.replace("<title>687 거품 주변 — 원본 25프레임</title>",
                        "<title>687 거품 주변 — 원격용 단일 파일</title>")
    target = out / "review-standalone.html"
    target.write_text(html, encoding="utf-8")
    for name, digest in verification["pins"].items():
        if sha(root / name) != digest:
            raise ValueError(f"frozen input changed during export: {name}")
    receipt = {
        "schema": "s11-milk-context-portable-export-v1",
        "source_viewer_sha256": sha(base / "review.html"),
        "atlas_sha256": sha(base / "native-atlas.png"),
        "locator_sha256": sha(locator), "exporter_sha256": sha(Path(__file__)),
        "outputs": {p.name: {"sha256": sha(p), "bytes": p.stat().st_size}
                    for p in (target, strip)},
        "embedded_images": 3, "contact_sheet_frames": [1039, 1051, 1063],
        "contact_sheet_scale": 2, "contact_sheet_pixels_equal": True,
        "frozen_inputs_preserved": True, "new_video_decodes": 0,
        "new_physical_labels": 0,
    }
    (out / "remote-export.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"outputs": receipt["outputs"], "embedded_images": 3}))


if __name__ == "__main__":
    main()
