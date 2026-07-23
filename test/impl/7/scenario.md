# Phase 8 — MCP server_host + auto-port 테스트 시나리오 (Iteration 7)

## 목적
3개 버그 수정 검증:
1. MCP 가이드 URL이 `localhost` 대신 실제 서버 IP 표시
2. proxy_port 설정 시 URL 형식 = `http://{server_host}:{port}/mcp`
3. 포트 미입력 저장 시 20000-59999 범위 auto-assign (프론트엔드)

## 테스트 케이스

| TC | 설명 | 검증 포인트 |
|----|------|------------|
| TC-7-01 | `server_host` 필드 존재 | guide 응답에 `server_host` 키 포함 |
| TC-7-02 | proxy_port 설정 시 URL = `http://{server_host}:{port}/mcp` | mcp_url이 server_host + port 포함, /mcp 종료 |
| TC-7-03 | proxy_port 없을 때 URL = `http://{server_host}[:{port}]/mcp/{agent_key}` | mcp_url이 server_host + /mcp/{agent_key} 포함 |
| TC-7-04 | `server_host` 값이 유효한 IP 또는 hostname | 빈 문자열이 아님, None이 아님 |
| TC-7-05 | proxy_port mcp_url이 `localhost` 미포함 (server_host가 실IP일 때) | server_host != localhost 이면 mcp_url에 localhost 없음 |
| TC-7-06 | 기존 TC-6-09 회귀: proxy_port=20001 → mcp_url에 "20001" 포함 + /mcp 종료 | 기존 동작 유지 |
| TC-7-07 | 기존 TC-6-10 회귀: proxy_port=null → /mcp/{agent_key} 포함 | 기존 동작 유지 |
