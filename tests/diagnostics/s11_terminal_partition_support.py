"""TPA-1 terminal-partition cross-representation support diagnostic. Not a promoted policy.

When both the candidate and the peer are terminal partitions of the textured
layer, the peer's high texture conflict no longer excludes it from
cross-representation support. See
docs/50-diagnostics/s11/2026-10-20-terminal-partition-support.md.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

from oil_tracker.adapters.vision import oil_observation_resolver as resolver
from tests.diagnostics import s11_clean_anchor_fill as caf
from tests.diagnostics import s11_role_consumer_intervention as rci
from tests.diagnostics import s11_single_observation_influence as soi

PROTOCOL = Path('docs/50-diagnostics/s11/2026-10-20-terminal-partition-support.md')
TERMINAL_LEVEL = 0.55  # existing material_layer_terminal level in oil_candidate_authority


def support(candidate, candidates, glass, *, evidence_index, exempt_terminal_pairs, exemptions=None):
    """Copy of resolver._cross_representation_support differing only in the texture peer exclusion."""
    unit = resolver._unit
    candidate_evidence = evidence_index.evidence(candidate)
    candidate_family = resolver._candidate_representation_family(candidate, candidate_evidence)
    candidate_terminal = candidate_evidence.terminal_support >= TERMINAL_LEVEL
    tolerance = max(8.0, float(glass.detector_settings.temporal_max_jump_px) * 0.375)
    value = 0.0
    for peer in candidates:
        if peer is candidate:
            continue
        peer_evidence = evidence_index.evidence(peer)
        peer_family = resolver._candidate_representation_family(peer, peer_evidence)
        if peer_family == candidate_family or not resolver._candidate_eligible(peer, peer_evidence):
            continue
        texture_excluded = peer_evidence.material_texture_conflict >= 0.60
        if (texture_excluded and exempt_terminal_pairs and candidate_terminal
                and peer_evidence.terminal_support >= TERMINAL_LEVEL):
            texture_excluded = False
            if exemptions is not None:
                exemptions.append((float(candidate.y), candidate.source, float(peer.y), peer.source))
        if (texture_excluded or peer_evidence.artifact_signature >= 0.44
                or peer_evidence.optics_opposition >= 0.46):
            continue
        if "calibrated_raster" in {candidate_family, peer_family} and "material" not in {
                candidate_family, peer_family}:
            continue
        distance = abs(float(peer.y) - float(candidate.y))
        if distance > tolerance:
            continue
        peer_features = peer.features
        peer_boundary = unit(peer_features.get("boundary_likelihood", peer.feature_score))
        peer_artifact = unit(peer_features.get(
            "artifact_likelihood", peer.penalties.get("artifact_likelihood", 0.0)))
        peer_coverage = unit(peer_features.get(
            "narrow_horizontal_coverage", peer_features.get("horizontal_coverage", 0.0)))
        advantage = unit((peer_boundary - peer_artifact + 0.10) / 0.30)
        evidence = unit(0.55 * peer_evidence.material_support + 0.25 * peer_coverage + 0.20 * advantage)
        proximity = 0.75 + 0.25 * unit(1.0 - distance / tolerance)
        value = max(value, evidence * proximity)
    return unit(value)


@contextmanager
def terminal_support(*, verify_copy=True):
    """Patch support with the TPA-1 copy; yield the list of changed support values.

    With ``verify_copy`` every call also evaluates the copy with the exemption off
    and requires exact equality with the original function.
    """
    original = resolver._cross_representation_support
    operations = []

    def patched(candidate, candidates, glass, *, evidence_index):
        if verify_copy:
            rci.require(support(candidate, candidates, glass, evidence_index=evidence_index,
                                exempt_terminal_pairs=False)
                        == original(candidate, candidates, glass, evidence_index=evidence_index),
                        'TPA-1 copy diverges from the original with the exemption off')
        exemptions = []
        trial = support(candidate, candidates, glass, evidence_index=evidence_index,
                        exempt_terminal_pairs=True, exemptions=exemptions)
        if exemptions:
            ordinary = original(candidate, candidates, glass, evidence_index=evidence_index)
            if trial != ordinary:
                operations.append(dict(candidate_y=float(candidate.y), source=candidate.source,
                                       ordinary=ordinary, trial=trial,
                                       exempted_peers=[dict(y=p_y, source=p_s) for _, _, p_y, p_s in exemptions]))
        return trial

    with patch.object(resolver, '_cross_representation_support', patched):
        yield operations
    rci.require(resolver._cross_representation_support is original, 'TPA-1 patch leak')


def execute(raw, recipe, case):
    with terminal_support() as operations:
        result = soi.execute(raw, recipe, case)
    return (*result, operations)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=rci.ROOT)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    caf.run(args.root.resolve(), args.output.resolve(), trial=execute, protocol=PROTOCOL,
            schema='s11-terminal-partition-support-v1',
            scope='TPA-1 diagnostic wrapper; not production adoption',
            extra_sources=(Path(__file__),))


if __name__ == '__main__':
    main()
