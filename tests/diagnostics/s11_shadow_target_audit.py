"""W3 packet context/recorded-funnel audit, not another scorer or trace writer.

The experiment owner supplies validated labels, packets and immutable input
receipts. This module preserves context the score projection does not consume.
"""
from collections import Counter
import copy
import json
from pathlib import Path

from tests.diagnostics import s11_interface_shadow_evaluation as o2

SCHEMA = 's11-o2-target-audit-v1'
SPEC = {
    'id': 'target-context-and-recorded-funnel-v1',
    'purpose': 'inspect existing context and recorded losses before choosing one W4 challenger',
    'predictions': 'none; ranking is not converted to identity/local/scalar decisions',
    'context': 'all actual centers/scales/bands; aliases are not independent measurements',
    'funnel': 'exact original candidate offset plus source/Y; recorded facts only',
    'fit_partitions': [], 'threshold': None,
}
FIELDS = ('gray_mean', 'gray_std', 'material_mean', 'static_overlap', 'glare_fraction',
          'saturation_fraction', 'mask_excluded_fraction', 'valid_fraction', 'normal_alignment')


STRUCTURE_SCHEMA = 's11-o2-structure-context-audit-v1'
STRUCTURE_FIELDS = (
    'artifact_likelihood', 'static_prior_contribution', 'static_artifact_penalty',
    'optics_conflict', 'glare_conflict', 'glare_penalty', 'border_penalty',
    'exclusion_conflict', 'exclusion_penalty', 'material_texture_conflict',
    'ambiguity_likelihood', 'boundary_likelihood', 'broad_strength', 'region_contrast',
    'narrow_peak_strength', 'edge_strength', 'narrow_horizontal_coverage',
    'horizontal_coverage', 'broad_scale_consistency', 'polarity_confidence',
    'material_terminal_partition_support', 'calibrated_artifact_match',
    'artifact_center_x_norm', 'artifact_center_y_norm', 'artifact_width_norm',
    'artifact_height_norm', 'artifact_angle_deg',
)
STRUCTURE_SPEC = {
    'id': 'recorded-structure-context-v1',
    'fields': list(STRUCTURE_FIELDS),
    'source': 'raw indexed candidate features/penalties and raw recipe glass geometry',
    'join': 'original candidate_input_index plus source/kind/canonical_y/local_y/rejected',
    'missing': 'missing/null/present; never default missing numeric evidence to zero',
    'interpretation': 'recorded signals and registered templates, not physical identity',
    'fit_partitions': [], 'threshold': None,
}


def recorded_field(mapping, key, *, numeric=False):
    value = mapping.get(key)
    state = 'missing' if key not in mapping else 'null' if value is None else 'present'
    if numeric and state == 'present':
        o2.number(value, key)
    return {'state': state, 'value': copy.deepcopy(value)}


