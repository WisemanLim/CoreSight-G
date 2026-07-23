# 시험 시나리오 — Iteration 29: P2-6 네트워크 모니터링 Addon (net-monitor)

## 범위
- mock exporter NIC 지표 확장: eth0/eth1 `hw_nic_{errors,drops}_total`, `hw_nic_link_up`,
  `hw_nic_{rx,tx}_bytes_per_sec` (ANOMALY 시 eth0 오류/드롭 누적 증가 + eth1 링크 다운)
- 알람 규칙 2종 추가: NICErrorsIncreasing(warning), NICLinkDown(critical, 1m) — 총 14종
- `addon-agents/zip/net-monitor/` — Addon-first, ADDON 등록(is_builtin=0),
  intent `network`, `/status` 위젯

## 테스트 케이스

| ID | 내용 | 기대 결과 |
|----|------|----------|
| TC-29-01 | addon 모듈 규약 | router + tool↔executor 3종 일치 + SYSTEM_PROMPT |
| TC-29-02 | 스냅샷 병합 (query 모킹) | 인터페이스 단위 5필드 병합, 정렬 |
| TC-29-03 | Prometheus 다운 내성 | executor error dict |
| TC-29-04 | orchestrator 배선 | network → net-monitor |
| TC-29-05 | ZIP+시드 정합 | is_builtin=0, agent_config 미등록 |
| TC-29-06 | (라이브) E2E | loader 10/10, eth0/eth1 스냅샷, 위젯, 규칙 14종 |
