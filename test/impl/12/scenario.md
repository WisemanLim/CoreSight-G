# Phase 13 — UI 통합: 새 Agent 만들기 + Addon 에이전트 등록 (Iteration 12)

## 목적

AgentsPage의 두 버튼("새 Agent 만들기" wizard + ZIP 아이콘 "Addon 에이전트 등록")을
단일 "새 Agent 만들기" 버튼으로 통합. AgentBuilderModal에 탭 구조 추가.

## 테스트 케이스

| TC | 시나리오 | 예상 결과 |
|----|---------|---------|
| TC-12-01 | TypeScript 컴파일 오류 없음 | `tsc --noEmit` 0 errors |
| TC-12-02 | Vite 프로덕션 빌드 성공 | `✓ built` 출력 |
| TC-12-03 | AgentsPage에 showModal / AddonAgentModal 참조 없음 | grep 0건 |
| TC-12-04 | AgentBuilderModal에 mode 탭 ("build"/"upload") 있음 | source 확인 |
| TC-12-05 | visibleTemplates 필터: .omc 등 dot-prefix 제외 | source 확인 |
| TC-12-06 | AgentsPage에 onChanged prop 전달 확인 | source 확인 |
