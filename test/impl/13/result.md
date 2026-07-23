# Phase 14 — LLM 설정 우선순위 버그 수정 결과 (Iteration 13)

## 판정: PASS ✅

| TC | 시나리오 | 결과 |
|----|---------|------|
| TC-13-01 | .env 값이 기본값과 다를 때 DB 덮어쓰기 | ✅ PASS |
| TC-13-02 | .env 값이 기본값과 같으면 DB 값 유지 | ✅ PASS |
| TC-13-03 | os.environ 명시 시 최우선 | ✅ PASS |
| TC-13-04 | DB 없고 .env 기본값 → 기본값 반환 | ✅ PASS |
| TC-13-05 | syntax 오류 없음 | ✅ PASS |
| TC-13-06 | _db_llm_settings 실제 실행 (DB fetch 모킹) | ✅ PASS |

**6/6 PASS** (0.36s)

## 수정 내용

`app/agents/orchestrator.py` `_db_llm_settings()` 우선순위 수정:

| 우선순위 | 이전 | 수정 후 |
|---------|------|--------|
| 1 (최우선) | os.environ | os.environ (Docker) |
| 2 | DB (tbl_settings) | .env.* 파일 (pydantic, 기본값과 다를 때) |
| 3 | - | DB (tbl_settings, UI 설정) |
| 4 | 기본값 | 기본값 |

### 핵심 로직

pydantic-settings는 `.env.*` 파일을 settings 객체에만 로드하고 `os.environ`에 주입하지 않음.
따라서 `settings.ollama_model` 값이 pydantic 기본값(`llama3.2`)과 다르면 `.env.*`에서
명시 설정된 것으로 판단하여 DB 값을 덮어씀.
