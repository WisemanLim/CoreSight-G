# 시험 시나리오 — Iteration 24: P2-1 스토리지 진단 Addon (storage-monitor)

## 범위
- mock exporter 스토리지 지표 확장: `hw_disk_{read,write}_latency_ms`, `hw_disk_iops{op}`,
  `hw_smart_healthy`, `hw_nvme_wear_level_percent` (ANOMALY 시 sda SMART 이상·지연 급증)
- 알람 규칙 2종 추가: SMARTUnhealthy(critical), DiskLatencyHigh(warning, 50ms/5m)
- `addon-agents/zip/storage-monitor/` — Addon-first (스냅샷 조회 로직 구현체 내),
  ADDON 에이전트 등록(is_builtin=0), intent `storage`, `/status` 위젯

## 테스트 케이스

| ID | 내용 | 기대 결과 |
|----|------|----------|
| TC-24-01 | addon 모듈 규약 | router + tool↔executor 일치 + SYSTEM_PROMPT |
| TC-24-02 | 스냅샷 병합 (query 모킹) | 디바이스 병합 + iops_{op} + raid degraded bool |
| TC-24-03 | Prometheus 다운 내성 | executor {"error": ...} |
| TC-24-04 | orchestrator 배선 | storage → storage-monitor |
| TC-24-05 | ZIP 3파일 | app/meta/guide |
| TC-24-06 | 시드 정합 | is_builtin=0, agent_config 미등록 |
| TC-24-07 | (라이브) E2E | loader 5/5, snapshot 2 devices, status 위젯, 규칙 9종 |
