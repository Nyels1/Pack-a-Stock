#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/root/pack-a-stock-prod/Pack-a-Stock}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.ionos.yml}"
ENV_FILE="${ENV_FILE:-.env.prod}"
PROJECT_NAME="${PROJECT_NAME:-pack-a-stock}"

if docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD=(docker-compose)
else
  echo "[recover] ERROR: docker compose is not available"
  exit 1
fi

compose() {
  DOCKER_BUILDKIT=0 COMPOSE_DOCKER_CLI_BUILD=0 \
    "${COMPOSE_CMD[@]}" \
    -p "${PROJECT_NAME}" \
    --env-file "${ENV_FILE}" \
    -f "${COMPOSE_FILE}" "$@"
}

echo "[recover] App dir: ${APP_DIR}"
cd "${APP_DIR}"

echo "[recover] Memory before recovery"
free -h

echo "[recover] Stopping optional heavy services (if present)"
docker stop pas_jenkins pas_netdata >/dev/null 2>&1 || true

echo "[recover] Ensuring compose contexts are correct"
sed -i 's|context: ./Pack-a-Stock$|context: .|' "${COMPOSE_FILE}"
sed -i 's|context: ./Pack-a-Stock_React$|context: ../Pack-a-Stock_React|' "${COMPOSE_FILE}"
grep -n "context:" "${COMPOSE_FILE}"

AVAILABLE_MIB="$(free -m | awk '/Mem:/ {print $7}')"
if [[ "${AVAILABLE_MIB}" -lt 350 ]]; then
  echo "[recover] Low available memory detected (${AVAILABLE_MIB} MiB). Enabling extra swap if available"
  if [[ -f /swapfile2 ]]; then
    swapon /swapfile2 >/dev/null 2>&1 || true
  fi
fi

echo "[recover] Starting database"
compose up -d db

for i in $(seq 1 30); do
  DB_HEALTH="$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' pas_db 2>/dev/null || echo "unknown")"
  if [[ "${DB_HEALTH}" == "healthy" || "${DB_HEALTH}" == "running" ]]; then
    echo "[recover] Database is ${DB_HEALTH}"
    break
  fi

  if [[ "${i}" -eq 30 ]]; then
    echo "[recover] ERROR: database did not become healthy"
    docker logs --tail=120 pas_db || true
    exit 1
  fi

  sleep 2
done

echo "[recover] Building and starting backend"
compose up -d --build backend

echo "[recover] Stopping backend temporarily to free RAM for frontend build"
compose stop backend || true

echo "[recover] Building frontend"
compose build frontend

echo "[recover] Starting backend and frontend"
compose up -d backend frontend

echo "[recover] Final status"
compose ps

echo "[recover] Backend health check"
for i in $(seq 1 30); do
  if docker exec pas_backend python - <<'PY'
import sys
from urllib.request import urlopen

resp = urlopen('http://127.0.0.1:8000/admin/login/', timeout=3)
sys.exit(0 if 200 <= resp.status < 400 else 1)
PY
  then
    echo "[recover] Backend check OK"
    break
  fi

  if [[ "${i}" -eq 30 ]]; then
    echo "[recover] ERROR: backend health check failed"
    docker logs --tail=120 pas_backend || true
    exit 1
  fi

  sleep 2
done

echo "[recover] Frontend health check"
for i in $(seq 1 30); do
  if docker exec pas_frontend node -e "fetch('http://127.0.0.1:3000').then(r=>process.exit((r.status>=200&&r.status<400)?0:1)).catch(()=>process.exit(1))"
  then
    echo "[recover] Frontend check OK"
    break
  fi

  if [[ "${i}" -eq 30 ]]; then
    echo "[recover] ERROR: frontend health check failed"
    docker logs --tail=120 pas_frontend || true
    exit 1
  fi

  sleep 2
done

echo "[recover] DONE"
