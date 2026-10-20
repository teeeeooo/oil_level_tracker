"""LBW-1 S0: layer-bottom witness screen on saved rasters (no detector consumer).

Implements the witness frozen in
docs/50-diagnostics/s11/2026-10-20-layer-bottom-witness.md and evaluates it on
the protocol's fixed controls. Two input paths share one evaluation:

- ``sample4``: the existing production analysis (P5 configuration, options OFF)
  with a debug level so frame artifacts exist; target-frame rasters are taken
  from the detector's own artifacts. The tracking fingerprint must equal the
  saved P5 baseline.
- ``bundle``: a saved debug trace (e.g. the Windows ④ bundle), read-only; the
  same rasters come from the record's PNGs.

Both recompute the existing whole-row material features from the same rasters as
a self-check. No detector decision consumes the witness. Not a promoted policy.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import math
from pathlib import Path
import sys

import cv2
import numpy as np

from oil_tracker.adapters.vision.oil_material_path import material_layer_context_features

ROW_NORM = 0.42        # existing row-support normalization
TEXTURE_LIMIT = 0.60   # existing "inside texture" limit
DEPTH_RATIO = 0.16     # middle of the existing terminal depth ratios
BAND = 2               # existing row-support band
MIN_SECTORS = 3        # architecture's distributed-sector count
CHECK_TOLERANCE = 0.03
CHECK_MAX_FAIL = 0.05

# Protocol controls for sample4 (time s, reviewed Y, role). Positives match within
# the P0 C1 band; negatives are exact candidate rows.
SAMPLE4_C1 = 5.2
SAMPLE4_CONTROLS = (
    (40.0, 841.0, 'pos'), (42.0, 839.0, 'pos'), (42.5, 835.0, 'pos'), (44.0, 844.0, 'pos'),
    (49.5, 841.0, 'pos'), (52.0, 833.0, 'pos'),
    (42.0, 805.0, 'neg'), (42.0, 868.0, 'neg'), (40.0, 865.5, 'neg'), (44.0, 822.0, 'neg'),
    (51.0, 862.0, 'neg'), (51.5, 862.0, 'neg'), (52.0, 862.0, 'neg'), (51.0, 861.5, 'neg'),
    (38.0, 880.0, 'report'), (38.0, 882.0, 'report'), (38.0, 887.0, 'report'),
)
SAMPLE4_DECISIVE = (42.0, (835.0, 837.0), (805.0, 868.0))
P5_FINGERPRINT = 'e447626b5717fb5d92f4a895be783658c1b4694eb80eb6f380d032e655a35db1'


def _unit(values):
    return np.clip(values, 0.0, 1.0)


def sector_bounds(effective):
    """Five equal sectors over the effective column range, as the material path."""
    rows, columns = np.where(effective > 0)
    if rows.size < 32:
        return ()
    x0, x1 = int(columns.min()), int(columns.max()) + 1
    width = x1 - x0
    if width < 12:
        return ()
    bounds = []
    for sector in range(5):
        start = x0 + int(round(width * sector / 5.0))
        stop = x0 + int(round(width * (sector + 1) / 5.0))
        if stop - start >= 2:
            bounds.append((start, stop))
    return tuple(bounds)


def _sector_texture(material, visible, start, stop):
    """Normalized, ±BAND-smoothed texture profile; NaN where < 50 % columns visible."""
    window = visible[:, start:stop]
    count = window.sum(axis=1).astype(np.float64)
    total = np.where(window, material[:, start:stop], 0.0).sum(axis=1)
    profile = _unit(np.divide(total, np.maximum(count, 1.0)) / ROW_NORM)
    profile[count < 0.5 * (stop - start)] = np.nan
    smoothed = np.full_like(profile, np.nan)
    for row in range(profile.size):
        band = profile[max(0, row - BAND): row + BAND + 1]
        if np.isfinite(band).any():
            smoothed[row] = np.nanmean(band)
    return smoothed


CLEAN_RUN = 2 * BAND + 1  # LBW-2: shortest clean run the ±BAND smoothing resolves


def same_boundary_tolerance(glass):
    """The tolerance `_cross_representation_support` uses for one boundary."""
    return max(8.0, float(glass.detector_settings.temporal_max_jump_px) * 0.375)


def sector_state(texture, y, depth, *, window=BAND, lower_rows=None):
    """LBW-1 defaults: test rows y±BAND, no texture within `depth` below.

    LBW-2 passes window=same-boundary tolerance and lower_rows=CLEAN_RUN.
    """
    lower_rows = depth if lower_rows is None else lower_rows
    evaluated = []
    for row in range(y - window, y + window + 1):
        if row < 0 or row >= texture.size:
            continue
        upper = texture[max(0, row - depth): row]
        lower = texture[row + 1: row + lower_rows + 1]
        upper, lower = upper[np.isfinite(upper)], lower[np.isfinite(lower)]
        if upper.size < 3 or lower.size < 3:
            continue
        evaluated.append((float(upper.mean()) >= TEXTURE_LIMIT, float(lower.max()) < TEXTURE_LIMIT))
    if not evaluated:
        return 'UNAVAILABLE'
    if any(textured and clean for textured, clean in evaluated):
        return 'TERMINAL'
    if any(textured for textured, _ in evaluated) and not any(clean for _, clean in evaluated):
        return 'INTERIOR'
    return 'OTHER'


def witness(material, effective, glare, local_y, tolerance=None):
    """Layer-bottom witness for one candidate row (material in [0, 1]).

    ``tolerance=None`` is the frozen LBW-1 definition; a tolerance selects LBW-2.
    """
    visible = (effective > 0) & ~(glare > 0)
    depth = max(4, int(round(DEPTH_RATIO * material.shape[0])))
    y = int(round(float(local_y)))
    options = {} if tolerance is None else dict(window=int(round(tolerance)), lower_rows=CLEAN_RUN)
    states = [sector_state(_sector_texture(material, visible, start, stop), y, depth, **options)
              for start, stop in sector_bounds(effective)]
    counts = {name: states.count(name) for name in ('TERMINAL', 'INTERIOR', 'OTHER', 'UNAVAILABLE')}
    if counts['TERMINAL'] >= MIN_SECTORS:
        decision = 'INTERFACE_SUPPORTED'
    elif counts['INTERIOR'] >= MIN_SECTORS:
        decision = 'INTERNAL_OR_ARTIFACT'
    else:
        decision = 'UNRESOLVED'
    return dict(decision=decision, states=states, counts=counts)


def self_check(material, effective, glare, local_y, features):
    """Existing whole-row features recomputed from these rasters vs stored values."""
    expected = {key: features.get(key) for key in ('raw_material_row_support', 'material_terminal_partition_support')}
    if any(value is None for value in expected.values()):
        return None
    recomputed = material_layer_context_features(material, effective, glare, local_y=float(local_y))
    return all(abs(recomputed[key] - float(value)) <= CHECK_TOLERANCE for key, value in expected.items())


def evaluate(rasters, candidates, origin_y, tolerance=None):
    """rasters = (material in [0,1], effective, glare); candidates = trace-style dicts."""
    material, effective, glare = rasters
    rows = []
    for item in candidates:
        if item.get('kind') != 'oil_air' or item.get('canonical_y') is None:
            continue
        local_y = float(item['canonical_y']) - origin_y
        result = witness(material, effective, glare, local_y, tolerance)
        rows.append(dict(idx=item.get('candidate_input_index'), y=float(item['canonical_y']),
                         source=str(item.get('source')), check=self_check(material, effective, glare, local_y,
                                                                          item.get('features') or {}), **result))
    return rows


def origin_from_record(record):
    """Crop origin Y from saved state, else from a candidate's own local_y."""
    foam = (record.get('state') or {}).get('foam_component_diagnostics') or {}
    if foam.get('crop_origin') is not None:
        return float(foam['crop_origin'][1]), 'state'
    offsets = {round(float(item['canonical_y']) - float(item['local_y']), 3)
               for item in record.get('candidates') or []
               if item.get('local_y') is not None and item.get('canonical_y') is not None}
    if len(offsets) == 1:
        return offsets.pop(), 'candidate_local_y'
    raise ValueError(f"crop origin unavailable or inconsistent: {sorted(offsets)}")


