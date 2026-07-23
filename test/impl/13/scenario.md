# Phase 14 — LLM 설정 우선순위 버그 수정 (Iteration 13)

## 목적

`_db_llm_settings()` 우선순위 오류 수정:
- 기존: os.environ > DB (pydantic .env.* 파일 값 무시)
- 수정: os.environ > .env.* 파일(pydantic) > DB > 기본값

## 테스트 케이스

| TC | 시나리오 | 예상 결과 |
|----|---------|---------|
| TC-13-01 | .env.* 값이 기본값과 다를 때 DB 값 덮어쓰기 | pydantic 값 우선 |
| TC-13-02 | .env.* 값이 기본값과 같을 때 DB 값 유지 | DB 값 유선 |
| TC-13-03 | os.environ 명시 시 .env 값 덮어쓰기 | os.environ 최우선 |
| TC-13-04 | DB에 값 없고 .env 기본값 → settings 기본값 반환 | 빈 dict 또는 기본값 |
| TC-13-05 | syntax/import 오류 없음 | ast.parse OK |
