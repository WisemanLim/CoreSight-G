# Phase 5 시험 시나리오 — F12 Standalone Agent A2A/MCP + Agent Registry

**구현 범위:** F12 — A2A Protocol v1.0 · MCP JSON-RPC 2.0 · Agent Registry CRUD

**활성화 방법:** `AGENT_EXPOSE_PROTOCOL=a2a,mcp` 환경변수 설정 시 메인 앱에 포함 (Hybrid 모드)

---

## MCP JSON-RPC 2.0

### T1: /mcp — initialize

| 항목 | 내용 |
|------|------|
| 대상 | `POST /mcp` |
| Body | `{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}` |
| 기댓값 | 200, `result.protocolVersion = "2025-11-05"`, `result.capabilities` 포함 |

### T2: /mcp — tools/list

| 항목 | 내용 |
|------|------|
| 대상 | `POST /mcp` |
| Body | `{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}` |
| 기댓값 | `result.tools` 배열, ExampleAgent 도구 목록 |

### T3: /mcp — tools/call

| 항목 | 내용 |
|------|------|
| 대상 | `POST /mcp` |
| Body | `{"method":"tools/call","params":{"name":"get_example_data","arguments":{"query":"test"}}}` |
| 기댓값 | `result.content[0].type = "text"` |

### T4: /mcp — tools/call unknown tool

| 항목 | 내용 |
|------|------|
| 대상 | `POST /mcp` |
| Body | `{"method":"tools/call","params":{"name":"nonexistent","arguments":{}}}` |
| 기댓값 | `error.code = -32602` |

### T5: /mcp — resources/list

| 항목 | 내용 |
|------|------|
| 기댓값 | `result.resources[0].uri = "domain://context"` |

### T6: /mcp — resources/read

| 항목 | 내용 |
|------|------|
| Body | `{"method":"resources/read","params":{"uri":"domain://context"}}` |
| 기댓값 | `result.contents[0].uri = "domain://context"` |

### T7: /mcp — prompts/list + prompts/get

| 항목 | 내용 |
|------|------|
| list 기댓값 | `result.prompts[0].name = "system"` |
| get 기댓값 | `result.messages[0].role = "user"` |

### T8: /mcp — unknown method → -32601

---

## A2A Protocol

### T9: /.well-known/agent-card.json

| 항목 | 내용 |
|------|------|
| 대상 | `GET /.well-known/agent-card.json` — 인증 불필요 |
| 기댓값 | `capabilities.streaming = true`, `skills` 배열 |

### T10: POST /a2a/tasks → 201 + task_id

| 항목 | 내용 |
|------|------|
| 대상 | `POST /a2a/tasks` (Bearer) |
| Body | `{"message":{"role":"user","parts":[{"kind":"text","text":"테스트"}]}}` |
| 기댓값 | 201, `id` 존재, `status = "submitted"` |

### T11: GET /a2a/tasks/{id}/result → 완료 확인

| 항목 | 내용 |
|------|------|
| 대상 | `GET /a2a/tasks/{id}/result` |
| 기댓값 | 200, `id` 일치 |

### T12: GET /a2a/tasks — 없는 task_id → 404

---

## Agent Registry

### T13: GET /api/agent-registry/ → 목록 (비어있음)

### T14: POST /api/agent-registry/ → 외부 Agent 등록

| Body | `{agent_key: "remote_test", agent_name: "Remote", protocol: "a2a", agent_card_url: "http://localhost:9999/agent"}` |
|------|------|
| 기댓값 | 201 |

### T15: POST /api/agent-registry/ 중복 → 409

### T16: GET /api/agent-registry/ → 등록된 Agent 확인

### T17: POST /api/agent-registry/{key}/ping → 연결 실패 (URL 없음)

### T18: DELETE /api/agent-registry/{key} → 200

### T19: viewer 권한 Registry 접근 → 403
