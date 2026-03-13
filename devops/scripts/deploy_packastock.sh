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
curl -fsS http://127.0.0.1:8001/admin/login/ >/dev/null
curl -fsS http://127.0.0.1:3003 >/dev/null

echo "[deploy] OK"
