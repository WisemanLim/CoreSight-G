# 시험 시나리오 — Iteration 28: P2-5 이상 탐지 Addon (anomaly-detector)

## 범위
- `addon-agents/zip/anomaly-detector/` — z-score(population stdev) 기반 통계 이상 탐지 +
  활성 알람 노드/GPU 단위 상관분석. Addon-first, ADDON 등록(is_builtin=0),
  intent `anomaly_detection`, `/status` 위젯

## 테스트 케이스

| ID | 내용 | 기대 결과 |
|----|------|----------|
| TC-28-01 | addon 모듈 규약 | router + tool↔executor 2종 일치 + SYSTEM_PROMPT |
| TC-28-02 | z-score 계산 | 정상분포 표본에서 이상치 정확 탐지, threshold 미달은 제외 |
| TC-28-03 | 표본 부족 스킵 | 5개 미만 시계열은 건너뜀 |
| TC-28-04 | 알람 상관 그룹핑 | 동일 Hostname 2건 이상만 correlated 목록 포함 |
| TC-28-05 | Prometheus 다운 내성 | 두 도구 모두 error dict |
| TC-28-06 | orchestrator 배선 | anomaly_detection → anomaly-detector |
| TC-28-07 | ZIP+시드 정합 | is_builtin=0, agent_config 미등록 |
| TC-28-08 | (라이브) E2E | loader 9/9, 정상모드 count=0, GPU3 단독 필터 시 z-score>3.5 탐지, MOCK_ANOMALY 시 알람 9건 1노드 상관 |

## 실행
```bash
uv run pytest test/impl/28/ -v
```
