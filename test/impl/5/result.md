# Phase 5 시험 결과

**판정: PASS**  
**실행일:** 2026-06-24  
**범위:** F12 — MCP JSON-RPC 2.0 · A2A Protocol v1.0 · Agent Registry

---

## 결과 요약

| 시험 | 설명 | 판정 |
|------|------|------|
| T1 | MCP initialize → protocolVersion + capabilities | PASS |
| T2 | MCP tools/list → ExampleAgent 도구 목록 | PASS |
| T3 | MCP tools/call → content[0].type = text | PASS |
| T4 | MCP tools/call 없는 도구 → -32602 | PASS |
| T5 | MCP resources/list → domain://context | PASS |
| T6 | MCP resources/read → contents[0].uri | PASS |
| T7 | MCP prompts/list + prompts/get → system prompt | PASS |
| T8 | MCP 없는 method → -32601 | PASS |
| T9 | AgentCard — 인증 불필요, capabilities.streaming=true | PASS |
| T10 | A2A POST /a2a/tasks → 201, status=submitted | PASS |
| T11 | A2A GET /a2a/tasks/{id}/result → id 일치 | PASS |
| T12 | A2A 없는 task_id → 404 | PASS |
| T13 | Registry 빈 목록 조회 | PASS |
| T14 | Registry 외부 Agent 등록 → 201 | PASS |
| T15 | Registry 중복 등록 → 409 | PASS |
| T16 | Registry 등록 후 목록 확인 | PASS |
| T17 | Registry ping (URL 없음) → ok=false | PASS |
| T18 | Registry 삭제 → 200 | PASS |
| T19 | viewer Registry 접근 → 403 | PASS |

**19/19 PASS** · 회귀 없음 (Phase 1+3+4+5 = 64/64)  
실행 시간: 2.56s (Phase 5 단독) / 10.87s (전체)

---

## 구현 파일

| 파일 | 역할 |
|------|------|
| `app/routers/router_a2a.py` | A2A Protocol v1.0 (AgentCard, Task 생성/스트림/결과) |
| `app/routers/router_mcp.py` | MCP JSON-RPC 2.0 (initialize/tools/resources/prompts) |
| `app/routers/router_agent_registry.py` | 외부 Agent 등록·삭제·ping |
| `app/main.py` | 3개 라우터 등록 |
| `standalone/standalone_app.py` | Standalone 모드 실행 앱 (A2A+MCP 포함) |
