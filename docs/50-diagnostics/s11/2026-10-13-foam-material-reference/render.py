"""Render a finite material-reference proposal from unchanged saved RGB pixels.

The earlier position-review renderers freeze horizontal boundary intervals; this
review needs a finite 2-D interior footprint and a clean detail beside its context.
No model, candidate, physical label, enhancement or video decode is involved.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
from PIL import Image


def render(source: Path, overview: list[int], footprint: list[int], label: str, output: Path) -> dict:
    if output.exists():
        raise FileExistsError(output)
    rgb = np.asarray(Image.open(source).convert("RGB"))
    height, width = rgb.shape[:2]
    ox0, oy0, ox1, oy1 = overview
    x0, y0, x1, y1 = footprint
    if not (0 <= ox0 <= x0 < x1 <= ox1 <= width and
            0 <= oy0 <= y0 < y1 <= oy1 <= height):
        raise ValueError("Footprint must lie inside overview and original pixels")
    crop, patch = rgb[oy0:oy1, ox0:ox1], rgb[y0:y1, x0:x1]
    fig = plt.figure(figsize=(9.6, 13.6), dpi=120, facecolor="white")
    fig.suptitle(f"{label} | proposed large-grained Foam reference", fontsize=17, y=.97)
    ax = fig.add_axes([.08, .39, .84, .52])
    ax.imshow(crop, interpolation="nearest", extent=(ox0-.5, ox1-.5, oy1-.5, oy0-.5))
    ax.add_patch(Rectangle((x0-.5, y0-.5), x1-x0, y1-y0, fill=False,
                           color="#00f0ff", linewidth=2))
    ax.annotate(label, xy=((x0+x1-1)/2, y0-.5),
                xytext=((x0+x1-1)/2+45, y0-40), color="#00f0ff",
                fontsize=20, fontweight="bold", ha="center",
                arrowprops={"arrowstyle": "-", "color": "#00f0ff", "lw": 1.5})
    ax.set_xlabel("Source X")
    ax.set_ylabel("Source Y")
    detail = fig.add_axes([.32, .07, .36, .24])
    detail.imshow(patch, interpolation="nearest", extent=(x0-.5, x1-.5, y1-.5, y0-.5))
    detail.set_title(f"{label} | clean original pixels", fontsize=15)
    detail.set_xlabel("Source X")
    detail.set_ylabel("Source Y")
    fig.text(.5, .012, f"{x1-x0} × {y1-y0} native pixels | No enhancement or generated detail",
             ha="center", fontsize=12)
    with output.open("xb") as stream:
        fig.savefig(stream, format="png", dpi=120,
                    metadata={"Software": "Matplotlib; original RGB, nearest-neighbour display"})
    plt.close(fig)
    return {"source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "source_shape": list(rgb.shape), "overview_xyxy_half_open": overview,
            "footprint_xyxy_half_open": footprint, "footprint_shape": list(patch.shape),
            "footprint_rgb_sha256": hashlib.sha256(patch.tobytes()).hexdigest(),
            "overview_rgb_sha256": hashlib.sha256(crop.tobytes()).hexdigest(),
            "display_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
            "display_bytes": output.stat().st_size, "model_calls": 0, "video_decode": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--overview", required=True, type=int, nargs=4)
    parser.add_argument("--footprint", required=True, type=int, nargs=4)
    parser.add_argument("--label", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(render(args.source, args.overview, args.footprint, args.label, args.output)))
