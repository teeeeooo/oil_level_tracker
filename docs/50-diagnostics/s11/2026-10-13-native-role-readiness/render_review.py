"""Render an exact saved-fragment review, distinct from the rectangle renderer.

The existing material-reference renderer supports rectangular interior units.
These subjects are unpaired native Canny fragments; no pixels/edges are created.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


def render(root, proposal, output):
    if output.exists():
        raise FileExistsError(output)
    fig, axes = plt.subplots(2, 2, figsize=(12, 11.5), dpi=120)
    colors = {'N1': '#00f0ff', 'N2': '#ff57e3', 'N3': '#00f0ff'}
    for i, view in enumerate(proposal['views']):
        image_path = root / view['source']['path']
        if hashlib.sha256(image_path.read_bytes()).hexdigest() != view['source']['sha256']:
            raise ValueError('review source hash mismatch')
        with Image.open(image_path) as image:
            rgb = np.asarray(image.convert('RGB'))
        ox, oy = view['image_origin_xy']
        x0, y0, x1, y1 = view['display_xyxy']
        if not (ox <= x0 < x1 <= ox + rgb.shape[1] and oy <= y0 < y1 <= oy + rgb.shape[0]):
            raise ValueError('review outside captured pixels')
        crop = rgb[y0-oy:y1-oy, x0-ox:x1-ox]
        for j in range(2):
            ax = axes[i, j]
            ax.imshow(crop, interpolation='nearest', extent=(x0-.5, x1-.5, y1-.5, y0-.5))
            ax.set_title(view['title'] + (' | original pixels' if j == 0 else ' | saved paths'), fontsize=12)
            ax.set_xlabel('Source X'); ax.set_ylabel('Source Y')
        for subject in proposal['subjects']:
            if subject['view_id'] != view['id']:
                continue
            xy = np.asarray(subject['source_path_xy'])
            ax = axes[i, 1]
            ax.plot(xy[:, 0], xy[:, 1], color=colors[subject['id']], linewidth=1.15)
            center = subject['fixed_column_xy']
            label_x, label_y = subject['display_label_xy']
            ax.annotate(subject['id'], xy=center, xytext=(label_x, label_y), fontsize=16,
                        color=colors[subject['id']], weight='bold',
                        arrowprops={'arrowstyle': '->', 'lw': 1, 'color': colors[subject['id']]})
    fig.suptitle('N1 / N2 / N3: what does each highlighted path follow?', fontsize=17, y=.995)
    fig.tight_layout(rect=(0, .025, 1, .975))
    fig.text(.5, .008, 'Saved RGB and native paths; nearest-neighbour display. Colors identify subjects; all roles await review.',
             ha='center', fontsize=10)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('xb') as stream:
        fig.savefig(stream, format='png', metadata={'Software': 'Matplotlib; saved native pixels and fragment coordinates'})
    plt.close(fig)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--proposal', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    render(args.root.resolve(), json.loads(args.proposal.read_text(encoding='utf-8')), args.output)
