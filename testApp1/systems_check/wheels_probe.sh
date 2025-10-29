#!/usr/bin/env bash
set -euo pipefail

REQ="${1:-testApp1/config/requirements.txt}"
TMPDIR="$(mktemp -d)"

pip download --only-binary=:all: \
  --platform manylinux2014_x86_64 \
  --python-version 3.12 \
  --implementation cp \
  --abi cp312 \
  -r "$REQ" -d "$TMPDIR"

echo "OK: Wheels resolved to $TMPDIR"


