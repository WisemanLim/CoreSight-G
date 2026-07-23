# 시험 시나리오 — Phase 1 (인증·사용자·설정)

> **차수:** 1  
> **범위:** F5 JWT 인증, F5 RBAC 사용자 관리, F9 시스템 설정

## 시험 항목

| ID | 항목 | 검증 포인트 |
|----|------|------------|
| T1 | DB seed — 기본 관리자 생성 | tbl_users 비어있으면 supervisor 계정 자동 생성 |
| T2 | POST /api/auth/login — 정상 | 200, access_token 반환 |
| T3 | POST /api/auth/login — 잘못된 비밀번호 | 401 반환 |
| T4 | POST /api/auth/login — 없는 사용자 | 401 반환 |
| T5 | GET /api/users/ — 인증 없이 | 403 반환 |
| T6 | GET /api/users/ — supervisor 토큰 | 200, 사용자 목록 반환 |
| T7 | POST /api/users/ — 새 사용자 생성 | 201, user_id 반환 |
| T8 | POST /api/users/ — 중복 user_id | 409 반환 |
| T9 | GET /api/settings/ — 인증 있음 | 200, settings 목록 반환 |
| T10 | POST /api/auth/logout — 토큰 무효화 | 200, 이후 동일 토큰 401 |

## 실행 명령

```bash
uv run pytest test/impl/1/test_phase1.py -v
```
