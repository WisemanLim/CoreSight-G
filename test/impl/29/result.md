# 시험 결과 — Iteration 29: P2-6 네트워크 모니터링 Addon (net-monitor)

- 일시: 2026-07-23
- 판정: **PASS** (자동 5/5 + 회귀 84/84 + 라이브)

## 자동 시험

```
uv run pytest test/impl/29/ -q → 5 passed
회귀 (14~20·23~28차) → 84 passed / ruff clean
```

| ID | 결과 | 비고 |
|----|------|------|
| TC-29-01 모듈 규약 | PASS | tool↔executor 3종 일치 |
| TC-29-02 스냅샷 병합 | PASS | eth0/eth1 정렬, 5필드 병합 |
| TC-29-03 Prometheus 다운 내성 | PASS | error dict |
| TC-29-04 배선 | PASS | intent network → net-monitor |
| TC-29-05 ZIP+시드 | PASS | is_builtin=0, agent_config 미등록 |

## 라이브 E2E (TC-29-06)

- 로더 `restored 10/10` (net-monitor 포함) — 관제 Agent 10종 완성
- `get_nic_snapshot`: eth0(오류/드롭 0, link up, RX 466MB/s) + eth1(오류/드롭 0, link up, RX 38MB/s)
- `/status` 위젯: `{"interface_count":2,"link_down":0,"with_errors":0}`
- Prometheus 규칙 14종 (신규 NICErrorsIncreasing·NICLinkDown 포함)
- 이상 재현: `MOCK_ANOMALY=1` 시 eth0 오류/드롭 누적 증가 + eth1 link_up=0
  → NICErrorsIncreasing(즉시)·NICLinkDown(1분 지속) 발화

## 변경 요약

- mock exporter: NIC 지표 8종 추가 (eth0/eth1 오류·드롭·링크·RX/TX)
- 알람 규칙: NICErrorsIncreasing(warning)·NICLinkDown(critical) 추가 — 총 14종
- addon: `addon-agents/zip/net-monitor/` (조회 로직 구현체 내 — Addon-first), intent `network`,
  ADDON 에이전트 등록
