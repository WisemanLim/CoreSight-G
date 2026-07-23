# MCP Prod Fix — 시험 시나리오 및 결과

## 목적

Docker Compose(dev/staging/prod) 환경에서 발생하는 MCP 설정 오류 수정 및 검증.

## 변경 사항

| 파일 | 변경 내용 |
|------|-----------|
| `sql/sqlite/` | SQLite 전용 SQL (`AUTOINCREMENT`, `INSERT OR IGNORE`) |
| `sql/pg/` | PostgreSQL 전용 SQL (`SERIAL`, `ON CONFLICT DO NOTHING`) |
| `docker-compose.yml` | `initdb.d` 마운트 경로 `./sql` → `./sql/pg` |
| `app/db.py` | `run_migrations()` — dialect별 SQL 디렉터리 선택, PG column migration 추가 |
| `app/core/config.py` | `MCP_HOST` 환경변수 추가 (Docker/NAT 환경 호스트 명시) |
| `app/routers/router_mcp.py` | `_get_server_host()` — `MCP_HOST` 우선 사용, `mcp_guide()` 호스트 고정 |
| `front/nginx.conf` | `/mcp` location 추가 → `proxy_pass http://api:8000` |
| `front/Dockerfile` | `--frozen-lockfile`, `CI=true` 빌드 안정화 |
| `Dockerfile` | `uv.lock` 복사, `uv sync --frozen` 두 단계 빌드 |
| `front/src/pages/agents/AgentsPage.tsx` | Toggle ON/OFF pill UI (orange 배경) |

## 핵심 문제 및 해결

### 1. SQL 방언 충돌

- **문제**: `sql/01_init.sql`의 `AUTOINCREMENT`, `INSERT OR IGNORE`를 PostgreSQL `initdb.d`가 실행 → 오류
- **해결**: `sql/sqlite/` + `sql/pg/` 분리, `docker-compose.yml`은 `sql/pg/`만 마운트

### 2. Docker 내부 MCP URL 오류

- **문제**: `_get_server_host()`가 컨테이너 내부 IP(172.x.x.x) 반환 → 외부에서 접근 불가
- **해결**: `MCP_HOST` env var 설정 시 해당 값 우선 사용 (호스트 IP 또는 도메인 명시)

### 3. nginx MCP 라우팅 누락

- **문제**: Docker Compose에서 nginx가 `/api/` 만 프록시 → `/mcp` 요청 404
- **해결**: `front/nginx.conf`에 `/mcp` location 추가

## 시험 실행

```bash
uv run pytest -q
```

## 결과

| 구분 | 수 |
|------|-----|
| 통과 | 80 |
| 실패 | 7 (pre-existing, phase3 seed 데이터 불일치) |
| 경고 | 1 (duplicate operation ID — pre-existing) |

### 통과 (MCP 관련)

- `test/impl/5/` — A2A · MCP JSON-RPC 2.0 · Agent Registry 전체 통과

### 실패 (Pre-existing, 이번 변경과 무관)

| 테스트 | 원인 |
|--------|------|
| `test_t6_list_agent_config` | 시드에서 `example` agent 삭제됨 |
| `test_t7/t8/t9_patch_agent_*` | `example` agent 없음 → 404 |
| `test_t10_list_addons_empty` | `board` builtin addon이 시드에 포함됨 |
| `test_t12_list_addons_after_upload` | `board` + upload = 2건 (1건 기대) |
| `test_t16_list_addons_after_delete` | `board` 남아서 빈 배열 아님 |

## 환경별 MCP 설정 가이드

### local (SQLite, 직접 실행)

MCP URL 자동 감지 — 추가 설정 불필요.

### dev/staging/prod (Docker Compose)

`.env.dev` (또는 `.env.staging`, `.env.prod`)에 추가:

```bash
MCP_HOST=192.168.1.100   # 실제 호스트 IP 또는 도메인
```

docker-compose.yml `api` 서비스 environment에도 반영:

```yaml
- MCP_HOST=${MCP_HOST:-}
```