def recorded_structure_context(frame, payload, recipe):
    """Project serialized evidence only; never rebuild typed evidence or match templates."""
    raw = o2.unique(payload['candidates'], 'candidate_input_index', 'raw candidates')
    expected = o2.unique(frame['witness']['candidates'], 'candidate_input_index', 'witness candidates')
    for idx in raw:
        o2.integer(idx, 'raw candidate index')
    o2.require(set(expected) == {idx for idx, c in raw.items() if c['kind'] == 'oil_air'},
               'structure candidate inventory mismatch')
    candidates = []
    for idx, witness in expected.items():
        c = raw[idx]
        for key in ('source', 'kind', 'canonical_y', 'local_y', 'rejected'):
            o2.require(c[key] == witness[key], 'structure candidate provenance mismatch')
        o2.require(type(c['rejected']) is bool, 'recorded rejected must be boolean')
        row = {k: copy.deepcopy(c[k]) for k in ('candidate_input_index', 'source', 'kind', 'canonical_y', 'local_y', 'rejected')}
        row['reject_reason'] = recorded_field(c, 'reject_reason')
        row['feature_score'] = recorded_field(c, 'feature_score', numeric=True)
        for container in ('features', 'penalties'):
            field = recorded_field(c, container)
            value = field.pop('value')
            o2.require(field['state'] != 'present' or isinstance(value, dict), 'context container must be an object')
            field['fields'] = {k: recorded_field(value or {}, k, numeric=True) for k in STRUCTURE_FIELDS}
            row[container] = field
        candidates.append(row)
    glasses = [g for g in recipe['glasses'] if g['id'] == frame['glass_id']]
    o2.require(len(glasses) == 1, 'structure recipe glass must match exactly once')
    geometry = glasses[0]['geometry']
    inventory = recorded_field(geometry, 'artifact_templates')
    if inventory['state'] == 'present':
        o2.require(isinstance(inventory['value'], list), 'artifact templates must be a list')
        o2.unique(inventory['value'], 'id', 'artifact templates')
        for template in inventory['value']:
            for key in ('center_x', 'center_y', 'width', 'height', 'angle_deg'):
                if key in template:
                    o2.number(template[key], key)
    inventory['count'] = len(inventory['value']) if inventory['state'] == 'present' else None
    return {'record_id': frame['record_id'], 'glass_id': frame['glass_id'],
            'frame_index': frame['frame_index'], 'candidates': candidates,
            'recipe_geometry': {k: recorded_field(geometry, k) for k in ('ellipse', 'exclusions')},
            'artifact_templates': inventory,
            'limitation': 'An empty registry is not absence of structure; a recorded match is not ground truth. '
                          'Same-frame derived features are correlated. No template matching or classifier was rerun.'}


def context_rows(case, frame):
    annotations = {a['candidate_input_index']: a for a in case['candidates']}
    rows = []
    for c in frame['witness']['candidates']:
        a = annotations[c['candidate_input_index']]
        reviews = {o2.geometry_key(p): p['judgment'] for p in a.get('path_reviews', [])}
        for sector in c['sectors']:
            for center in sector['centers']:
                geometry = {'geometry_basis': center['role'], 'source_x_range': sector['source_x_range'],
                            'source_y': center['source_y']}
                for scale in center['scales']:
                    for band in scale['bands']:
                        fields = {}
                        for key in FIELDS:
                            value = band.get(key)
                            state = 'missing' if key not in band else 'null' if value is None else 'present'
                            if state == 'present':
                                o2.number(value, key)
                            fields[key] = {'state': state, 'value': value}
                        rows.append({'case_id': case['case_id'], 'candidate_input_index': c['candidate_input_index'],
                            'witness_sha256': a['witness_sha256'], 'identity': o2.identity(a), **geometry,
                            'judgment': reviews.get(o2.geometry_key(geometry), 'unreviewed'),
                            'band_width_px': scale['band_width_px'], 'band': band['name'],
                            'availability': {k: {'state': 'missing' if k not in band else 'null' if band[k] is None else 'present',
                                                  'value': band.get(k)}
                                             for k in ('available', 'material_available', 'static_available')},
                            'reason': band.get('reason'), 'fields': fields})
    return rows


def context_summary(rows):
    """Descriptive candidate/basis summaries; no near/off-derived inference mask."""
    groups = {}
    for row in rows:
        key = (row['candidate_input_index'], row['geometry_basis'])
        groups.setdefault(key, []).append(row)
    summaries = []
    for (idx, basis), group in sorted(groups.items()):
        metrics = {}
        for key in FIELDS:
            states = Counter(r['fields'][key]['state'] for r in group)
            availability_key = {'material_mean': 'material_available', 'static_overlap': 'static_available'}.get(key, 'available')
            # These ratios describe occlusion itself, including unavailable bands.
            independent_ratio = key in ('glare_fraction', 'saturation_fraction', 'mask_excluded_fraction', 'valid_fraction')
            usable = [r['fields'][key]['value'] for r in group if r['fields'][key]['state'] == 'present'
                      and (independent_ratio or r['availability'][availability_key]['value'] is True)]
            metrics[key] = {'states': dict(states), 'usable_count': len(usable),
                            'median': o2.deterministic_percentile(usable, .5),
                            'min': min(usable) if usable else None, 'max': max(usable) if usable else None}
        summaries.append({'candidate_input_index': idx, 'geometry_basis': basis,
                          'identity': group[0]['identity'], 'band_count': len(group), 'fields': metrics})
    return summaries


