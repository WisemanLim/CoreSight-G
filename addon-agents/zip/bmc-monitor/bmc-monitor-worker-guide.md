# bmc-monitor — BMC/IPMI 관제 Addon Agent 가이드 (PRD P2-2)

## 역할
BMC/iDRAC/iLO 센서(Prometheus)와 이벤트 로그(Loki, `job=bmc`)를 결합 조회하는 read-only 관제 Agent.
근거: `.docs/gpu_server_monitoring_scale_guide.md` "BMC/iDRAC/iLO event 권장, critical 이벤트 선제 대응".

## 파일 규약
| 파일 | 용도 |
|------|------|
| `bmc-monitor-app.py` | FastAPI router (`/api/addon/bmc-monitor/*`) + `_TOOLS` + `TOOL_EXECUTORS` export |
| `bmc-monitor-meta.json` | agent_type/capabilities (Agent Registry 등록용) |
| `bmc-monitor.zip` | 업로드용 패키지 |

## 도구
| tool | 소스 | 설명 |
|------|------|------|
| `get_bmc_sensors` | Prometheus | 노드 별 팬 RPM·전압 레일·PSU·흡기 온도·섀시 전력 |
| `get_bmc_events` | Loki | BMC 이벤트 로그 (keyword/level/minutes) |
| `get_active_alerts` | Prometheus | 활성 알람 (FanSpeedLow·VoltageOutOfRange·PSUFailure 포함) |

## 메트릭·로그 규약 (운영 전환 시 exporter/수집기 제공 항목)
- 메트릭: `hw_fan_speed_rpm{fan}` · `hw_voltage_volts{rail}` · `hw_psu_status{psu}` (1=정상) ·
  `hw_inlet_temp_celsius` · `hw_bmc_power_watts` — ipmi_exporter 매핑 권장
- 로그: Loki 라벨 `job=bmc`, `level=info|warning|error`, `Hostname=<node>`
- 로컬은 mock exporter/log generator 시뮬레이션 (`MOCK_ANOMALY=1` 시 fan1 저속 + 12V 저전압 + RAID 이벤트)

## 대시보드 위젯 (`GET /status`)
`{node_count, sensor_abnormal, error_events_1h}` — Loki 미가용 시 error_events_1h=-1 (센서만 유효).

## 수동 점검
```bash
curl http://localhost:8100/api/addon/bmc-monitor/status -H "Authorization: Bearer $TOKEN"
curl -X POST http://localhost:8100/api/addon/bmc-monitor/tools/get_bmc_sensors \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{}'
curl -X POST http://localhost:8100/api/addon/bmc-monitor/tools/get_bmc_events \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"level":"error","minutes":120}'
```
