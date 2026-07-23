# Phase 11 F24 Agent Builder UI 시험 결과 (Iteration 10)

## 판정: PASS ✅

## 결과 요약

| TC | 시나리오 | 결과 |
|----|---------|------|
| TC-10-01 | scaffold — app 유형 ZIP 생성 | ✅ PASS |
| TC-10-02 | scaffold — service 유형 ZIP 생성 | ✅ PASS |
| TC-10-03 | scaffold — rag 유형 ZIP 생성 | ✅ PASS |
| TC-10-04 | scaffold — tool-proxy 유형 ZIP 생성 | ✅ PASS |
| TC-10-05 | scaffold — reviewer 유형 (템플릿 없음) → 기본 구조 ZIP | ✅ PASS |
| TC-10-06 | scaffold — 이름 유효성 검사 실패 (숫자 시작) | ✅ PASS |
| TC-10-07 | scaffold — 이름 유효성 검사 실패 (공백 포함) | ✅ PASS |
| TC-10-08 | scaffold — 무효 agent_type | ✅ PASS |
| TC-10-09 | scaffold ZIP — meta.json 포함 여부 확인 | ✅ PASS |
| TC-10-10 | scaffold ZIP — meta.json 내 agent_type 일치 | ✅ PASS |
| TC-10-11 | scaffold ZIP — description/domain 반영 | ✅ PASS |
| TC-10-12 | TS 빌드 오류 없음 | ✅ PASS |

**총 12개 / 12 PASS, 0 FAIL**  
실행 시간: 5.08s

## 버그 수정

- **scaffold domain 치환 로직 수정** (`router_addon_agent.py` L211):
  - 기존: `f"{body.domain}.{cap['domain'].split('.')[-1]}"` (suffix 붙임)
  - 수정: `body.domain` 직접 교체 — 요청한 domain을 그대로 사용

## 구현 확인

- `front/src/api/addonAgents.ts` — `scaffoldAgent()`, `getCatalog()` 함수 추가
- `front/src/pages/agents/AgentBuilderModal.tsx` — 4단계 Wizard 모달 신규 생성
  - Step 1: 9종 유형 카드 선택 (템플릿 유무 배지 표시)
  - Step 2: 이름(PascalCase 검증)/설명/도메인 입력
  - Step 3: ZIP 파일 구조 + meta.json 미리보기
  - Step 4: ZIP 다운로드 / 바로 배포 선택
- `front/src/pages/agents/AgentsPage.tsx` — "새 Agent 만들기" 버튼 → AgentBuilderModal 연동
