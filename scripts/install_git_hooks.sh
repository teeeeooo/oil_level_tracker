#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"
test -x scripts/check_detector_governance.py || chmod +x scripts/check_detector_governance.py
git config core.hooksPath .githooks
chmod +x .githooks/pre-push
printf 'Installed repository hooks at %s/.githooks (core.hooksPath=.githooks)\n' "$repo_root"
