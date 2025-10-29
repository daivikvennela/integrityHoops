#!/usr/bin/env bash
set -euo pipefail

export PIP_ONLY_BINARY=":all:"
pip install -r testApp1/config/requirements.txt --dry-run 2>&1 | tee /tmp/pip_dry_run.log
if grep -E "Building wheel for|Preparing metadata \(pyproject.toml\)" /tmp/pip_dry_run.log; then
  echo "FAIL: Detected source build preparation in dry run"; exit 1
fi
echo "OK: No source build steps detected in dry run"


