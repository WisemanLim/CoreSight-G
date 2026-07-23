# storage-monitor — 스토리지 진단 Addon Agent 가이드 (PRD P2-1)

## 역할
Prometheus 에서 디스크 latency/IOPS/SMART/NVMe wear/RAID 상태를 조회·진단하는 read-only 관제 Agent.
근거: `.docs/gpu_server_monitoring_scale_guide.md` 체크리스트(Disk latency/IOPS 필수, RAID degraded 즉시 알람).

## 파일 규약
| 파일 | 용도 |
|------|------|
| `storage-monitor-app.py` | FastAPI router (`/api/addon/storage-monitor/*`) + `_TOOLS` + `TOOL_EXECUTORS` export |
| `storage-monitor-meta.json` | agent_type/capabilities (Agent Registry 등록용) |
| `storage-monitor.zip` | 업로드용 패키지 |

## 도구
| tool | 설명 |
|------|------|
| `get_storage_snapshot` | 디바이스 별 latency/IOPS/SMART/wear + RAID 상태 |
| `get_active_alerts` | 활성 알람 (SMARTUnhealthy·DiskLatencyHigh·RAIDDegraded 포함) |
| `query_promql` | PromQL 직접 조회 |

## 메트릭 규약 (운영 전환 시 exporter 가 제공해야 할 이름)
`hw_disk_read_latency_ms{device}` · `hw_disk_write_latency_ms{device}` · `hw_disk_iops{device,op}` ·
`hw_smart_healthy{device}` (1=정상) · `hw_nvme_wear_level_percent{device}` · `hw_raid_degraded{controller}`
(로컬은 mock exporter 가 시뮬레이션 — `MOCK_ANOMALY=1` 시 sda SMART 이상 + 지연 급증)

## 대시보드 위젯 (`GET /status`)
`{device_count, smart_unhealthy, raid_degraded}` — 활성화 시 자동 표시.

## 수동 점검
```bash
curl http://localhost:8100/api/addon/storage-monitor/status -H "Authorization: Bearer $TOKEN"
curl -X POST http://localhost:8100/api/addon/storage-monitor/tools/get_storage_snapshot \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{}'
```