def _read_png(path):
    image = cv2.imdecode(np.fromfile(str(path), dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    if image is None:
        raise ValueError(f'cannot decode {path}')
    return image


def rasters_from_bundle(root, record):
    images = record.get('images') or {}
    missing = [key for key in ('foam_combined_evidence', 'effective_mask', 'glare_mask') if key not in images]
    if missing:
        raise ValueError(f"record {record['record_id']} lacks images {missing}")
    load = lambda key: _read_png(Path(root) / 'debug' / images[key])
    return load('foam_combined_evidence').astype(np.float64) / 255.0, load('effective_mask'), load('glare_mask')


def _line(frame, row, role=''):
    counts = row['counts']
    check = {None: '-', True: 'ok', False: 'MISMATCH'}[row['check']]
    return (f"f{frame} | {row['y']:.1f} | {row['idx']} | {row['source'][:20]} | {role} | {row['decision']} | "
            f"T{counts['TERMINAL']} I{counts['INTERIOR']} O{counts['OTHER']} U{counts['UNAVAILABLE']} | {check}")


def _check_valid(rows):
    checked = [row['check'] for row in rows if row['check'] is not None]
    failed = sum(not value for value in checked)
    return failed <= CHECK_MAX_FAIL * max(1, len(checked)), failed, len(checked)


def run_bundle(bundle_path, glass_key, positives, negatives, definition='lbw1'):
    """Windows path: positives/negatives are {frame_index: {candidate_input_index}}."""
    from tests.diagnostics.s11_accum_texture_gate_extract import _load, _records
    bundle, repository, glass = _load(bundle_path, glass_key)
    by_frame = {item.frame_index: item for item in repository.summaries(str(glass.id))}
    frames = sorted(set(positives) | set(negatives))
    tolerance = same_boundary_tolerance(glass) if definition == 'lbw2' else None
    print(f'run_id={bundle.run_id} trace={bundle.debug_trace_level} glass={glass.name} definition={definition} '
          f'tol={tolerance}')
    print('[W] frame | Y | idx | source | role | decision | sectors | self-check')
    all_rows, frame_lines, verdict = [], [], {'pos_frames': 0, 'pos_supported': 0, 'neg_supported': []}
    for frame in frames:
        summary = by_frame.get(frame)
        if summary is None:
            print(f'f{frame} | NOT_CAPTURED')
            continue
        record = next(_records(bundle, [summary]))
        origin, _ = origin_from_record(record)
        rows = evaluate(rasters_from_bundle(bundle.root, record), record.get('candidates') or [], origin, tolerance)
        all_rows += rows
        by_idx = {row['idx']: row for row in rows}
        wanted_pos, wanted_neg = positives.get(frame, set()), negatives.get(frame, set())
        for idx in sorted(wanted_pos | wanted_neg, key=lambda value: by_idx[value]['y'] if value in by_idx else 1e9):
            if idx not in by_idx:
                print(f'f{frame} | - | {idx} | NOT_FOUND')
                continue
            print(_line(frame, by_idx[idx], 'pos' if idx in wanted_pos else 'neg'))
        supported = lambda idx: by_idx.get(idx, {}).get('decision') == 'INTERFACE_SUPPORTED'
        frame_pos = sorted(idx for idx in wanted_pos if supported(idx))
        frame_neg = sorted(idx for idx in wanted_neg if supported(idx))
        frame_lines.append(f'f{frame} | pos supported {frame_pos or "-"} | neg supported {frame_neg or "-"}')
        if wanted_pos:
            verdict['pos_frames'] += 1
            verdict['pos_supported'] += bool(frame_pos)
        verdict['neg_supported'] += [f'f{frame}:idx{idx}' for idx in frame_neg]
    valid, failed, checked = _check_valid(all_rows)
    print('[F] ' + '\n[F] '.join(frame_lines))
    print(f"[S] positive frames supported {verdict['pos_supported']}/{verdict['pos_frames']} | "
          f"negatives supported {len(verdict['neg_supported'])} {' '.join(verdict['neg_supported'])} | "
          f"self-check mismatch {failed}/{checked} ({'valid' if valid else 'INVALID'})")


@contextmanager
def _capture(frames):
    """Capture target-frame rasters from the real detector artifacts."""
    from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
    captured = {}
    original = OpenCvPhaseDetector.detect

    def detect(self, *args, **kwargs):
        detection, artifacts = original(self, *args, **kwargs)
        if artifacts is not None and detection.frame_index in frames:
            images = artifacts.images
            candidates = [dict(kind=c.kind.value, canonical_y=c.y, source=c.source, candidate_input_index=i,
                               local_y=c.features.get('local_y'), features=dict(c.features))
                          for i, c in enumerate(detection.candidates)]
            origin_y, _ = origin_from_record(dict(state=dict(artifacts.state), candidates=candidates))
            captured[detection.frame_index] = dict(
                time=float(detection.time_sec), origin_y=origin_y, candidates=candidates,
                rasters=(images['foam_combined_evidence'].astype(np.float64) / 255.0,
                         images['effective_mask'].copy(), images['glare_mask'].copy()))
        return detection, artifacts

    OpenCvPhaseDetector.detect = detect
    try:
        yield captured
    finally:
        OpenCvPhaseDetector.detect = original


def run_sample4(work, definition='lbw1'):
    from tempfile import TemporaryDirectory
    from tests.diagnostics.s11_report_observability_replay import _session, QUALIFICATION_WINDOWS, _tracking_fingerprint
    from oil_tracker.adapters.storage.jsonl_debug_trace_writer import JsonlDebugTraceWriterFactory
    from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
    from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
    from oil_tracker.application.services.analysis_pipeline import AnalysisPipeline
    from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
    from oil_tracker.domain.session import DebugTraceLevel

    root = Path(__file__).resolve().parents[2]
    work = Path(work).resolve()
    times = sorted({time for time, _, _ in SAMPLE4_CONTROLS})
    frames = {int(round(time * 30)) for time in times}
    with TemporaryDirectory(dir=work) as scratch:
        recipe, session = _session('sample4', root / 'sample' / 'sample4.mp4', Path(scratch),
                                   *QUALIFICATION_WINDOWS['sample4'], run_label='LBW-1 S0', run_note='off')
        session.debug_trace_level = DebugTraceLevel.BASIC
        with _capture(frames) as captured:
            result = AnalysisPipeline(OpenCvVideoReader, OpenCvPhaseDetector(), RecipeValidationService(),
                                      JsonlDebugTraceWriterFactory(Path(scratch))).run(recipe, session)
    assert not result.errors, result.errors
    fingerprint = _tracking_fingerprint(result)
    tolerance = same_boundary_tolerance(next(g for g in recipe.glasses if g.enabled)) if definition == 'lbw2' else None
    print(f'sample4 fingerprint={fingerprint} p5_equal={fingerprint == P5_FINGERPRINT} frames={len(captured)} '
          f'definition={definition} tol={tolerance}')
    if fingerprint != P5_FINGERPRINT:
        print('STOP: input mismatch with the saved P5 baseline')
        return None
    print('[L] frame | Y | idx | source | role | decision | sectors | self-check')
    report, all_rows = [], []
    for frame in sorted(captured):
        item = captured[frame]
        rows = evaluate(item['rasters'], item['candidates'], item['origin_y'], tolerance)
        all_rows += rows
        for time, target, role in SAMPLE4_CONTROLS:
            if int(round(time * 30)) != frame:
                continue
            tolerance = SAMPLE4_C1 if role == 'pos' else 1.0
            for row in rows:
                if abs(row['y'] - target) <= tolerance:
                    print(_line(frame, row, f'{role}{target:g}'))
                    report.append(dict(time=time, target=target, role=role, **{k: row[k] for k in (
                        'idx', 'y', 'source', 'decision', 'counts', 'states', 'check')}))
    pos_times = sorted({time for time, _, role in SAMPLE4_CONTROLS if role == 'pos'})
    supported = [time for time in pos_times if any(r['time'] == time and r['role'] == 'pos'
                                                   and r['decision'] == 'INTERFACE_SUPPORTED' for r in report)]
    negatives = [f"{r['time']}s:Y{r['y']:g}" for r in report
                 if r['role'] == 'neg' and r['decision'] == 'INTERFACE_SUPPORTED']
    time, pos_ys, neg_ys = SAMPLE4_DECISIVE
    decisive = (any(r['time'] == time and r['y'] in pos_ys and r['decision'] == 'INTERFACE_SUPPORTED' for r in report)
                and not any(r['time'] == time and r['y'] in neg_ys and r['decision'] == 'INTERFACE_SUPPORTED'
                            for r in report))
    valid, failed, checked = _check_valid(all_rows)
    summary = dict(definition=definition, fingerprint_equal=True, positive_frames_supported=f'{len(supported)}/{len(pos_times)}',
                   negatives_supported=negatives, decisive_42s=decisive,
                   self_check=dict(mismatch=failed, checked=checked, valid=valid))
    print('[S] ' + json.dumps(summary, ensure_ascii=False))
    (work / f'sample4-s0-{definition}.json').write_text(json.dumps(dict(summary=summary, rows=report), indent=2,
                                                      ensure_ascii=False) + '\n', encoding='utf-8')
    return summary


def _pairs(text):
    from tests.diagnostics.s11_accum_texture_gate_extract import parse_rows
    return parse_rows(text) if text else {}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='mode', required=True)
    local = sub.add_parser('sample4')
    local.add_argument('--work', type=Path, required=True)
    local.add_argument('--definition', choices=('lbw1', 'lbw2'), required=True)
    saved = sub.add_parser('bundle')
    saved.add_argument('--bundle', type=Path, required=True)
    saved.add_argument('--glass', default='Accum')
    saved.add_argument('--pos', required=True, help="frame:idx list, e.g. '16184:10,22'")
    saved.add_argument('--neg', required=True)
    saved.add_argument('--definition', choices=('lbw1', 'lbw2'), required=True)
    args = parser.parse_args()
    if args.mode == 'sample4':
        run_sample4(args.work, args.definition)
    else:
        run_bundle(args.bundle.expanduser().resolve(), args.glass, _pairs(args.pos), _pairs(args.neg),
                   args.definition)


if __name__ == '__main__':
    main()
