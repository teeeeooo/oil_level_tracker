"""Retired-after-run CR-1 diagnostic entry; never imported by the application.

Use only with the frozen preflight, readiness pins and saved-input preparation.
Full/local comparisons use the same native footprint, common strips and scale.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import socket
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
WORKSPACE = ROOT / 'sample/output/s11-cr1-workspace'
sys.dont_write_bytecode = True


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, allow_nan=False, separators=(',', ':'))
        stream.write('\n')


def allocated(root):
    return sum(p.lstat().st_blocks * 512 for p in root.rglob('*'))


def sandbox():
    for key, suffix in [('TMPDIR', 'tmp'), ('TORCH_HOME', 'torch'),
                        ('XDG_CACHE_HOME', 'xdg'), ('HF_HOME', 'huggingface')]:
        path = WORKSPACE / 'cache' / suffix
        path.mkdir(parents=True, exist_ok=True)
        os.environ[key] = str(path)
    os.environ.update(PYTHONDONTWRITEBYTECODE='1', XFORMERS_DISABLED='1',
                      HF_HUB_OFFLINE='1', OMP_NUM_THREADS='2', MKL_NUM_THREADS='2')
    denied = []

    def inside(path):
        if isinstance(path, (str, bytes, os.PathLike)):
            return Path(os.fsdecode(path)).resolve().is_relative_to(WORKSPACE)
        return True  # already-open descriptors, e.g. stdout

    def audit(event, args):
        if event in ('socket.connect', 'socket.getaddrinfo', 'socket.bind'):
            denied.append(event)
            raise PermissionError('offline CR-1 runtime')
        paths = []
        if event == 'open':
            path, mode, flags = args
            if flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
                paths = [path]
        elif event in ('os.mkdir', 'os.remove', 'os.rmdir'):
            paths = [args[0]]
        elif event in ('os.rename', 'os.link', 'os.symlink'):
            paths = list(args[:2])
        if any(not inside(p) for p in paths):
            denied.append(event)
            raise PermissionError('write outside CR-1 workspace')

    sys.addaudithook(audit)
    try:
        socket.getaddrinfo('example.invalid', 443)
        raise AssertionError('network guard absent')
    except PermissionError:
        pass
    try:
        (ROOT / 'cr1-must-not-be-created.tmp').write_text('blocked')
        raise AssertionError('write guard absent')
    except PermissionError:
        pass
    assert not (ROOT / 'cr1-must-not-be-created.tmp').exists()
    test = WORKSPACE / 'cache/tmp/guard-smoke.tmp'
    test.write_text('allowed')
    test.unlink()
    return denied


def unit(value):
    if not np.isfinite(value).all():
        return None
    norm = float(np.linalg.norm(value))
    return value / norm if norm > 1e-12 else None


def descriptor(tokens, upper, lower):
    if upper is None or lower is None:
        return None
    u, v = unit(upper @ tokens), unit(lower @ tokens)
    if u is None or v is None:
        return None
    difference = unit(u - v)
    return None if difference is None else unit(np.concatenate([u, v, difference]))


def rank(query, references, required=2):
    if query is None or len(references) < required or any(v is None for v in references.values()):
        return dict(status='UNAVAILABLE', preference=None, scores={})
    scores = {k: float(query @ value) for k, value in references.items()}
    if not all(math.isfinite(v) for v in scores.values()):
        return dict(status='UNAVAILABLE', preference=None, scores={})
    ordered = sorted(scores, key=lambda k: (-scores[k], k))
    tied = scores[ordered[0]] - scores[ordered[1]] <= 1e-6
    return dict(status='TIE' if tied else 'MEASURED', preference=None if tied else ordered[0],
                scores=scores, top_margin=scores[ordered[0]] - scores[ordered[1]])


def local_xy(source_xy, origin=(543, 798)):
    return tuple(int(a - b) for a, b in zip(source_xy, origin))


def common_columns(contexts):
    columns = []
    for mask, (x, y) in contexts:
        if x - 12 < 0 or y - 12 < 0 or x + 12 >= 104 or y + 12 >= 104:
            return []
    offsets = list(range(-12, -1)) + list(range(2, 13))
    for dx in range(-12, 13):
        if all(all(mask[y + dy, x + dx] for dy in offsets) for mask, (x, y) in contexts):
            columns.append(dx)
    return columns if len(columns) >= 8 else []


def weights(xy, columns, rows):
    if not columns:
        return None
    result = np.zeros(256, dtype=np.float64)
    for dy in rows:
        for dx in columns:
            gx, gy = [min(15., max(0., (p + 0.5) * (224 / 104) / 14 - 0.5))
                      for p in (xy[0] + dx, xy[1] + dy)]
            ix, iy = math.floor(gx), math.floor(gy)
            ax, ay = gx - ix, gy - iy
            for xx, wx in [(ix, 1 - ax), (min(ix + 1, 15), ax)]:
                for yy, wy in [(iy, 1 - ay), (min(iy + 1, 15), ay)]:
                    result[yy * 16 + xx] += wx * wy / (len(rows) * len(columns))
    return result


def strips(xy, columns):
    return weights(xy, columns, range(-12, -1)), weights(xy, columns, range(2, 13))


def weight_record(xy, columns):
    upper, lower = strips(xy, columns)
    if upper is None:
        return dict(status='UNAVAILABLE')
    return dict(upper=[[int(i), float(upper[i])] for i in np.flatnonzero(upper)],
                lower=[[int(i), float(lower[i])] for i in np.flatnonzero(lower)],
                overlap_mass=float(np.minimum(upper, lower).sum()),
                shared_token_count=int(np.count_nonzero((upper > 0) & (lower > 0))))


def checks():
    # Independent analytic coordinate field: bilinear interpolation reproduces x,y.
    xgrid = np.tile(np.arange(16), 16)
    ygrid = np.repeat(np.arange(16), 16)
    w = weights((52, 52), [-1, 0, 1], [0])
    expected = 52.5 * 224 / 104 / 14 - 0.5
    assert abs(w.sum() - 1) < 1e-12
    assert abs(w @ xgrid - expected) < 1e-12 and abs(w @ ygrid - expected) < 1e-12
    assert local_xy((595, 841)) == local_xy((1595, 1841), (1543, 1798))
    visible = np.ones((104, 104), dtype=bool)
    assert len(common_columns([(visible, (52, 52))])) == 25
    assert not common_columns([(visible, (3, 52))])
    visible[:, :52] = False
    assert common_columns([(visible, (52, 52))]) == list(range(13))
    visible[:] = False
    assert not common_columns([(visible, (52, 52))])
    u, v = strips((52, 52), list(range(-12, 13)))
    # Identical pooled rows, zero/nonfinite and genuine unequal vectors.
    assert descriptor(np.zeros((256, 2)), u, v) is None
    assert descriptor(np.full((256, 2), np.nan), u, v) is None
    assert descriptor(np.ones((256, 2)), u, v) is None
    d = descriptor(np.column_stack([np.ones(256), ygrid]), u, v)
    assert d is not None and abs(np.linalg.norm(d) - 1) < 1e-12
    assert rank(d, {'a': d, 'b': d})['status'] == 'TIE'
    assert rank(d, {'a': d})['status'] == 'UNAVAILABLE'
    assert rank(d, {'a': d, 'b': None})['status'] == 'UNAVAILABLE'
    assert rank(d, {'a': d, 'b': -d})['preference'] == 'a'
    return dict(status='PASS', checks=['analytic_bilinear_coordinates', 'weight_mass',
        'origin_translation', 'complete_crop', 'common_mask_columns', 'zero_nonfinite_equal_sides',
        'unit_descriptor', 'copied_tie', 'missing_reference', 'known_cosine_order'])


class Encoder:
    def __init__(self, limits):
        started = time.monotonic()
        import torch
        self.torch = torch
        torch.set_num_threads(2)
        torch.set_num_interop_threads(2)
        torch.manual_seed(0)
        torch.use_deterministic_algorithms(True)
        sys.path.insert(0, str(WORKSPACE / 'models/dinov2-source'))
        from dinov2.hub.backbones import dinov2_vits14
        self.model = dinov2_vits14(pretrained=False)
        state = torch.load(WORKSPACE / 'models/dinov2_vits14_pretrain.pth',
                           map_location='cpu', weights_only=True)
        self.model.load_state_dict(state, strict=True)
        del state
        self.model.eval().float().cpu()
        self.limits = limits
        self.times = []
        self.load_seconds = time.monotonic() - started
        self.version = torch.__version__
        self.global_full = {}  # at most one 256x384 map per saved frame; never retained
        self.local_references = {}  # three fixed exemplars only

    def encode(self, rgb, visible, xy, mode):
        torch = self.torch
        if len(self.times) >= self.limits['max_forward_calls']:
            raise RuntimeError('forward budget exceeded')
        started = time.monotonic()
        mean = np.array([.485, .456, .406], dtype=np.float32)
        pixels = rgb.astype(np.float32) / 255
        mask = visible.copy()
        if mode == 'local':
            mask[:] = False
            x, y = xy
            mask[y-12:y+13, x-12:x+13] = visible[y-12:y+13, x-12:x+13]
        pixels[~mask] = mean
        tensor = torch.from_numpy(pixels.transpose(2, 0, 1).copy())[None]
        tensor = torch.nn.functional.interpolate(tensor, size=(224, 224), mode='bilinear',
                                                 align_corners=False, antialias=True)
        tensor = (tensor - torch.tensor(mean)[None, :, None, None]) / torch.tensor(
            [.229, .224, .225])[None, :, None, None]
        with torch.inference_mode():
            result = self.model.forward_features(tensor)['x_norm_patchtokens'][0].numpy().copy()
        duration = time.monotonic() - started
        self.times.append(duration)
        assert result.shape == (256, 384) and np.isfinite(result).all()
        if duration > self.limits['forward_seconds_limit']:
            raise RuntimeError('forward time budget exceeded')
        if rss() > self.limits['peak_rss_bytes_limit']:
            raise RuntimeError('RSS budget exceeded')
        return result

    def saved(self, images, masks, frame, xy, mode, reference=False):
        key = (frame, xy)
        cache = self.global_full if mode == 'full' else self.local_references
        cache_key = frame if mode == 'full' else key
        if (mode == 'full' or reference) and cache_key in cache:
            return cache[cache_key]
        value = self.encode(images[frame], masks[str(frame)], xy, mode)
        if mode == 'full' or reference:
            cache[cache_key] = value
        return value


def rss():
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return value if sys.platform == 'darwin' else value * 1024


def synthetic(encoder):
    yy, xx = np.indices((104, 104))
    a = np.stack([40 + (xx // 8 % 2) * 160, 30 + (yy // 8 % 2) * 100, xx], axis=-1).astype(np.uint8)
    b = np.stack([yy, 30 + (yy // 4 % 2) * 190, 220 - xx], axis=-1).astype(np.uint8)
    b[40:65, 40:65] = a[40:65, 40:65]
    visible = np.ones((104, 104), dtype=bool)
    xy = (52, 52)
    upper, lower = strips(xy, list(range(-12, 13)))
    modes = {}
    deterministic_repeat = None
    for mode in ('full', 'local'):
        refs = {}
        for k, im in [('a', a), ('b', b)]:
            tokens = encoder.encode(im, visible, xy, mode)
            if mode == 'full' and k == 'a':
                repeated = encoder.encode(im, visible, xy, mode)
                deterministic_repeat = bool(np.array_equal(tokens, repeated))
                assert deterministic_repeat
            refs[k] = descriptor(tokens, upper, lower)
        values = []
        for label, original in [('a', a), ('b', b)]:
            query = original.copy()
            query[2, 2, 0] += 1
            tokens = encoder.encode(query, visible, xy, mode)
            desc = descriptor(tokens, upper, lower)
            values.append(dict(expected=label, result=rank(desc, refs)))
            assert rank(desc, {'copy1': desc, 'copy2': desc})['status'] == 'TIE'
            empty_columns = common_columns([(np.zeros_like(visible), xy)])
            assert rank(descriptor(tokens, *strips(xy, empty_columns)), refs)['status'] == 'UNAVAILABLE'
        modes[mode] = values
    passed = (all(v['result']['preference'] == v['expected'] for v in modes['full']) and
              all(v['result']['status'] == 'TIE' for v in modes['local']))
    return dict(status='PASS' if passed else 'FAIL', modes=modes,
                actual_token_tie_and_masked_unavailable='PASS', equal_local_pixels=True,
                cold_warm_same_input_bitwise_equal=deterministic_repeat)


def exclusion(query, pre):
    return [key for key, ref in pre['references'].items()
            if ref['episode_exclusion_frames'][0] <= query['frame'] <= ref['episode_exclusion_frames'][1]]


def compare(query, pre, encoder, images, masks):
    excluded = exclusion(query, pre)
    if excluded:
        return dict(query=query, status='EXCLUDED_REFERENCE_EPISODE', excluded_classes=excluded)
    variants = []
    refs = pre['references']
    for y in sorted({math.floor(query['source_xy'][1]), math.ceil(query['source_xy'][1])}):
        source_xy = [int(query['source_xy'][0]), y]
        xy = local_xy(source_xy)
        ref_xy = {k: local_xy(r['source_xy']) for k, r in refs.items()}
        contexts = [(masks[str(query['frame'])], xy)] + [
            (masks[str(r['frame'])], ref_xy[k]) for k, r in refs.items()]
        columns = common_columns(contexts)
        value = dict(source_center_xy=source_xy, common_columns=columns, modes={})
        if not columns:
            value['status'] = 'UNAVAILABLE_COMMON_SUPPORT_OR_CROP'
        else:
            value['status'] = 'MEASURED'
            value['token_weights'] = dict(query=weight_record(xy, columns),
                references={k: weight_record(ref_xy[k], columns) for k in refs})
            for mode in ('full', 'local'):
                q = descriptor(encoder.saved(images, masks, query['frame'], xy, mode), *strips(xy, columns))
                bank = {k: descriptor(encoder.saved(images, masks, r['frame'], ref_xy[k], mode, True),
                                      *strips(ref_xy[k], columns)) for k, r in refs.items()}
                value['modes'][mode] = rank(q, bank, required=3)
        variants.append(value)
    summary = {}
    for mode in ('full', 'local'):
        prefs = [v['modes'].get(mode, {}).get('preference') for v in variants]
        summary[mode] = prefs[0] if all(p == prefs[0] for p in prefs) else None
    return dict(query=query, status='COMPARED', variants=variants, regional_context_preference=summary)


def run(prepared_path, readiness_path, out, denied):
    started = time.monotonic()
    pre, ready, prepared = read(HERE / 'preflight.json'), read(readiness_path), read(prepared_path)
    assert prepared['preflight_sha256'] == sha(HERE / 'preflight.json')
    for rel, digest in ready['frozen_files'].items():
        assert sha(ROOT / rel) == digest, rel
    assert sha(prepared_path.parent / prepared['masks_file']) == prepared['mask_sha256']
    independent = checks()
    encoder = Encoder(pre['resources'])
    result = dict(schema='s11-cr1-regional-context-readout-v1', preflight_sha256=sha(HERE / 'preflight.json'),
        readiness_sha256=sha(readiness_path), prepared_sha256=sha(prepared_path),
        arithmetic_and_geometry=independent, stages={}, physical_acceptance='NOT_EVALUATED',
        retained_unassessed=pre['retained_unassessed'], results=[],
        source_partition=pre['exposure'], production_changed=False)
    stage_start = time.monotonic()
    result['stages']['stage1'] = synthetic(encoder)
    result['stages']['stage1']['elapsed_sec'] = time.monotonic() - stage_start
    assert result['stages']['stage1']['elapsed_sec'] <= pre['resources']['stage_seconds_limit']
    measured = {}
    result['stages']['stage2'] = dict(status='NOT_RUN')
    result['stages']['stage3'] = dict(status='NOT_RUN')
    if result['stages']['stage1']['status'] == 'PASS':
        stage_start = time.monotonic()
        from PIL import Image
        decode_start = time.monotonic()
        images = {int(f): np.array(Image.open(ROOT / path).convert('RGB')) for f, path in prepared['images'].items()}
        masks = dict(np.load(prepared_path.parent / prepared['masks_file'], allow_pickle=False))
        decode_seconds = time.monotonic() - decode_start
        for qid in pre['primary_queries']:
            q = next(q for q in prepared['queries'] if q['id'] == qid)
            measured[qid] = compare(q, pre, encoder, images, masks)
        a, b = [measured[qid].get('regional_context_preference', {}) for qid in pre['primary_queries']]
        full_pass = a.get('full') == 'interface' and b.get('full') in ('structure', 'texture')
        local_pass = a.get('local') == 'interface' and b.get('local') in ('structure', 'texture')
        passed = full_pass and not local_pass
        result['stages']['stage2'] = dict(status='PASS' if passed else 'FAIL',
            full_pair_pass=full_pass, local_pair_pass=local_pass,
            elapsed_sec=time.monotonic() - stage_start, saved_png_and_mask_decode_sec=decode_seconds,
            native_video_decode='NOT_RUN')
        assert result['stages']['stage2']['elapsed_sec'] <= pre['resources']['stage_seconds_limit']
        if passed:
            stage_start = time.monotonic()
            for q in prepared['queries']:
                if q['id'] not in measured:
                    measured[q['id']] = compare(q, pre, encoder, images, masks)
                if time.monotonic() - stage_start > pre['resources']['stage_seconds_limit']:
                    raise RuntimeError('stage3 time budget exceeded')
            result['stages']['stage3'] = dict(status='COMPLETE_DIAGNOSTIC_ONLY', elapsed_sec=time.monotonic()-stage_start)
    for q in prepared['queries']:
        result['results'].append(measured.get(q['id'], dict(query=q, status='NOT_RUN',
            excluded_classes_if_run=exclusion(q, pre), reason='stopped_at_first_failed_stage')))
    result['denominators'] = dict(total=len(result['results']), candidates=160, context_controls=4,
        statuses=dict(Counter(r['status'] for r in result['results'])),
        reviewed_target_candidates=sum(q.get('label') == 'confirmed_target' for q in prepared['queries']),
        reviewed_rejected_candidates=sum(q.get('label') == 'rejected_target' for q in prepared['queries']),
        unreviewed_candidates=sum(q['label'] == 'UNREVIEWED' for q in prepared['queries']))
    result['disposition'] = ('DIAGNOSTIC_ONLY_NO_PROMOTION' if result['stages']['stage3']['status'] != 'NOT_RUN'
                             else 'CLOSED_WITHOUT_PROMOTION')
    result['resources'] = dict(elapsed_sec=time.monotonic()-started, encoder_load_sec=encoder.load_seconds,
        forward_count=len(encoder.times), forward_seconds=encoder.times, peak_rss_bytes=rss(),
        workspace_allocated_bytes=allocated(WORKSPACE), external_artifact_allocated_bytes=allocated(HERE),
        tokens_per_forward=256, feature_dimension=384, retained_token_maps=0,
        python=sys.version, torch=encoder.version, device='cpu', dtype='float32', threads=2)
    assert result['resources']['elapsed_sec'] < pre['resources']['full_seconds_limit']
    assert result['resources']['workspace_allocated_bytes'] + allocated(HERE) < 3_000_000_000
    result['runtime_guard'] = dict(smoke_checks='PASS', denied_events=denied,
        scope='Python audit events for network and writes; not an OS sandbox security proof')
    for rel, digest in {**pre['inputs'], **pre['original_capture_pins'], **pre['production_source_pins']}.items():
        assert sha(ROOT / rel) == digest, rel
    result['unchanged_pins_at_end'] = True
    write(out / 'readout.json', result)
    assert sum(p.stat().st_size for p in out.rglob('*') if p.is_file()) < pre['resources']['run_output_bytes_limit']
    print(json.dumps(dict(stages=result['stages'], denominators=result['denominators'], resources=result['resources'])))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['check', 'run'])
    parser.add_argument('--prepared', type=Path)
    parser.add_argument('--readiness', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    denied = sandbox()
    import numpy as np
    if args.mode == 'check':
        print(json.dumps(checks()))
    else:
        run(args.prepared, args.readiness, args.out, denied)