def recorded_funnel(frame, sequence):
    """Join serialized R21 witness offsets, never score-sorted sequence positions."""
    witness = sequence.get('state', {}).get('sequence_decision_witness') if sequence else None
    if witness is None:
        return {'status': 'UNAVAILABLE', 'reason': 'recorded_decision_witness_absent', 'candidates': []}
    o2.require(witness.get('schema_version') == 'r21-decision-witness-v1', 'unsupported recorded decision witness')
    ident = witness['identity']
    o2.require(ident['layer'] == 'sequence' and ident['glass_id'] == frame['glass_id']
               and ident['frame_index'] == frame['frame_index'] and ident['time_sec'] == frame['timestamp_sec'],
               'decision witness frame mismatch')
    raw = {c['candidate_input_index']: c for c in frame['witness']['candidates']}
    members = {}
    for row in witness['rows']:
        for member in row['members']:
            idx = o2.integer(member['candidate_offset'], 'decision candidate offset')
            o2.require(idx in raw and idx not in members, 'unknown or duplicate decision witness member')
            o2.require(member['source'] == raw[idx]['source'] and member['y'] == raw[idx]['canonical_y'],
                       'decision member source/Y mismatch')
            for value in (member['tracklet_admitted'], member['selected'], row['phase_admitted'], row['publishable']):
                o2.require(type(value) is bool, 'recorded gate must be boolean')
            members[idx] = (row, member)
    selected = witness['selection']['selected_candidate']
    if selected is not None:
        idx = o2.integer(selected['candidate_offset'], 'selected candidate offset')
        o2.require(idx in members and members[idx][1]['selected'] and selected['source'] == raw[idx]['source']
                   and selected['y'] == raw[idx]['canonical_y'], 'selection/member mismatch')
    o2.require(sum(m['selected'] for _, m in members.values()) == (selected is not None), 'ambiguous recorded selection')
    rows = []
    for idx, c in raw.items():
        match = members.get(idx)
        if match is None:
            rows.append({'candidate_input_index': idx, 'status': 'NOT_IN_RETAINED_REFS',
                         'first_known_loss': 'UNKNOWN_BEFORE_RETAINED_REFS'})
            continue
        row, member = match
        first = (None if member['selected'] else 'tracklet_not_admitted' if not member['tracklet_admitted'] else
                 'phase_not_admitted' if not row['phase_admitted'] else
                 'not_publishable' if not row['publishable'] else
                 'not_selected' if not member['selected'] else None)
        rows.append({'candidate_input_index': idx, 'status': 'RECORDED', 'first_known_loss': first,
                     'member': copy.deepcopy(member),
                     'row': {k: row[k] for k in ('row_hypothesis_id', 'tracklet_id', 'phase_admitted', 'publishable')}})
    return {'status': 'RECORDED', 'candidates': rows, 'phase': copy.deepcopy(witness['phase']),
            'routes': copy.deepcopy(witness['routes']), 'selection': copy.deepcopy(witness['selection']),
            'sequence_positions': copy.deepcopy(sequence.get('positions', {})),
            'limitation': 'Absent refs do not identify authority versus top-k loss; sequence facts are not CSV publication proof.'}


