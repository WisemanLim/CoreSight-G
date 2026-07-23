# Phase 9 F22 Agent 카탈로그 시험 시나리오 (Iteration 8)

## 목적

F22 Agent 카탈로그 시스템 구현 검증:
- BUG-v1.4-01 수정: `sql_path` DB 저장 확인
- `agent_type` + `meta_json` 컬럼 마이그레이션
- ZIP 업로드 시 `-meta.json` 파싱 → `agent_type` 저장
- `/api/addon-agents/catalog` — 유형별 그룹핑
- `/api/addon-agents/scaffold` — 스캐폴딩 ZIP 생성

## 사전 조건

- 서버 실행: `uv run uvicorn app.main:app --port 8000`
- 환경: SQLite local `.env.local`
- 인증 토큰: admin 계정 로그인 필요

## 테스트 케이스

| TC | 시나리오 | 예상 결과 |
|----|---------|---------|
| TC-8-01 | `/api/addon-agents/` 목록 — agent_type 필드 포함 | 각 항목에 `agent_type` 필드 존재 |
| TC-8-02 | `/api/addon-agents/catalog` — 전체 카탈로그 | `groups` 딕셔너리 + `total`, `items` 반환 |
| TC-8-03 | `/api/addon-agents/catalog?agent_type=app` — 필터 | app 유형 항목만 반환 |
| TC-8-04 | `/api/addon-agents/templates/list` — 유형 정보 포함 | 각 템플릿에 `agent_type`, `description` 필드 |
| TC-8-05 | `/api/addon-agents/scaffold` Board 유형 — ZIP 반환 | Content-Type: application/zip |
| TC-8-06 | scaffold — 잘못된 agent_name (숫자 시작) | 400 오류 |
| TC-8-07 | scaffold — 잘못된 agent_type | 400 오류 |
| TC-8-08 | scaffold ZIP 내용 확인 — meta.json + app.py | ZIP에 두 파일 모두 포함 |
| TC-8-09 | Board ZIP 업로드 → agent_type=app 저장 확인 | 업로드 응답에 `agent_type: "app"` |
| TC-8-10 | ServiceAgent ZIP 업로드 → agent_type=service 저장 | 업로드 응답에 `agent_type: "service"` |
| TC-8-11 | sql_path 저장 확인 — SQL 있는 ZIP 업로드 시 | DB에 sql_path 비어있지 않음 |
| TC-8-12 | catalog type filter 무효값 — 전체 반환 | 필터 무시하고 전체 반환 |
