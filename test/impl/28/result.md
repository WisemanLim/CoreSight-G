# 시험 결과 — Iteration 28: P2-5 이상 탐지 Addon (anomaly-detector)

- 일시: 2026-07-23
- 판정: **PASS** (자동 9/9 + 회귀 70/70 + 라이브)

## 자동 시험

```
uv run pytest test/impl/28/ -v → 9 passed
회귀 (14~20·23~27차) → 70 passed / ruff clean
```

수정 1건: `test_zscores_flags_outlier`/`test_detect_metric_anomalies_end_to_end` 초기 표본이
너무 작아 population stdev 가 이상치 자체에 끌려 올라가 z-score 가 임계값(3.0) 미달(2.23→2.99).
표본 수 확대(6→13, 이상치 배율 5→20배)로 재현성 있는 통계 신호 확보 후 PASS.

| ID | 결과 | 비고 |
|----|------|------|
| TC-28-01 모듈 규약 | PASS | tool↔executor 2종 일치 |
| TC-28-02 z-score 계산 | PASS | 이상치 z>3.0, 정상값 z<1.5, zero-stdev 처리 |
| TC-28-03 표본 부족 스킵 | PASS | 5개 미만 시계열 제외 |
| TC-28-04 알람 상관 그룹핑 | PASS | 2건 이상 동일 Hostname 만 포함 |
| TC-28-05 Prometheus 다운 내성 | PASS | 두 도구 모두 error dict |
| TC-28-06 배선 | PASS | intent anomaly_detection → anomaly-detector |
| TC-28-07 ZIP+시드 | PASS | is_builtin=0, agent_config 미등록 |

## 라이브 E2E (TC-28-08)

- 로더 `restored 9/9` (anomaly-detector 포함)
- **정상 모드**: `detect_metric_anomalies`(GPU_TEMP, 1h) → count=0 (이상 없음, 오탐 없음 확인)
- **이상 모드**(`MOCK_ANOMALY=1`, gpu-mock-exporter 재기동): GPU3 단독 필터 조회 시
  z-score 3.52~4.04 (온도 91~95°C) 정확 탐지
- **알람 상관**: 이상 모드 2분+ 경과 후 `correlate_alerts` → 활성 9건 전부 `gpu-node-01` 로 그룹핑
  (`correlated_targets:1`) — GPU·하드웨어·스토리지·BMC 알람이 동일 노드에 동시 발생함을 정확히 포착
- 시험 후 정상 모드로 복원 완료

## 변경 요약

- addon: `addon-agents/zip/anomaly-detector/` — population stdev 기반 z-score(외부 ML 라이브러리 없음,
  표준 라이브러리 `statistics` 만 사용) + 활성 알람 Hostname/GPU 그룹핑. intent `anomaly_detection`,
  ADDON 에이전트 등록. "통계적 신호일 뿐 확정 진단 아님" 명시 — 과신 방지.
