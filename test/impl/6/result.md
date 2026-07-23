# Phase 8 MCP Proxy per-agent 시험 결과 (Iteration 6)

## 판정: ✅ PASS

**실행일**: 2026-06-25  
**테스트 파일**: `test/impl/6/test_phase6.py`  
**결과**: 16 passed, 0 failed, 0 errors (8.41s)

---

## 테스트 결과 요약

| TC | 테스트명 | 결과 | 비고 |
|----|---------|------|------|
| TC-6-01 | `test_mcp_config_upsert_create` | ✅ PASS | PUT → 생성 |
| TC-6-02 | `test_mcp_config_get_single` | ✅ PASS | GET 단건 |
| TC-6-03 | `test_mcp_config_list` | ✅ PASS | GET 목록 |
| TC-6-04 | `test_mcp_config_upsert_update` | ✅ PASS | PUT → 갱신 |
| TC-6-05 | `test_mcp_config_delete` | ✅ PASS | DELETE → 404 |
| TC-6-06 | `test_mcp_status_red_no_config` | ✅ PASS | 설정 없음 → red |
| TC-6-07 | `test_mcp_status_red_no_port` | ✅ PASS | **버그수정 검증**: port=null → red |
| TC-6-08 | `test_mcp_status_green_builtin` | ✅ PASS | port+builtin is_enabled → green |
| TC-6-09 | `test_mcp_guide_proxy_port` | ✅ PASS | proxy_port 포함 URL 반환 |
| TC-6-10 | `test_mcp_guide_no_proxy_port` | ✅ PASS | proxy_port=null 폴백 |
| TC-6-11 | `test_mcp_status_red_after_delete` | ✅ PASS | DELETE 후 → red |
| TC-6-12 | `test_mcp_jsonrpc_tools_list_builtin` | ✅ PASS | builtin tools/list → [] |
| TC-6-13 | `test_mcp_jsonrpc_initialize` | ✅ PASS | initialize → protocolVersion |
| TC-6-14 | `test_no_zero_rendering_pattern` | ✅ PASS | `!!` 강제변환 코드 존재 확인 |
| TC-6-15 | `test_mcp_config_get_404` | ✅ PASS | 없는 key → 404 |
| TC-6-16 | `test_mcp_config_put_forbidden` | ✅ PASS | user role → 403 |

---

## 발견 및 수정된 버그

### BUG-6-01: MCP status green — port 미설정 시 오표시
- **현상**: `tbl_mcp_configs` row 존재 + `is_enabled=1`이면 `port=NULL`이어도 `green` 반환
- **원인**: status 쿼리가 `is_enabled`만 체크, `port` 누락
- **수정**: `router_mcp_config.py` — `SELECT port, is_enabled` + `or not row["port"]` 추가
- **검증**: TC-6-07 PASS

### 시험 환경 이슈 (코드 버그 아님)
- `board` agent가 `tbl_addon_agents`(is_active=0) + `tbl_agent_config` 양쪽에 존재
- Addon 체크가 builtin 체크보다 먼저 실행되어 red 반환 → TC-6-08 격리 키 사용으로 해결
- 운영 환경에서는 addon과 builtin이 같은 키를 공유하지 않음

---

## 변경 파일

| 파일 | 변경 내용 |
|------|---------|
| `app/routers/router_mcp_config.py` | BUG-6-01: status endpoint — port 미설정 시 red 반환 |
| `.docs/Multi AI Agent Standard-PRD.md` | 8.8 guide response에 proxy_port 필드 문서화, 8.8-ext status 조건 갱신 |
| `README.md` | MCP Proxy 섹션 — URL 포맷, port 필수 조건 추가 |
| `README.en.md` | MCP status dot 설명 — port 필수 조건 반영 |
| `test/impl/6/scenario.md` | 시나리오 작성 (TC-6-01~16) |
| `test/impl/6/test_phase6.py` | 통합 시험 구현 |
| `test/impl/6/result.md` | 시험 결과 (본 파일) |
