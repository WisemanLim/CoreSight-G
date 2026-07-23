# 시험 시나리오 — Iteration 27: P2-4 용량 계획·효율 Addon (capacity-planner)

## 범위
- `addon-agents/zip/capacity-planner/` — Addon-first, `avg_over_time` 기반 기간 평균 조회,
  ADDON 등록(is_builtin=0), intent `capacity_planning`, `/status` 위젯
- 별도 mock exporter 변경 없음 (기존 GPU 지표를 range 로 재사용)

## 테스트 케이스

| ID | 내용 | 기대 결과 |
|----|------|----------|
| TC-27-01 | addon 모듈 규약 | router + tool↔executor 3종 일치 + SYSTEM_PROMPT |
| TC-27-02 | 저활용 필터 | avg util ≤ threshold 만 반환 |
| TC-27-03 | 효율 리포트 병합 | util+vram_percent 병합, fleet 평균 계산 |
| TC-27-04 | 카디널리티 요약 | 메트릭별 시계열 수 내림차순 |
| TC-27-05 | Prometheus 다운 내성 | 각 도구 error dict |
| TC-27-06 | orchestrator 배선 | capacity_planning → capacity-planner |
| TC-27-07 | ZIP+시드 정합 | is_builtin=0, agent_config 미등록 |
| TC-27-08 | (라이브) E2E | loader 8/8, GPU3 저활용(9.91%) 탐지, cardinality 77개 시계열/28 메트릭 |
