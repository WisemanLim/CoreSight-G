# 표준 환경 검증 시나리오 — dev-env

> 목적: 의존성 설치 + 인프라 기동 + 핵심 API 동작 확인 (최초 1회 수행)

## 전제 조건

- [ ] Python 3.12+ 설치 (`python --version`)
- [ ] uv 설치 (`uv --version`)
- [ ] Docker Desktop 실행 중
- [ ] Node.js 20+ + pnpm 설치 (`node -v`, `pnpm -v`)

## 시험 절차

### S1. 의존성 설치

```bash
uv sync
cd front && pnpm install && cd ..
```

**기대**: 오류 없이 완료

---

### S2. 인프라 기동 (postgres + redis + ollama)

```bash
make up
docker compose ps
```

**기대**: postgres, redis, ollama 3개 서비스 `Up` 상태

---

### S3. 백엔드 기동

```bash
make dev-be &
sleep 3
curl http://localhost:8000/health
```

**기대**:
```json
{"status":"ok","env":"local","mode":"embedded"}
```

---

### S4. 데이터베이스 연결

```bash
uv run python -c "
import sqlite3
conn = sqlite3.connect('local.db')
tables = conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()
print([t[0] for t in tables])
"
```

**기대**: `['tbl_users', 'tbl_agent_config', 'tbl_addon_agents', 'tbl_settings', ...]`

---

### S5. 프론트엔드 기동

```bash
cd front && pnpm dev &
sleep 5
curl -I http://localhost:4100
```

**기대**: HTTP 200

---

### S6. pytest 기본 통과

```bash
make test
```

**기대**: `0 failed` (stub 단계 — 실제 테스트는 impl/1/ 에서 추가)

---

## 결과 기록

| 단계 | 결과 | 비고 |
|------|------|------|
| S1 의존성 설치 | ⬜ | |
| S2 인프라 기동 | ⬜ | |
| S3 백엔드 헬스체크 | ⬜ | |
| S4 DB 연결 | ⬜ | |
| S5 프론트엔드 | ⬜ | |
| S6 pytest | ⬜ | |