def load_recorded_sequences(bundle_path, label_paths, snapshots, *, structure_context=False):
    from oil_tracker.adapters.storage.result_bundle_reader import ResultBundleReader
    from oil_tracker.adapters.storage.debug_trace_repository import DebugTraceRepository
    from tests.diagnostics import s11_review_records as records
    bundle = ResultBundleReader().read(bundle_path)
    o2.require(bundle.debug_trace_path and bundle.debug_index_path, 'indexed trace required')
    files = [bundle.files[k] for k in ('manifest', 'recipe_snapshot', 'session')]
    files += [Path(bundle.root)/bundle.debug_trace_path, Path(bundle.root)/bundle.debug_index_path]
    for path in files:
        path = Path(path).resolve()
        digest = o2.sha256_file(path)
        o2.require(path not in snapshots or snapshots[path] == digest, 'bundle changed while loading')
        snapshots[path] = digest
    recipe = o2.read_json(bundle.files['recipe_snapshot']) if structure_context else None
    frames = []
    for path in label_paths:
        frames.extend(records._verify_packets(bundle, o2.read_json(path), Path(path).parent))
    repo = DebugTraceRepository(bundle, record_cache_size=1)
    try:
        index = {s.record_id: s for s in repo.summaries()}
        results = {}
        for frame in frames:
            s = index[frame['record_id']]
            # The existing public record model omits the top-level sequence key.
            # Reuse its verified index/identity, reading only this bounded record.
            o2.require(s.byte_length <= 16*1024**2, 'sequence record exceeds audit bound')
            with (Path(bundle.root)/bundle.debug_trace_path).open('rb') as handle:
                handle.seek(s.byte_offset)
                payload = json.loads(handle.read(s.byte_length))
            o2.require(payload['record_id'] == frame['record_id'] and payload['run_id'] == frame['run_id']
                       and payload['glass_id'] == frame['glass_id'] and payload['frame_index'] == frame['frame_index'],
                       'sequence raw record mismatch')
            results[frame['case_id']] = recorded_funnel(frame, payload.get('sequence'))
            if structure_context:
                results[frame['case_id']]['structure_context'] = recorded_structure_context(frame, payload, recipe)
        return results
    finally:
        repo.close()


def audit_case(case, frame, funnel=None):
    rows = context_rows(case, frame)
    return {'case_id': case['case_id'], 'identity_counts': dict(Counter(o2.identity(a) for a in case['candidates'])),
            'target_accounting': o2.summarize_targets([case], {case['packet_sha256']: {case['case_id']: frame}}, {}),
            'context_rows': rows, 'context_summary': context_summary(rows),
            'recorded_funnel': funnel or {'status': 'NOT_REQUESTED', 'candidates': []}}


def render_summary(report):
    def metric(summary, field):
        f = summary['fields'][field]
        values = ('none' if f['median'] is None else f"{f['median']:.4f} [{f['min']:.4f},{f['max']:.4f}]")
        return f"{f['usable_count']}/{summary['band_count']}; {values}"

    lines = ['# S11 W3 target/context audit', '', 'EXPLORATORY_UNCALIBRATED; no classifier decisions or field qualification.',
             'Missing predictions stay missing. Existing scores are reference checks, not predictions.',
             f"Artifact: `{report['artifact']['sha256']}`", '']
    for c in report['target_audit']:
        t = c['target_accounting']
        lines += [f"## Case {c['case_id']}", f"Identity counts: {c['identity_counts']}",
                  f"Visible frames: {t['visible_frame_count']}; scalar truth: {t['scalar']['status']}",
                  f"Recorded funnel: {c['recorded_funnel']['status']}",
                  f"Recorded phase: {c['recorded_funnel'].get('phase', {}).get('value', 'UNAVAILABLE')}; selected candidate: {c['recorded_funnel'].get('selection', {}).get('selected_candidate')}", '',
                  'Context columns: usable/total bands; median [min,max]. Descriptive across correlated scales/bands, not fitted separation.',
                  '| Candidate | Basis | Identity | Static overlap | Material mean | Glare fraction |',
                  '|---|---|---|---|---|---|']
        for s in c['context_summary']:
            lines.append(f"| {s['candidate_input_index']} | {s['geometry_basis']} | {s['identity']} | {metric(s,'static_overlap')} | {metric(s,'material_mean')} | {metric(s,'glare_fraction')} |")
        lines += ['', '| Candidate | Recorded status | First known loss | Authority | Tracklet / phase / publishable / selected |', '|---|---|---|---|---|']
        for r in c['recorded_funnel']['candidates']:
            m, row = r.get('member', {}), r.get('row', {})
            gates = [m.get('tracklet_admitted'), row.get('phase_admitted'), row.get('publishable'), m.get('selected')]
            lines.append(f"| {r['candidate_input_index']} | {r['status']} | {r['first_known_loss']} | {m.get('authority')} / {m.get('authority_reason')} | {gates} |")
        lines += ['', 'Missing retained refs cannot identify an earlier gate; do not infer top-k/authority causes.', '']
    lines += ['Return this generated summary plus COMPLETE/output-hash/input-preservation verification.',
              'Keep detailed JSON local. No new labels, freeze, detector run or threshold selection is needed.', '']
    return '\n'.join(lines)


