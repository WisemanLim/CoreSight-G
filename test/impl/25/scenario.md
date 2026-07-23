# 시험 시나리오 — Iteration 25: P2-2 BMC/IPMI Addon (bmc-monitor)

## 범위
- mock exporter BMC 지표 확장: `hw_fan_speed_rpm{fan1,fan2}`, `hw_voltage_volts{12V,5V,3.3V}`,
  `hw_bmc_power_watts` (ANOMALY 시 fan1 저속 + 12V 저전압)
- 알람 규칙 2종 추가: FanSpeedLow(critical, <1000RPM/2m), VoltageOutOfRange(critical, 12V 11.4~12.6 이탈/1m) — 총 11종
- `addon-agents/zip/bmc-monitor/` — Prometheus 센서 + Loki(job=bmc) 이벤트 결합 addon,
  ADDON 등록(is_builtin=0), intent `bmc`, `/status` 위젯

## 테스트 케이스

| ID | 내용 | 기대 결과 |
|----|------|----------|
| TC-25-01 | addon 모듈 규약 | router + tool↔executor 3종 일치 + SYSTEM_PROMPT |
| TC-25-02 | 센서 병합 (query 모킹) | 노드 단위 fans/voltages/psu/온도/전력 병합 |
| TC-25-03 | 이벤트 조회 (loki 모킹) | job=bmc LogQL + entries 반환 |
| TC-25-04 | 소스 다운 내성 | Prometheus/Loki 오류 → error dict / status 는 Loki 미가용 시 -1 |
| TC-25-05 | orchestrator 배선 | bmc → bmc-monitor |
| TC-25-06 | ZIP 3파일 + 시드 정합 | is_builtin=0, agent_config 미등록 |
| TC-25-07 | (라이브) E2E | loader 6/6, 센서 스냅샷, bmc 이벤트 50건, 위젯, 규칙 11종 |
