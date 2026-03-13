#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/srv/pack-a-stock-prod}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.ionos.yml}"

if docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD=(docker-compose)
else
  echo "[deploy] ERROR: docker compose is not available in Jenkins runtime"
  exit 1
fi

echo "[deploy] Project root: ${PROJECT_ROOT}"

if [[ "${SKIP_PULL:-false}" != "true" ]]; then
  echo "[deploy] Pulling latest backend repo"
  cd "${PROJECT_ROOT}/Pack-a-Stock"
  git pull --ff-only

  echo "[deploy] Pulling latest frontend repo"
  cd "${PROJECT_ROOT}/Pack-a-Stock_React"
  git pull --ff-only
fi

cd "${PROJECT_ROOT}"

echo "[deploy] Building backend and frontend images"
"${COMPOSE_CMD[@]}" -f "${COMPOSE_FILE}" build backend frontend

echo "[deploy] Updating running services"
"${COMPOSE_CMD[@]}" -f "${COMPOSE_FILE}" up -d backend frontend

echo "[deploy] Current service status"
"${COMPOSE_CMD[@]}" -f "${COMPOSE_FILE}" ps

echo "[deploy] Health checks"
for i in $(seq 1 30); do
  if docker exec pas_backend python - <<'PY'
import sys
from urllib.request import urlopen

resp = urlopen('http://127.0.0.1:8000/admin/login/', timeout=3)
sys.exit(0 if 200 <= resp.status < 400 else 1)
PY
  then
    echo "[deploy] Backend check OK"
    break
  fi

  if [[ "$i" -eq 30 ]]; then
    echo "[deploy] ERROR: backend health check failed"
    exit 1
  fi

  sleep 2
done

for i in $(seq 1 30); do
  if docker exec pas_frontend node -e "fetch('http://127.0.0.1:3000').then(r=>process.exit((r.status>=200&&r.status<400)?0:1)).catch(()=>process.exit(1))"
  then
    echo "[deploy] Frontend check OK"
    break
  fi

  if [[ "$i" -eq 30 ]]; then
    echo "[deploy] ERROR: frontend health check failed"
    exit 1
  fi

  sleep 2
done

echo "[deploy] OK"
