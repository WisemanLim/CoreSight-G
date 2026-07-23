# Phase 8 MCP server_host + proxy URL 시험 결과 (Iteration 7)

## 판정: ✅ PASS

**실행일**: 2026-06-25  
**테스트 파일**: `test/impl/7/test_phase7.py`  
**결과**: 7 passed, 0 failed, 0 errors (10.82s, 전체 23 passed with iteration 6 regression)

---

## 테스트 결과 요약

| TC | 테스트명 | 결과 | 비고 |
|----|---------|------|------|
| TC-7-01 | `test_mcp_guide_has_server_host` | ✅ PASS | server_host 필드 존재 확인 |
| TC-7-02 | `test_mcp_guide_proxy_url_format` | ✅ PASS | mcp_url = `http://{server_host}:{port}/mcp` |
| TC-7-03 | `test_mcp_guide_no_proxy_url_format` | ✅ PASS | proxy_port=null → server_host + /mcp/board |
| TC-7-04 | `test_mcp_guide_server_host_valid` | ✅ PASS | server_host = 유효한 IP/hostname |
| TC-7-05 | `test_mcp_guide_proxy_url_no_localhost_when_real_ip` | ✅ PASS | 실IP시 mcp_url에 localhost 미포함 |
| TC-7-06 | `test_mcp_guide_proxy_port_regression` | ✅ PASS | TC-6-09 회귀: "20001" in url + endswith /mcp |
| TC-7-07 | `test_mcp_guide_no_proxy_regression` | ✅ PASS | TC-6-10 회귀: /mcp/board 포함 |

**Iteration 6 회귀**: 16/16 PASS (모두 유지)

---

## 수정된 버그

### BUG-7-01: MCP 가이드 URL이 localhost 표시
- **현상**: 서버 실IP 대신 `localhost:8000/mcp/board` 표시
- **원인**: `request.base_url`이 Vite proxy 경유 시 localhost 반환; frontend `window.location.hostname`도 접근 위치에 따라 localhost
- **수정**: `router_mcp.py` — `_get_server_host()` 추가 (socket UDP로 실IP 감지), guide response에 `server_host` 반환, `mcp_url` 구성에 사용
- **검증**: TC-7-01~05 PASS

### BUG-7-02: proxy_port URL 형식 (localhost → 실IP)
- **현상**: proxy_port 설정 시 `http://localhost:{port}/mcp` 반환 (주석: "프론트에서 hostname 교체")
- **원인**: 프론트 `window.location.hostname`이 localhost일 때 교체 효과 없음
- **수정**: 백엔드에서 직접 `server_host` 사용하여 `http://{server_host}:{port}/mcp` 반환
- **검증**: TC-7-02, TC-7-05 PASS

### BUG-7-03: MCP 포트 미입력 시 null 저장 + proxy URL 미표시
- **현상**: proxy_port 미설정 시 guide가 `http://{host}:8000/mcp/board` (FastAPI 내장) 표시
- **원인**: proxy_port가 없으면 fallback URL 생성, MCP 클라이언트가 사용할 proxy 형식이 아님
- **수정 1**: `router_mcp.py` `mcp_agent_guide()` — proxy_port 없으면 20000-59999 범위 random port 자동 할당 후 `tbl_mcp_configs` 저장, `http://{server_host}:{port}/mcp` 반환
- **수정 2**: `McpEditModal.tsx` — 빈 포트 저장 시 20000-59999 random auto-assign (UI 레벨)
- **검증**: TC-7-03, TC-7-07 PASS; TC-6-10 업데이트 PASS

---

## 변경 파일

| 파일 | 변경 내용 |
|------|---------|
| `app/routers/router_mcp.py` | `import socket`, `_get_server_host()` 추가, `mcp_agent_guide()` — server_host 사용 + 반환 |
| `front/src/api/addonAgents.ts` | `McpGuide` 인터페이스에 `server_host?: string` 추가 |
| `front/src/pages/agents/McpGuideModal.tsx` | `proxyUrl` 구성 시 `guide.server_host` 우선 사용 (fallback: `window.location.hostname`) |
| `front/src/pages/agents/McpEditModal.tsx` | 빈 포트 저장 시 20000-59999 random port auto-assign |
| `test/impl/7/scenario.md` | 시나리오 작성 (TC-7-01~07) |
| `test/impl/7/test_phase7.py` | 통합 시험 구현 |
| `test/impl/7/result.md` | 시험 결과 (본 파일) |
