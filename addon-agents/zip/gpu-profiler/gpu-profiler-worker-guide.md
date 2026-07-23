# gpu-profiler — GPU 고급 프로파일링 Addon Agent 가이드 (PRD P2-3)

## 역할
DCGM profiling metrics(2·3순위 고급 지표) 조회 — SM occupancy, Tensor pipe active, DRAM bandwidth,
throttle reasons, PCIe TX/RX. gpu-monitor(1순위 기본 운영 지표)와 분리해 카디널리티·비용을 통제한다.
근거: `.docs/enterprise_monitoring_roi_gpu_report.md`(수집 우선순위 2·3순위),
`.docs/monitoring_market_observability_report_2026_2034.md`(고급 지표, DCGM profiling 저오버헤드).

## 파일 규약
| 파일 | 용도 |
|------|------|
| `gpu-profiler-app.py` | FastAPI router (`/api/addon/gpu-profiler/*`) + `_TOOLS` + `TOOL_EXECUTORS` export |
| `gpu-profiler-meta.json` | agent_type/capabilities (Agent Registry 등록용) |
| `gpu-profiler.zip` | 업로드용 패키지 |

## 도구
| tool | 설명 |
|------|------|
| `get_gpu_profile` | GPU 별 SM occupancy·Tensor pipe·DRAM active·throttle·PCIe TX/RX |
| `get_throttled_gpus` | 현재 throttle 걸린 GPU 목록 (전력/온도 제한 탐지) |
| `query_promql` | PromQL 직접 조회 |

## 메트릭 규약 (운영 전환 시 DCGM Exporter 가 제공하는 profiling 필드명)
`DCGM_FI_PROF_SM_OCCUPANCY` · `DCGM_FI_PROF_PIPE_TENSOR_ACTIVE` · `DCGM_FI_PROF_DRAM_ACTIVE` ·
`DCGM_FI_DEV_CLOCK_THROTTLE_REASONS` · `DCGM_FI_PROF_PCIE_TX_BYTES` / `_RX_BYTES`
(로컬은 mock exporter 시뮬레이션 — `MOCK_ANOMALY=1` 시 GPU3 throttle=1)

## 알람
`GPUThrottling`(warning, throttle_reasons>0 지속 2분) — `deploy/prometheus/rules/coresight_alerts.yml`.

## 대시보드 위젯 (`GET /status`)
`{gpu_count, throttled}` — 활성화 시 자동 표시.

## 수동 점검
```bash
curl http://localhost:8100/api/addon/gpu-profiler/status -H "Authorization: Bearer $TOKEN"
curl -X POST http://localhost:8100/api/addon/gpu-profiler/tools/get_gpu_profile \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{}'
```
