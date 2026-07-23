# 시험 결과 — Iteration 26: P2-3 GPU 프로파일링 Addon (gpu-profiler)

- 일시: 2026-07-23
- 판정: **PASS** (자동 6/6 + 회귀 57/57 + 라이브)

## 자동 시험

```
uv run pytest test/impl/26/ -q → 6 passed
회귀 (14~20·23~25차) → 57 passed / ruff clean
```

| ID | 결과 | 비고 |
|----|------|------|
| TC-26-01 모듈 규약 | PASS | tool↔executor 3종 일치 |
| TC-26-02 프로파일 병합 | PASS | GPU 단위 6지표 병합, gpu 오름차순 정렬 |
| TC-26-03 throttle 필터 | PASS | throttle_reasons>0 만 반환 |
| TC-26-04 Prometheus 다운 내성 | PASS | error dict |
| TC-26-05 배선 | PASS | intent gpu_profiling → gpu-profiler |
| TC-26-06 ZIP+시드 | PASS | is_builtin=0, agent_config 미등록 |

## 라이브 E2E (TC-26-07)

- 로더 `restored 7/7` (gpu-profiler 포함)
- `get_gpu_profile`: GPU0 sm_occupancy=0.768, tensor_pipe_active=0.321, dram_active=0.241,
  throttle=0, PCIe TX/RX 확인 (4 GPU 전체)
- `/status` 위젯: `{"gpu_count":4,"throttled":0}`
- Prometheus 규칙 12종 (신규 GPUThrottling 포함)
- 이상 재현: `MOCK_ANOMALY=1` 시 GPU3 throttle_reasons=1 → GPUThrottling 2분 지속 시 발화

## 변경 요약

- mock exporter: GPU 고급 지표 6종 추가 (SM occupancy, Tensor pipe, DRAM active, throttle, PCIe TX/RX)
  — 운영 전환 시 DCGM profiling 필드명 규약 worker-guide 기재
- 알람 규칙: GPUThrottling(warning) 추가 — 총 12종
- addon: `addon-agents/zip/gpu-profiler/` — 1순위(gpu-monitor)와 분리된 2·3순위 지표 전용 Agent
  (카디널리티·비용 통제 원칙 반영), intent `gpu_profiling`, ADDON 에이전트 등록
