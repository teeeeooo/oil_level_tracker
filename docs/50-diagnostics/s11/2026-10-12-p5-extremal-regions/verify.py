"""Verify S3 input identity, every query, and independent qualified-area floods."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root, output = args.root.resolve(), args.output.resolve()
    if output.exists():
        raise FileExistsError(output)
    sys.path[:0] = [str(root/'src'), str(root)]
    import numpy as np
    from tests.unit.test_s11_extremal_regions import flood_spectrum
    here = Path(__file__).resolve().parent
    module = importlib.util.spec_from_file_location('s3_saved_raster_reader', here/'run.py')
    runner = importlib.util.module_from_spec(module)
    module.loader.exec_module(runner)
    result = json.loads((here/'readout.json').read_text())
    pre = json.loads((here/'preflight.json').read_text())
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    for path, expected in result['inputs'].items():
        assert sha(root/path) == expected, path
    old = json.loads((root/pre['inventory']['path']).read_text())
    source = json.loads((root/pre['source_snapshot']['path']).read_text())['source_files']
    assert len(source) == 221 and all(sha(root/p) == v for p, v in source.items())
    assert [c['id'] for c in result['cases']] == pre['representative_case_ids']
    assert [c['id'] for c in result['broader_inventory']] == [c['id'] for c in old['cases']]
    assert all(c['status'] == ('REPRESENTATIVE_ONLY' if c['id'] in pre['representative_case_ids'] else 'NOT_RUN')
               for c in result['broader_inventory'])
    rasters = {}
    queries = sides = available = 0
    for case in result['cases']:
        meta = next(c for c in old['cases'] if c['id'] == case['id'])
        gray, edges, visible = runner.load_case(root, meta)
        rasters[case['id']] = gray
        measured = case['measurement']
        assert measured['selected_scalar'] is None and measured['physical_decision'] == 'UNRESOLVED'
        assert [r['row'] for r in measured['rows']] == np.flatnonzero(edges[:, meta['column']] & visible[:, meta['column']]).tolist()
        for row in measured['rows']:
            queries += 1
            assert row['source_y'] == meta['origin'][1]+(row['row']+.5)*meta['scale_xy'][1]-.5
            assert not row['scalar_eligible'] and row['physical_role'] == 'UNRESOLVED'
            b = min(32, max(4, round(min(gray.shape)*.06)))
            for side in ('upper', 'lower'):
                sides += 1
                record = row[side]
                expected_y = [row['row']-2-b, row['row']-2] if side == 'upper' else [row['row']+3, row['row']+3+b]
                assert record['bounds_xyxy'] == [meta['column']-b, expected_y[0], meta['column']+b+1, expected_y[1]]
                x0, y0, x1, y1 = record['bounds_xyxy']
                inside = x0 >= 0 and y0 >= 0 and x1 <= gray.shape[1] and y1 <= gray.shape[0]
                valid = inside and visible[y0:y1, x0:x1].all()
                assert (record['status'] == 'AVAILABLE') == bool(valid)
                if not valid:
                    assert 'integrated' not in record and 'threshold_area_runs' not in record
                    continue
                available += 1
                runs = record['threshold_area_runs']
                assert runs[0][0] == 1 and runs[-1][1] == 256
                assert all(a[1] == z[0] for a, z in zip(runs[:-1], runs[1:], strict=True))
                spectrum = [area for a, z, area in runs for _ in range(a, z)]
                assert len(spectrum) == 255
                assert sum(spectrum) == record['integrated_area']
                assert max(spectrum) == record['peak_area']
                assert record['integrated'] == sum(spectrum)/(255*(y1-y0)*(x1-x0))
                assert record['ablated'] == max(spectrum)/((y1-y0)*(x1-x0))
                assert 0 <= record['integrated'] <= record['ablated'] <= 1
    floods = 0
    for query in result['qualified_queries']:
        case = next(c for c in result['cases'] if c['id'] == query['case_id'])
        rows = [r for r in case['measurement']['rows'] if query['interval'][0] <= r['source_y'] <= query['interval'][1]]
        assert rows == query['rows']
        for row in rows:
            for side in ('upper', 'lower'):
                record = row[side]
                if record['status'] == 'AVAILABLE':
                    x0, y0, x1, y1 = record['bounds_xyxy']
                    expected = flood_spectrum(rasters[query['case_id']][y0:y1, x0:x1])
                    actual = [area for a, z, area in record['threshold_area_runs'] for _ in range(a, z)]
                    assert actual == expected, (query['id'], row['source_y'], side)
                    floods += 1
    assert result['disposition'] == 'CLOSED_WITHOUT_PROMOTION'
    assert all(result['synthetic_conditions'].values())
    assert not result['representative_conditions']['both_foam_uppers_retained']
    report = dict(status='PASS', inputs_verified=len(result['inputs']), production_files_unchanged=len(source),
        queries_verified=queries, side_records_verified=sides, available_side_records=available,
        qualified_side_spectra_independently_flooded=floods, thresholds_per_spectrum=255,
        broad_inventory_count=len(result['broader_inventory']),
        readout_sha256=sha(here/'readout.json'), verifier_sha256=sha(Path(__file__)),
        frozen_preflight_sha256=sha(here/'preflight.json'), production_or_field_acceptance=False)
    with output.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