def render_structure_summary(report):
    def cell(value):
        return str(value).replace('|', r'\|').replace('\n', ' ').replace('\r', ' ')

    def field_value(field):
        return cell(field['value']) if field['state'] == 'present' else field['state']

    lines = ['# S11 recorded structure/context audit', '',
             'EXPLORATORY_UNCALIBRATED; FIELD FAIL; no new predictions or detector run.',
             'Historical labels are pinned; human uncertainty qualifications remain separate from recorded measurements.',
             'Missing/null are not zero. Registered templates and recorded signals are not identity truth.',
             f"Artifact: `{report['artifact']['sha256']}`", '']
    for case in report['target_audit']:
        context = case['recorded_funnel']['structure_context']
        inventory = context['artifact_templates']
        lines += [f"## Case {cell(case['case_id'])}",
                  f"Templates: state={inventory['state']}; count={inventory['count']}",
                  'Template metadata/geometry retained in JSON; provenance of registration is not independently verified.',
                  '| Candidate | Source | Historical identity | Rejected | Reject reason |', '|---|---|---|---|---|']
        identities = {r['candidate_input_index']: r['identity'] for r in case['context_summary']}
        for c in context['candidates']:
            lines.append(f"| {c['candidate_input_index']} | {cell(c['source'])} | {identities.get(c['candidate_input_index'], 'unavailable')} | {c['rejected']} | {field_value(c['reject_reason'])} |")
        lines += ['', 'All present context values (including zero); missing/null counts cover the fixed field inventory.',
                  '| Candidate | Container | Container state | Missing | Null | Present fields |', '|---|---|---|---|---|---|']
        for c in context['candidates']:
            for key in ('features', 'penalties'):
                container = c[key]
                counts = Counter(f['state'] for f in container['fields'].values())
                values = '; '.join(f"{k}={field_value(f)}" for k, f in container['fields'].items() if f['state'] == 'present')
                lines.append(f"| {c['candidate_input_index']} | {key} | {container['state']} | {counts['missing']} | {counts['null']} | {values or 'none'} |")
        lines += ['', '| Template ID | Kind | Center X/Y | Width/height | Angle |', '|---|---|---|---|---|']
        for template in inventory['value'] or []:
            values = [field_value(recorded_field(template, k)) for k in ('id', 'kind', 'center_x', 'center_y', 'width', 'height', 'angle_deg')]
            lines.append(f"| {values[0]} | {values[1]} | {values[2]} / {values[3]} | {values[4]} / {values[5]} | {values[6]} |")
        lines += ['', context['limitation'], '']
    lines += ['Return this generated summary and COMPLETE/output/input hash checks. Keep detailed JSON local.',
              'No label edit, threshold choice, template registration or video review is requested.', '']
    return '\n'.join(lines)
