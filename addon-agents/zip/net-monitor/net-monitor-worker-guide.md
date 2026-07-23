# net-monitor — 네트워크 인터페이스 관제 Addon Agent 가이드 (PRD P2-6)

## 역할
NIC 오류/드롭/링크상태/RX·TX 처리량 조회 — read-only 관제 Agent.
근거: `.docs/gpu_server_monitoring_scale_guide.md` "NIC error/drop 필수".

## 파일 규약
| 파일 | 용도 |
|------|------|
| `net-monitor-app.py` | FastAPI router (`/api/addon/net-monitor/*`) + `_TOOLS` + `TOOL_EXECUTORS` export |
| `net-monitor-meta.json` | agent_type/capabilities |
| `net-monitor.zip` | 업로드용 패키지 |

## 도구
| tool | 설명 |
|------|------|
| `get_nic_snapshot` | 인터페이스 별 오류/드롭/링크상태/RX·TX 처리량 |
| `get_active_alerts` | 활성 알람 (NICErrorsIncreasing·NICLinkDown 포함) |
| `query_promql` | PromQL 직접 조회 |

## 메트릭 규약 (운영 전환 시 node_exporter/커스텀 exporter 제공 항목)
`hw_nic_errors_total{nic}` · `hw_nic_drops_total{nic}` · `hw_nic_link_up{nic}`(1=up) ·
`hw_nic_rx_bytes_per_sec{nic}` / `hw_nic_tx_bytes_per_sec{nic}`
(로컬은 mock exporter 시뮬레이션 — `MOCK_ANOMALY=1` 시 eth0 오류/드롭 증가 + eth1 링크 다운)

## 알람
`NICErrorsIncreasing`(warning) · `NICLinkDown`(critical, 1분) —
`deploy/prometheus/rules/coresight_alerts.yml`.

## 대시보드 위젯 (`GET /status`)
`{interface_count, link_down, with_errors}` — 활성화 시 자동 표시.

## 수동 점검
```bash
curl http://localhost:8100/api/addon/net-monitor/status -H "Authorization: Bearer $TOKEN"
curl -X POST http://localhost:8100/api/addon/net-monitor/tools/get_nic_snapshot \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{}'
```
