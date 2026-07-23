# 시험 결과 — Iteration 15: 통합 관제 대시보드 + 에이전트 관리 그룹 분리

- 일시: 2026-07-22
- 판정: **PASS** (자동 4/4 + 빌드 + 라이브 3/3)

## 자동 시험 (pytest)

```
uv run pytest test/impl/15/ -v
4 passed in 0.47s
```

| ID | 결과 | 비고 |
|----|------|------|
| TC-15-01 gpu_util_history 변환 | PASS | 정렬·points 구조 확인 |
| TC-15-02 history 미인증 | PASS | 401/403 |
| TC-15-03 history 200 | PASS | 서비스 모킹 |
| TC-15-04 minutes=0 → 422 | PASS | Query 검증 |

## 빌드·라이브 검증

- TC-15-05 `pnpm build` (tsc --noEmit 포함): 오류 없음 (1.13s)
- TC-15-06 `GET /api/metrics/gpu/history?minutes=10&step=30`: series 4 (GPU 4장), gpu0 points 21
- TC-15-07 `http://localhost:4100/dashboard`: 200 — 알람 배너("활성 알람 없음")·GPU 카드 4장(Util/VRAM 바,
  스파크라인, 온도/전력)·HW 노드 테이블(gpu-node-01 RAID OK/PSU OK) 렌더
- TC-15-08 `/agents`: "기본 Agent" / "관제 Agent" 섹션 분리 렌더 (nav_group 기준, 등장 순서 유지)

## 변경 요약

- 백엔드: `query_range` + `gpu_util_history` 서비스, `GET /api/metrics/gpu/history`
- 프론트: `pages/dashboard/DashboardPage.tsx`(15s 폴링, 순수 SVG 스파크라인 — 신규 의존성 없음),
  `api/metrics.ts`, 라우트 `/dashboard`(기본 진입), 사이드바 메뉴 + IcDashboard, i18n ko/en
- 에이전트 관리: 내장 에이전트 nav_group 별 섹션 분리 (`AgentsPage.tsx`)

## 접수된 신규 요구 (다음 차수, PRD 기록)

- Orchestrator·AI Assistant 외 관제 Agent(GPU 모니터링/하드웨어)를 `addon-agents/zip/` ZIP 구현체로
  분리 관리 (참조: SeCuardian `addon-agents/zip/<agent>/` — `<agent>-app.py` + `<agent>-meta.json`
  + 가이드 md + 패키징 `<agent>.zip`). 본 차수 범위 확대 금지 원칙에 따라 Iteration 16 대상.
