from __future__ import annotations

import csv
import json

import pytest

from oil_tracker.domain.enums import InitialObservationState
from oil_tracker.domain.session import AnalysisSession, InitialStateConfirmation
from tests.diagnostics import s11_layer_bottom_topology_2_field as field

SEGMENTS = [dict(id='A-1', glass='Accum', start_sec=480.0, end_sec=653.0),
            dict(id='A-2', glass='Accum', start_sec=653.0, end_sec=780.0),
            dict(id='B-1', glass='BASE', start_sec=480.0, end_sec=780.0)]
COLUMNS = ('glass_id', 'frame_index', 'timestamp_sec') + field.DIFF_FIELDS


def test_segments_are_half_open_except_the_last_of_each_glass():
    assert field.segment_of(SEGMENTS, 'Accum', 653.0) == 'A-2'
    assert field.segment_of(SEGMENTS, 'Accum', 652.5) == 'A-1'
    assert field.segment_of(SEGMENTS, 'Accum', 780.0) == 'A-2'
    assert field.segment_of(SEGMENTS, 'BASE', 780.0) == 'B-1'
    assert field.segment_of(SEGMENTS, 'BASE', 479.5) is None
    assert field.segment_of(SEGMENTS, 'sample4', 10.0) is None


def test_video_override_moves_the_confirmations_with_the_session(tmp_path):
    session = AnalysisSession(input_video_path='C:/old.mp4', analysis_start_sec=480.0, initial_state_confirmations={
        'g': InitialStateConfirmation(InitialObservationState.FULL_NO_INTERFACE, 'C:/old.mp4', 480.0)})
    (tmp_path / 'session.json').write_text(json.dumps(session.to_dict()), encoding='utf-8')
    from unittest.mock import patch
    with patch('oil_tracker.adapters.storage.json_recipe_repository.JsonRecipeRepository.load', return_value='recipe'):
        moved, recipe = field.load_session(tmp_path, tmp_path / 'new.mp4')
    assert recipe == 'recipe'
    confirmation = moved.initial_state_confirmations['g']
    assert moved.input_video_path == confirmation.input_video_path == str(tmp_path / 'new.mp4')
    assert confirmation.matches(InitialObservationState.FULL_NO_INTERFACE, moved)


def _bundle(path, rows):
    path.mkdir()
    with (path / 'tracking_data.csv').open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def _row(glass, frame, time, oil='', foam=''):
    return dict(glass_id=glass, frame_index=frame, timestamp_sec=time, fill_state='VISIBLE', raw_oil_air_level_y=oil,
                raw_foam_front_y=foam, oil_is_valid='True' if oil else 'False', foam_is_valid='False', flags='')


def test_compare_lists_changed_rows_segments_held_out_and_watch_rows(tmp_path):
    truth = tmp_path / 'truth.json'
    truth.write_text(json.dumps(dict(segments=SEGMENTS)), encoding='utf-8')
    ref_rows = [_row('a', 16112, '672.0', '438.0'), _row('a', 16268, '678.5', '238.0'), _row('b', 16112, '672.0')]
    trial_rows = [_row('a', 16112, '672.0', '495.0'), _row('a', 16268, '678.5', '238.0'), _row('b', 16112, '672.0')]
    reference, trial = _bundle(tmp_path / 'r', ref_rows), _bundle(tmp_path / 't', trial_rows)
    names = {'a': 'Accum', 'b': 'BASE'}
    from unittest.mock import patch

    def tracking(bundle):
        with (bundle / 'tracking_data.csv').open(encoding='utf-8-sig', newline='') as handle:
            return {(names[r['glass_id']], int(r['frame_index'])): r for r in csv.DictReader(handle)}

    with patch.object(field, 'tracking', tracking):
        result = field.compare(reference, trial, truth)
    (changed,) = result['changed']
    assert (changed['glass'], changed['segment'], changed['ref'][1], changed['trial'][1]) == ('Accum', 'A-2', 438.0, 495.0)
    assert result['segments']['A-2'] == dict(rows=2, oil_ref=2, oil_trial=2, foam_ref=0, foam_trial=0, changed=1)
    assert [(r['frame'], r['ref'], r['trial']) for r in result['held_out']] == [(16112, 438.0, 495.0)]
    assert [(r['frame'], r['equal']) for r in result['watch']] == [(16268, True)]
    with patch.object(field, 'tracking', lambda bundle: tracking(reference) if bundle == reference else {}):
        with pytest.raises(SystemExit, match='row keys differ'):
            field.compare(reference, trial, truth)
