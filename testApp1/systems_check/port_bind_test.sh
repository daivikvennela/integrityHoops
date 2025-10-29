#!/usr/bin/env bash
set -euo pipefail

export PORT="${PORT:-5000}"
cd testApp1
timeout 10s bash -c "gunicorn --bind 0.0.0.0:${PORT} src.core.app:app & sleep 2; curl -fsS http://127.0.0.1:${PORT}/healthz > /dev/null"
echo "OK: gunicorn bound and /healthz responded"


