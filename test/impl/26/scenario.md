# 시험 시나리오 — Iteration 26: P2-3 GPU 프로파일링 Addon (gpu-profiler)

## 범위
- mock exporter 고급 지표 6종: SM occupancy, Tensor pipe active, DRAM active, throttle reasons,
  PCIe TX/RX (ANOMALY 시 GPU3 throttle=1)
- 알람 규칙 1종 추가: GPUThrottling(warning, 2분 지속) — 총 12종
- `addon-agents/zip/gpu-profiler/` — Addon-first, ADDON 등록(is_builtin=0),
  intent `gpu_profiling`, `/status` 위젯

## 테스트 케이스

| ID | 내용 | 기대 결과 |
|----|------|----------|
| TC-26-01 | addon 모듈 규약 | router + tool↔executor 3종 일치 + SYSTEM_PROMPT |
| TC-26-02 | 프로파일 병합 (query 모킹) | GPU 단위 6지표 병합, 정렬 |
| TC-26-03 | throttle 필터 | throttle_reasons>0 인 GPU 만 반환 |
| TC-26-04 | Prometheus 다운 내성 | executor error dict |
| TC-26-05 | orchestrator 배선 | gpu_profiling → gpu-profiler |
| TC-26-06 | ZIP+시드 정합 | is_builtin=0, agent_config 미등록 |
| TC-26-07 | (라이브) E2E | loader 7/7, 4 GPU 프로파일, 위젯, 규칙 12종 |
