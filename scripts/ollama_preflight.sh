#!/usr/bin/env bash
# Ollama 실행 확인 및 모델 준비 (local-all / up / dev-all 등에서 호출)
# Usage: ollama_preflight.sh [ENV_FILE]
set -euo pipefail

ENV_FILE="${1:-.env.local}"

# OLLAMA_PORT: env 파일에서 읽기, 없으면 기본값 11434
OLLAMA_PORT=$(grep '^OLLAMA_PORT=' "$ENV_FILE" 2>/dev/null | cut -d= -f2 | tr -d '"' | tr -d "'" | xargs || true)
OLLAMA_PORT="${OLLAMA_PORT:-11434}"
OLLAMA_URL="http://localhost:${OLLAMA_PORT}"

# ── 1. Ollama 실행 확인 ───────────────────────────────────────────────────────
if curl -sf "${OLLAMA_URL}/api/tags" >/dev/null 2>&1; then
    echo "✅ Ollama :${OLLAMA_PORT} 이미 실행 중 — Docker Compose 스킵"
elif lsof -i ":${OLLAMA_PORT}" -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "❌ 포트 ${OLLAMA_PORT}이 Ollama 아닌 다른 프로세스에 사용 중"
    lsof -i ":${OLLAMA_PORT}" -sTCP:LISTEN | tail -n +2
    exit 1
else
    echo "🐳 Ollama Docker Compose 기동 중..."
    docker compose --env-file "$ENV_FILE" up -d ollama
    echo "⏳ Ollama 준비 대기 중..."
    for i in $(seq 1 30); do
        if curl -sf "${OLLAMA_URL}/api/tags" >/dev/null 2>&1; then
            echo "✅ Ollama 준비 완료"
            break
        fi
        if [ "$i" -eq 30 ]; then
            echo "❌ Ollama 시작 시간 초과 (60초)"
            exit 1
        fi
        sleep 2
    done
fi

# ── 2. 모델 확인 및 다운로드 ──────────────────────────────────────────────────
if [ ! -f "$ENV_FILE" ]; then
    echo "⚠️  $ENV_FILE 없음 — 모델 확인 스킵"
    exit 0
fi

OLLAMA_MODEL=$(grep '^OLLAMA_MODEL=' "$ENV_FILE" 2>/dev/null | cut -d= -f2 | tr -d '"' | tr -d "'" | xargs || true)

if [ -z "$OLLAMA_MODEL" ]; then
    echo "ℹ️  OLLAMA_MODEL 미설정 — 모델 확인 스킵"
    exit 0
fi

echo "🔍 모델 확인: ${OLLAMA_MODEL}"

TAGS_JSON=$(curl -sf "${OLLAMA_URL}/api/tags" 2>/dev/null || echo '{"models":[]}')
if echo "$TAGS_JSON" | grep -q "\"name\":\"${OLLAMA_MODEL}"; then
    echo "✅ 모델 ${OLLAMA_MODEL} 사용 가능"
else
    echo "⬇️  모델 ${OLLAMA_MODEL} 없음 — 다운로드 중 (시간 소요)..."
    if command -v ollama >/dev/null 2>&1; then
        ollama pull "${OLLAMA_MODEL}"
    else
        docker compose --env-file "$ENV_FILE" exec ollama ollama pull "${OLLAMA_MODEL}"
    fi
    echo "✅ 모델 ${OLLAMA_MODEL} 다운로드 완료"
fi
