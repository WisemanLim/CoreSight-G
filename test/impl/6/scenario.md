# Phase 8 — MCP Proxy per-agent 테스트 시나리오 (Iteration 6)

## 대상 기능
- F12 재설계: MCP Proxy per-agent
- tbl_mcp_configs CRUD (`/api/mcp-configs/*`)
- MCP status 엔드포인트 (green/orange/red)
- MCP guide 엔드포인트 (`/mcp/{key}/guide`) + `proxy_port` 반환
- MCP URL 포맷: `http://{host}:{proxy_port}/mcp`
- status 버그 수정: port 미설정 시 red (not green)
- React: `!!` 강제변환 — SQLite 0/1 → boolean (JSX '0' 렌더링 제거)

---

## TC-6-01: tbl_mcp_configs — PUT upsert (생성)

**전제**: board agent 설정 없음  
**실행**: `PUT /api/mcp-configs/board` body `{"port":20001,"extra_args":["--header:x-api-key:tok"]}`  
**기대**: 201/200, `{agent_key:"board", port:20001, extra_args:[...], is_enabled:true}`

## TC-6-02: tbl_mcp_configs — GET 단건

**실행**: `GET /api/mcp-configs/board`  
**기대**: 200, port=20001

## TC-6-03: tbl_mcp_configs — GET 목록

**실행**: `GET /api/mcp-configs/`  
**기대**: 200, `{configs:[...]}` 배열에 board 포함

## TC-6-04: tbl_mcp_configs — PUT upsert (갱신)

**실행**: `PUT /api/mcp-configs/board` body `{"port":20002}`  
**기대**: port=20002로 갱신, extra_args=[]로 초기화

## TC-6-05: tbl_mcp_configs — DELETE

**실행**: `DELETE /api/mcp-configs/board`  
**기대**: 204  
**검증**: `GET /api/mcp-configs/board` → 404

## TC-6-06: MCP status — red (설정 없음)

**전제**: board agent mcp_configs 없음  
**실행**: `GET /api/mcp-configs/board/status`  
**기대**: `{"status":"red","message":"MCP 프록시 미설정"}`

## TC-6-07: MCP status — red (port 미설정)

**전제**: `PUT /api/mcp-configs/board` body `{"port":null,"is_enabled":true}` 저장  
**실행**: `GET /api/mcp-configs/board/status`  
**기대**: `{"status":"red","message":"MCP 프록시 미설정"}` ← 버그 수정 검증

## TC-6-08: MCP status — green (builtin agent, port 설정)

**전제**: `PUT /api/mcp-configs/board` body `{"port":20001}`, board is_enabled=1  
**실행**: `GET /api/mcp-configs/board/status`  
**기대**: `{"status":"green","message":"정상"}`

## TC-6-09: MCP guide — proxy_port 반환

**전제**: board mcp_configs port=20001  
**실행**: `GET /mcp/board/guide`  
**기대**: `proxy_port=20001`, `mcp_url="http://localhost:20001/mcp"`

## TC-6-10: MCP guide — proxy_port null (내장 엔드포인트 폴백)

**전제**: board mcp_configs 없음  
**실행**: `GET /mcp/board/guide`  
**기대**: `proxy_port=null`, `mcp_url` 포함 `"/mcp/board"`

## TC-6-11: MCP status — DELETE 후 red

**실행**: `DELETE /api/mcp-configs/board` 후 `GET /api/mcp-configs/board/status`  
**기대**: `{"status":"red"}`

## TC-6-12: MCP JSON-RPC — per-agent tools/list (builtin)

**실행**: `POST /mcp/board` body `{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}`  
**기대**: `{"result":{"tools":[]}}` (builtin = tool 없음)

## TC-6-13: MCP JSON-RPC — initialize

**실행**: `POST /mcp/board` body `{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}`  
**기대**: `protocolVersion`, `serverInfo.name` 포함

## TC-6-14: '0' 렌더링 버그 — SQLite boolean 강제변환

**검증**: AgentsPage에서 비활성 내장 에이전트 옆에 '0' 미표시  
**방법**: `is_enabled=0` agent가 있을 때 ReactDOM 렌더링에 `!!` 강제변환 코드 존재 확인  
**기대**: `!!c.is_enabled && <McpControls>` 패턴 코드 존재

## TC-6-15: MCP configs — 404 on missing GET

**실행**: `GET /api/mcp-configs/nonexistent_key`  
**기대**: 404

## TC-6-16: MCP configs — 권한 확인 (PUT requires admin+)

**실행**: user 토큰으로 `PUT /api/mcp-configs/board`  
**기대**: 403
