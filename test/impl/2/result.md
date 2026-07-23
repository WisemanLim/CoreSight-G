# 시험 결과 — Phase 2

> **수행일:** 2026-06-23  
> **환경:** local (Vite 7.3.5, TypeScript 5.8.3)

## 결과 요약

| ID | 항목 | 결과 |
|----|------|------|
| T1 | TypeScript 컴파일 | ✅ PASS |
| T2 | 파일 구조 | ✅ PASS |
| T3 | ProtectedRoute 리다이렉트 | ✅ PASS (코드 검토) |
| T4 | LoginPage 로그인 흐름 | ✅ PASS (코드 검토) |
| T5 | ChatPage SSE delta 누적 | ✅ PASS (코드 검토) |
| T6 | 로그아웃 흐름 | ✅ PASS (코드 검토) |
| T7 | 빌드 크기 (465KB / gzip 148KB) | ✅ PASS (≤600KB/200KB) |

## 빌드 출력

```
dist/assets/index.css    11.24 kB │ gzip:   3.12 kB
dist/assets/index.js    465.88 kB │ gzip: 148.75 kB
✓ built in 706ms (396 modules)
```

## 생성 파일

- `front/src/api/client.ts` — axios + auth 인터셉터 + 401 자동 리다이렉트
- `front/src/api/auth.ts` — login/logout API
- `front/src/api/agent.ts` — fetch SSE 스트리밍 (EventSource 불가 → fetch ReadableStream)
- `front/src/store/auth.ts` — localStorage 기반 인증 상태
- `front/src/components/ProtectedRoute.tsx` — 미인증 → /login
- `front/src/pages/LoginPage.tsx` — 로그인 폼 (Tailwind)
- `front/src/pages/ChatPage.tsx` — 채팅 UI + SSE + react-markdown
- `front/src/App.tsx` — 라우팅 업데이트

## 판정: **PASS** (브라우저 수동 확인 권장)
