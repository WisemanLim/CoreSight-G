# Phase 11 F24 Agent Builder UI 시험 시나리오 (Iteration 10)

## 목적

F24 Agent Builder UI 구현 검증:
- Frontend: AgentBuilderModal.tsx 4단계 Wizard UI 존재
- API: POST /api/addon-agents/scaffold 동작 (9종 유형별 ZIP 생성)
- addonAgents.ts: scaffoldAgent / getCatalog 함수 존재
- AgentsPage.tsx: "새 Agent 만들기" 버튼 연동

## 테스트 케이스

| TC | 시나리오 | 예상 결과 |
|----|---------|---------|
| TC-10-01 | scaffold — app 유형 ZIP 생성 | 200, ZIP 반환 |
| TC-10-02 | scaffold — service 유형 ZIP 생성 | 200, ZIP 반환 |
| TC-10-03 | scaffold — rag 유형 ZIP 생성 | 200, ZIP 반환 |
| TC-10-04 | scaffold — tool-proxy 유형 ZIP 생성 | 200, ZIP 반환 |
| TC-10-05 | scaffold — reviewer 유형 (템플릿 없음) → 기본 구조 ZIP | 200, ZIP 반환 |
| TC-10-06 | scaffold — 이름 유효성 검사 실패 (숫자 시작) | 400 |
| TC-10-07 | scaffold — 이름 유효성 검사 실패 (공백 포함) | 400 |
| TC-10-08 | scaffold — 무효 agent_type | 400 |
| TC-10-09 | scaffold ZIP — meta.json 포함 여부 확인 | ZIP 내 {Name}-meta.json 존재 |
| TC-10-10 | scaffold ZIP — meta.json 내 agent_type 일치 | meta.json.agent_type == 요청값 |
| TC-10-11 | scaffold ZIP — description/domain 반영 | meta.json.description 포함 |
| TC-10-12 | TS 빌드 오류 없음 | tsc --noEmit 통과 |
