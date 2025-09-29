#!/usr/bin/env bash
set -Eeuo pipefail
cd /home/su/api-factory-automation

echo "== docker compose ps =="
docker compose ps || true
echo

echo "== Puertos escuchando (host) =="
ss -ltnp | grep ':8000' || echo 'No hay nada en 8000'
echo

echo "== Logs API (ultimas 120 líneas) =="
docker compose logs --no-color --tail=120 api || true
echo

echo "== Curl verbose /health =="
curl -v http://localhost:8000/health || true
echo

echo "== Curl con headers /health =="
curl -i http://localhost:8000/health || true
echo

echo "== Probar desde dentro del contenedor =="
docker compose exec api sh -lc 'wget -qO- http://127.0.0.1:8000/health || true' || true
echo
