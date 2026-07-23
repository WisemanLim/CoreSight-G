# capacity-planner — 용량 계획·효율 Addon Agent 가이드 (PRD P2-4)

## 역할
저활용 GPU 탐지, GPU 효율 리포트, 카디널리티(활성 시계열) 요약 — 비용 거버넌스.
근거: `.docs/enterprise_monitoring_roi_gpu_report.md` 보존 전략·비용 최적화,
`.docs/monitoring_market_observability_report_2026_2034.md` 로드맵 5단계 "capacity planning·cost governance".

## 파일 규약
| 파일 | 용도 |
|------|------|
| `capacity-planner-app.py` | FastAPI router (`/api/addon/capacity-planner/*`) + `_TOOLS` + `TOOL_EXECUTORS` export |
| `capacity-planner-meta.json` | agent_type/capabilities |
| `capacity-planner.zip` | 업로드용 패키지 |

## 도구
| tool | 설명 |
|------|------|
| `get_underutilized_gpus` | `avg_over_time` 기반 기간 평균 utilization ≤ 임계값(기본 10%, 24h) GPU |
| `get_efficiency_report` | GPU 전체/노드별 평균 utilization·VRAM 사용률 |
| `get_cardinality_summary` | `count({__name__=~"DCGM_FI_.+\|hw_.+"}) by (__name__)` — 메트릭별 활성 시계열 수 |

## PRD 성공지표 연계
`.docs/CoreSightG-PRD.md` §5 — TCO(라이선스 $0·운영시간 주 4h), 메트릭 저장량/카디널리티(95%+ 준수율)
판단에 이 Agent 의 `get_cardinality_summary` 를 근거로 사용.

## 대시보드 위젯 (`GET /status`)
`{underutilized_gpus_24h}` — 활성화 시 자동 표시.

## 수동 점검
```bash
curl http://localhost:8100/api/addon/capacity-planner/status -H "Authorization: Bearer $TOKEN"
curl -X POST http://localhost:8100/api/addon/capacity-planner/tools/get_efficiency_report \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"hours":24}'
```
