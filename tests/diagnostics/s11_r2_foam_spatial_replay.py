from __future__ import annotations

import argparse
import json
from pathlib import Path

from tests.diagnostics.s11_report_observability_replay import run_replay


R2_NUMERIC_OIL_COUNTS = {
    "base_sample_1": 3,
    "sample2": 2,
    "sample3": 42,
    "sample4": 64,
}
R2_TRACKING_FINGERPRINTS = {
    "base_sample_1": "87166f357d7c962fb16a9a27a4def3329b587e27a74efd0671dce981046f3654",
    "sample2": "912225deb00b1a33504d7541be9a61727049a2a845c29ebd8b7badd7197f06aa",
    "sample3": "0bbd8a8c3a7c353b0f4a7a6557dc61220f681c7a33eea38ea79c8d75cb268f3c",
    "sample4": "d37bbd9101fa3f7d3f56524b588c1e22d76eb4849702d12fceeeec3ea2385c37",
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replay and verify the bounded S11-R2 Foam/Spatial repair."
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("sample/output/s11-r2"),
    )
    args = parser.parse_args()
    manifest = run_replay(
        output_root=args.output_root,
        expected_numeric_oil_counts=R2_NUMERIC_OIL_COUNTS,
        expected_tracking_fingerprints=R2_TRACKING_FINGERPRINTS,
        run_label="S11-R2",
        run_note="Bounded Foam/Spatial authority repair qualification replay",
        manifest_schema="s11-r2-foam-spatial-replay-v1",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
