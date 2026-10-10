"""Explicit use of retired local evidence, shared by S11 diagnostic entry points.

This is an evaluation guard, not a production detector rule or a security boundary.
The wrapper scopes its environment to one command and its worker processes.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys


SAMPLE3_PURPOSE_ENV = "OIL_TRACKER_SAMPLE3_PURPOSE"
SAMPLE3_PURPOSES = ("legacy-regression", "engineering-replay")


class RestrictedCorpusUseError(RuntimeError):
    """A retired source requires an explicit, limited evaluation purpose."""


def require_corpus_access(samples: tuple[str, ...]) -> dict[str, object]:
    restricted = ["sample3"] if "sample3" in samples else []
    purpose = os.environ.get(SAMPLE3_PURPOSE_ENV) if restricted else None
    if restricted and purpose not in SAMPLE3_PURPOSES:
        raise RestrictedCorpusUseError(
            "sample3 is QUARANTINED: default development/replay use is blocked. "
            "For an existing legacy regression or engineering compatibility check, use "
            "python -m tests.diagnostics.s11_corpus_access "
            "--purpose {legacy-regression,engineering-replay} -- <command>. "
            "This does not authorize new sample3 tuning, clip mining or physical scoring. "
            "See sample/README.md#sample3-use-restriction."
        )
    return {
        "schema": "s11-corpus-access-v1",
        "restricted_samples": restricted,
        "sample3_purpose": purpose,
        "physical_acceptance": "NOT_EVALUATED",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--purpose", choices=SAMPLE3_PURPOSES, required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("a command is required after --")
    env = os.environ.copy()
    env[SAMPLE3_PURPOSE_ENV] = args.purpose
    print(
        f"sample3 explicit purpose={args.purpose}; physical_acceptance=NOT_EVALUATED",
        file=sys.stderr,
        flush=True,
    )
    return subprocess.run(command, env=env, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
