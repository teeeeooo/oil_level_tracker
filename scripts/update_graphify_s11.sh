#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

if ! command -v graphify >/dev/null 2>&1; then
  printf 'graphify is not installed; skip topology refresh and use source/logic-map routing.\n' >&2
  exit 2
fi

if [[ -f graphify-out/graph.json ]]; then
  graphify update . --no-cluster
else
  graphify extract . --no-cluster
fi
