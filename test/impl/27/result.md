# 시험 결과 — Iteration 27: P2-4 용량 계획·효율 Addon (capacity-planner)

- 일시: 2026-07-23
- 판정: **PASS** (자동 7/7 + 회귀 63/63 + 라이브)

## 자동 시험

```
uv run pytest test/impl/27/ -q → 7 passed
회귀 (14~20·23~26차) → 63 passed / ruff clean
```

| ID | 결과 | 비고 |
|----|------|------|
| TC-27-01 모듈 규약 | PASS | tool↔executor 3종 일치 |
| TC-27-02 저활용 필터 | PASS | `avg_over_time(...[24h])` 임계값 필터 |
| TC-27-03 효율 리포트 병합 | PASS | util+vram_percent 병합, fleet 평균 |
| TC-27-04 카디널리티 요약 | PASS | 메트릭별 시계열 수 내림차순, 합계 정확 |
| TC-27-05 Prometheus 다운 내성 | PASS | 3개 도구 모두 error dict |
| TC-27-06 배선 | PASS | intent capacity_planning → capacity-planner |
| TC-27-07 ZIP+시드 | PASS | is_builtin=0, agent_config 미등록 |

## 라이브 E2E (TC-27-08)

- 로더 `restored 8/8` (capacity-planner 포함)
- `get_efficiency_report`(1h): fleet_avg_util=59.24%, GPU0 util 76.23%/VRAM 66.9% 등 4 GPU
- `get_underutilized_gpus`(1h, threshold 10%): **GPU3(9.91%) 정확히 탐지** — mock exporter 의
  GPU3 저활용 설계(5~15%)와 일치, 로직 검증
- `get_cardinality_summary`: 전체 77 활성 시계열 / 28 메트릭 이름
- `/status` 위젯: `{"underutilized_gpus_24h":0}` (24h 윈도우는 별도 검증 — 1h 예시와 기간 다름)

## 변경 요약

- addon: `addon-agents/zip/capacity-planner/` — 신규 mock 지표 없이 기존 GPU 메트릭을
  `avg_over_time` range 로 재사용해 추세·비용 거버넌스 제공. intent `capacity_planning`,
  ADDON 에이전트 등록. PRD §5 성공지표(TCO·카디널리티 준수율) 판단 근거로 연계.
