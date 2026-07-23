# 시험 시나리오 — Iteration 31: 채팅 "에이전트 목록" 응답에 ADDON 에이전트 누락 수정

## 증상
사용자 보고: 채팅에서 "에이전트 목록을 보여줘" 요청 시 기본 Agent·관제 Agent(GPU/HW)만 응답,
ADDON 에이전트(로그 분석·트레이스 분석 등 9종)는 목록에서 완전히 누락됨.

## 원인 ①(주 버그) — Addon 목록 누락
`app/rules/keyword_matcher.py` 의 `agent_list` 규칙이 `GET /api/agent-config/`(tbl_agent_config,
기본+내장 관제 Agent만 포함) 만 조회. Iteration 23 결정(P1+ Addon 은 tbl_agent_config 미등록)
이후 이 포맷터가 갱신되지 않아 Addon 목록이 항상 빠짐.

## 원인 ②(부수 버그, 조사 중 발견) — Addon 재업로드 시 중복/오염 데이터 생성
`app/routers/router_addon_agent.py` 의 `_VALID_TYPES` 화이트리스트에 우리 관제 Addon 9종이 쓰는
`agent_type="monitoring"` 이 없어 업로드 시 자동으로 `"app"` 으로 리셋됨 → "monitoring 타입은
tbl_agent_config 미등록" 가드가 우회되어, 누구든 addon.zip 을 재업로드(force=true)하면
`tbl_agent_config` 에 원문 키 이름(`agent_name=zip_stem`, `nav_group` 없음)의 중복 행이 생겨
목록에 "기타" 그룹으로 재등장. 실제로 재현 테스트 중 이 버그를 실증.

## 수정
1. `keyword_matcher._format_agent_list` — `tbl_addon_agents WHERE is_builtin=0` 를 추가 조회해
   "ADDON 에이전트" 그룹으로 병합. `format_response` 를 async 로 전환.
2. `orchestrator.py` 의 `format_response` 호출 2곳(run/stream)을 `await` 로 갱신.
3. `router_addon_agent._VALID_TYPES` 에 `"monitoring"` 추가 — 재업로드 시 agent_type 유지,
   tbl_agent_config 미오염 가드 정상 작동.
4. 재현 테스트로 오염된 `anomaly-detector`/`bmc-monitor` 의 `tbl_agent_config` 잔재 행 삭제 +
   `tbl_addon_agents.agent_name` 원문키 복구.

## 테스트 케이스

| ID | 내용 | 기대 결과 |
|----|------|----------|
| TC-31-01 | 회귀 (P0~P2 전체) | 14~30차 전부 PASS, ruff clean |
| TC-31-02 | (라이브) 채팅 에이전트 목록 | 기본 2 + 관제 2 + **ADDON 9** 전부 정상 표시명으로 응답 |
| TC-31-03 | (라이브) monitoring 재업로드 재현 | agent_type="monitoring" 유지, tbl_agent_config 미오염 |
