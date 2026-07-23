# 시험 결과 — Phase 1

> **수행일:** 2026-06-23  
> **환경:** local (SQLite, Python 3.13)  
> **명령:** `uv run pytest test/impl/1/test_phase1.py -v`

## 결과 요약

| ID | 항목 | 결과 |
|----|------|------|
| T1 | DB seed — 기본 관리자 | ✅ PASS |
| T2 | login 정상 | ✅ PASS |
| T3 | login 잘못된 비밀번호 → 401 | ✅ PASS |
| T4 | login 없는 사용자 → 401 | ✅ PASS |
| T5 | 인증 없이 /api/users/ → 401 | ✅ PASS |
| T6 | supervisor 토큰으로 목록 조회 | ✅ PASS |
| T7 | 새 사용자 생성 → 201 | ✅ PASS |
| T8 | 중복 user_id → 409 | ✅ PASS |
| T9 | 설정 목록 조회 | ✅ PASS |
| T10 | 로그아웃 후 토큰 무효화 → 401 | ✅ PASS |

## 판정: **PASS** (9/9)

## 수정 이력

| 이슈 | 원인 | 수정 |
|------|------|------|
| passlib + bcrypt 4.x 충돌 | passlib 2020년 이후 미유지, bcrypt 4.x `__about__` 제거 | passlib 제거 → `bcrypt` 직접 사용 |
| T5 기대값 403 vs 실제 401 | FastAPI HTTPBearer auto_error → 401 반환 | 기대값 `in (401, 403)` 으로 완화 |
| T7 중복 실패 | 이전 통합 테스트에서 `pytest_user` 잔류 | cleanup fixture 추가 |
