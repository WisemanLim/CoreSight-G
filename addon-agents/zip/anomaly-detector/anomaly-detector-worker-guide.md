# anomaly-detector — 이상 탐지·원인 분석 보조 Addon Agent 가이드 (PRD P2-5)

## 역할
z-score 기반 메트릭 이상 탐지 + 활성 알람 상관분석(동일 노드/GPU 다중 알람 그룹핑).
별도 ML 인프라 없이 통계 기법만 사용 — 근거: 시장 보고서 "AI/ML 이상 탐지·예측 = 핵심 차별점",
"알람 노이즈 감소".

## 파일 규약
| 파일 | 용도 |
|------|------|
| `anomaly-detector-app.py` | FastAPI router (`/api/addon/anomaly-detector/*`) + `_TOOLS` + `TOOL_EXECUTORS` export |
| `anomaly-detector-meta.json` | agent_type/capabilities |
| `anomaly-detector.zip` | 업로드용 패키지 |

## 도구
| tool | 설명 |
|------|------|
| `detect_metric_anomalies` | 지정 PromQL 시계열의 z-score 기반 이상치 (population stdev, 임계값 조정 가능) |
| `correlate_alerts` | 활성 알람을 Hostname/GPU 단위로 그룹핑 → 2건 이상 동시 발생 = 상관 후보 |

## 한계 (명시)
- 통계적 신호일 뿐 확정 진단 아님 — SYSTEM_PROMPT 에 명시.
- 표본 5개 미만인 시계열은 스킵(신뢰도 낮음).
- 다른 addon(gpu-monitor 등)의 메트릭을 그대로 조회 — 자체 지표는 생성하지 않음.

## 대시보드 위젯 (`GET /status`)
`{correlated_targets}` — 2건 이상 알람이 겹치는 노드/GPU 수.

## 수동 점검
```bash
curl http://localhost:8100/api/addon/anomaly-detector/status -H "Authorization: Bearer $TOKEN"
curl -X POST http://localhost:8100/api/addon/anomaly-detector/tools/detect_metric_anomalies \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"promql":"DCGM_FI_DEV_GPU_TEMP","hours":6}'
```
