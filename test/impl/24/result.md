# 시험 결과 — Iteration 24: P2-1 스토리지 진단 Addon (storage-monitor)

- 일시: 2026-07-23
- 판정: **PASS** (자동 6/6 + 회귀 45/45 + 라이브)

## 자동 시험

```
uv run pytest test/impl/24/ -q → 6 passed
회귀 (14~20·23차) → 45 passed / ruff clean
```

| ID | 결과 | 비고 |
|----|------|------|
| TC-24-01 모듈 규약 | PASS | tool↔executor 3종 일치 |
| TC-24-02 스냅샷 병합 | PASS | latency/iops_{op}/SMART 병합 + RAID degraded bool |
| TC-24-03 Prometheus 다운 내성 | PASS | error dict, 예외 미전파 |
| TC-24-04 배선 | PASS | intent storage → storage-monitor |
| TC-24-05 ZIP 3파일 | PASS | |
| TC-24-06 시드 정합 | PASS | is_builtin=0 (ADDON 관리), agent_config 미등록 |

## 라이브 E2E (TC-24-07)

- 로더 `restored 5/5` (storage-monitor 포함)
- `get_storage_snapshot`: nvme0n1(latency 2.15/0.67ms, IOPS 8838/2567, wear 5.2%) +
  sda(latency 5.1/9.59ms) + RAID megaraid0 정상
- `/status` 위젯: `{"device_count":2,"smart_unhealthy":0,"raid_degraded":0}` — 대시보드 자동 반영
- Prometheus 규칙 9종 로드 (신규 SMARTUnhealthy·DiskLatencyHigh 포함)
- 이상 재현: `MOCK_ANOMALY=1` 시 sda SMART=0 + 읽기 지연 80~200ms → SMARTUnhealthy 즉시,
  DiskLatencyHigh 5분 지속 시 발화

## 변경 요약

- mock exporter: 스토리지 지표 12종 추가 (운영 전환 시 메트릭 이름 규약은 worker-guide 기재)
- 알람 규칙: SMARTUnhealthy(critical)·DiskLatencyHigh(warning) 추가 — 총 9종
- addon: `addon-agents/zip/storage-monitor/` (스냅샷 조회 로직 구현체 내 — Addon-first),
  intent `storage`, ADDON 에이전트 등록(is_builtin=0, 토글·위젯·intent 게이팅 자동 적용)
