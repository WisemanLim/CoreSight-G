# 시험 결과 — Iteration 25: P2-2 BMC/IPMI Addon (bmc-monitor)

- 일시: 2026-07-23
- 판정: **PASS** (자동 6/6 + 회귀 51/51 + 라이브)

## 자동 시험

```
uv run pytest test/impl/25/ -q → 6 passed
회귀 (14~20·23·24차) → 51 passed / ruff clean
```

| ID | 결과 | 비고 |
|----|------|------|
| TC-25-01 모듈 규약 | PASS | tool↔executor 3종 일치 |
| TC-25-02 센서 병합 | PASS | 노드 단위 fans/voltages/psu/온도/전력 |
| TC-25-03 이벤트 조회 | PASS | LogQL `{job="bmc", level="error"}` |
| TC-25-04 소스 다운 내성 | PASS | Prometheus/Loki 각각 error dict |
| TC-25-05 배선 | PASS | intent bmc → bmc-monitor |
| TC-25-06 ZIP+시드 | PASS | is_builtin=0, agent_config 미등록 |

## 라이브 E2E (TC-25-07)

- 로더 `restored 6/6` (bmc-monitor 포함)
- `get_bmc_sensors`: fan1 5010/fan2 4716 RPM, 12V/5V/3.3V 정상, PSU1/2 OK, 흡기 22.3°C, 전력 1517W
- `get_bmc_events`: Loki `job=bmc` 50건 조회 (IPMI fan speed 정상 로그)
- `/status` 위젯: `{"node_count":1,"sensor_abnormal":0,"error_events_1h":0}`
- Prometheus 규칙 11종 (신규 FanSpeedLow·VoltageOutOfRange 포함)
- 이상 재현: `MOCK_ANOMALY=1` 시 fan1 300~800RPM + 12V 10.8~11.2V → FanSpeedLow(2m)·VoltageOutOfRange(1m) 발화

## 변경 요약

- mock exporter: BMC 지표 6종 추가 (fan1/2, 3-rail 전압, 섀시 전력) — 운영 전환 시 ipmi_exporter 매핑 규약 worker-guide 기재
- 알람 규칙: FanSpeedLow(critical)·VoltageOutOfRange(critical) 추가 — 총 11종
- addon: `addon-agents/zip/bmc-monitor/` — **Prometheus(센서) + Loki(job=bmc 이벤트) 결합** 최초 사례
  (조회 로직 구현체 내 — Addon-first), intent `bmc`, ADDON 에이전트 등록
