# 시험 시나리오 — Phase 2 (프론트엔드 UI)

> **차수:** 2  
> **범위:** F5 로그인 UI, F6 채팅 UI, 인증 라우팅

## 시험 항목

| ID | 항목 | 검증 방법 |
|----|------|----------|
| T1 | TypeScript 컴파일 | `pnpm build` 오류 없음 |
| T2 | 파일 구조 | 필수 파일 모두 존재 |
| T3 | ProtectedRoute — 미인증 시 /login 리다이렉트 | 코드 검토 |
| T4 | LoginPage — 폼 제출 → login() → setAuth() → /chat 이동 | 코드 검토 |
| T5 | ChatPage — SSE 스트리밍 delta 이벤트 누적 | 코드 검토 |
| T6 | 로그아웃 → clearAuth() → /login 이동 | 코드 검토 |
| T7 | 브라우저 빌드 크기 (JS ≤ 600KB gzip ≤ 200KB) | 빌드 출력 확인 |

## 수동 확인 (브라우저 필요)

```bash
make dev-be &   # :8000
make dev-fe     # :4100
# → http://localhost:4100 접속
# → /login 리다이렉트 확인
# → admin / Admin123! 로그인
# → /chat 진입 확인
# → 메시지 전송 → SSE 스트리밍 응답 확인
# → 로그아웃 → /login 리다이렉트 확인
```

## 실행 명령

```bash
cd front && pnpm build   # T1, T7
```
