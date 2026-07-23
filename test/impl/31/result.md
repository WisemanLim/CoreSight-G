# 시험 결과 — Iteration 31: 채팅 "에이전트 목록" 응답 Addon 누락 수정

- 일시: 2026-07-23
- 판정: **PASS**

| ID | 결과 | 비고 |
|----|------|------|
| TC-31-01 | PASS | 92 passed, ruff clean |
| TC-31-02 | PASS | 기본 2 + 관제 2 + ADDON 9(BMC/IPMI·GPU 프로파일링·네트워크·로그·스토리지·용량계획·워크로드상관·이상탐지·트레이스) 전부 정상 표시명 |
| TC-31-03 | PASS | 재업로드 후 `agent_type:"monitoring"` 유지, `tbl_agent_config` 신규 행 생성 없음 확인 |

## 수정 파일

- `app/rules/keyword_matcher.py` — `format_response`/`_format_agent_list` async 전환, addon 병합
- `app/agents/orchestrator.py` — `format_response` 호출 4곳 `await` 추가
- `app/routers/router_addon_agent.py` — `_VALID_TYPES` 에 `"monitoring"` 추가,
  agent_config 등록 조건을 `agent_type != "monitoring"` 로 가드

## 부수 정리

- 재현 테스트 중 오염됐던 `anomaly-detector`/`bmc-monitor` 의 `tbl_agent_config` 중복 행 삭제,
  `tbl_addon_agents.agent_name` 표시명(원문키→"이상 탐지 Agent"/"BMC/IPMI Agent") 복구
- seed 파일에 두 addon 의 `agent_name` 복구 UPDATE 문 추가(재발 방지, 최소 범위)

## 근본 원인 요약

두 개의 독립적 버그가 결합:
1. Addon-first 아키텍처 결정(23차) 후 채팅 목록 포맷터가 갱신되지 않음(설계 누락).
2. `_VALID_TYPES` 화이트리스트 누락으로 monitoring addon 재업로드 시 P1+ 는 agent_config
   미등록이라는 설계 원칙 자체가 조용히 우회됨(가드 무력화 버그).
2번은 사용자가 직접 보고하지 않았으나 1번을 조사하는 과정에서 실제 업로드 재현으로 발견·확정.
