# 시험 시나리오 — Iteration 15: 통합 관제 대시보드 (PRD P0) + 에이전트 관리 그룹 분리

## 범위
- 백엔드: `query_range`/`gpu_util_history` 서비스 + `GET /api/metrics/gpu/history`
- 프론트: `/dashboard` 페이지 (활성 알람 배너 + GPU 카드 + 스파크라인 + HW 노드 테이블, 15s 폴링),
  기본 라우트 `/` → `/dashboard`, 사이드바 "대시보드" 메뉴, i18n(ko/en)
- 에이전트 관리: 내장 에이전트를 nav_group(기본 Agent/관제 Agent) 별 섹션으로 분리

## 테스트 케이스

| ID | 내용 | 방법 | 기대 결과 |
|----|------|------|----------|
| TC-15-01 | gpu_util_history 시계열 변환 | query_range 모킹 | hostname/gpu/points 구조, 정렬 |
| TC-15-02 | /api/metrics/gpu/history 미인증 | 토큰 없이 | 401/403 |
| TC-15-03 | /api/metrics/gpu/history 정상 | 서비스 모킹 + 인증 오버라이드 | 200 + series |
| TC-15-04 | history 파라미터 검증 | minutes=0 | 422 |
| TC-15-05 | (수동) 프론트 빌드 | `pnpm build` (tsc --noEmit 포함) | 오류 없음 |
| TC-15-06 | (수동, 라이브) history 응답 | curl | GPU 4장 utilization 시계열 |
| TC-15-07 | (수동, UI) 대시보드 렌더 | 브라우저 /dashboard | 알람/GPU 카드/HW 테이블 표시 |
| TC-15-08 | (수동, UI) 에이전트 관리 그룹 | 브라우저 /agents | "기본 Agent"/"관제 Agent" 섹션 분리 |

## 실행
```bash
uv run pytest test/impl/15/ -v
cd front && pnpm build
```
