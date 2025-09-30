#!/usr/bin/env bash
set -Eeuo pipefail
PORT="${PORT:-8080}"
HOST="${HOST:-0.0.0.0}"
echo "🚀 Starting Uvicorn on $HOST:$PORT"
exec python -m uvicorn app.main:app --host "$HOST" --port "$PORT"
