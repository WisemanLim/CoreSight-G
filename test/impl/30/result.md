# 시험 결과 — Iteration 30: P2-7 워크로드 상관 Addon (workload-correlator) — **P2 로드맵 완결**

- 일시: 2026-07-23
- 판정: **PASS** (자동 8/8 + 회귀 92/92 + 라이브)

## 자동 시험

```
uv run pytest test/impl/30/ -q → 8 passed
회귀 (14~20·23~29차) → 92 passed / ruff clean
```

| ID | 결과 | 비고 |
|----|------|------|
| TC-30-01 모듈 규약 | PASS | tool↔executor 3종 일치 |
| TC-30-02 프로세스 맵 | PASS | GPU 오름차순 정렬 |
| TC-30-03 job 집계 | PASS | 분산 잡(2 GPU) 합산 정확, 내림차순 |
| TC-30-04 user 집계 | PASS | 사용자별 합산 정확 |
| TC-30-05 Prometheus 다운 내성 | PASS | 3개 도구 모두 error dict |
| TC-30-06 배선 | PASS | intent workload_correlation → workload-correlator |
| TC-30-07 ZIP+시드 | PASS | is_builtin=0, agent_config 미등록 |
| P2 로드맵 완결 확인 | PASS | P2-1~7 전체 9개 addon 이 ADDON 에이전트로 등록됨을 시드 파일 기준 검증 |

## 라이브 E2E (TC-30-08)

- 로더 `restored 11/11` (workload-correlator 포함) — **관제 Agent 11종 완성**
- `get_gpu_process_map`: GPU0(pid 10231, job-7a1, alice, 17.8GB) / GPU1(pid 10232, job-7a1, alice,
  11.9GB) / GPU2(pid 20450, job-9f3, bob, 26.8GB)
- `get_usage_by_job`: **job-7a1 이 GPU0+1 분산 학습 잡으로 정확히 집계**(총 29.7GB, 2 프로세스),
  job-9f3(GPU2 단일, 26.8GB) — mock exporter 설계와 정확히 일치
- `/status` 위젯: `{"active_processes":3,"active_jobs":2}`

## 변경 요약

- mock exporter: `DCGM_FI_DEV_GPU_PROCESS_MEM_USED{gpu,pid,job_id,user}` 고정 3프로세스 추가
- addon: `addon-agents/zip/workload-correlator/` — job_id/user 단위 집계(구현체 내 — Addon-first),
  intent `workload_correlation`, ADDON 에이전트 등록

## PRD P2 로드맵 최종 상태

| P2 | Addon | 상태 |
|---|---|---|
| 1 | storage-monitor | ✅ (24차) |
| 2 | bmc-monitor | ✅ (25차) |
| 3 | gpu-profiler | ✅ (26차) |
| 4 | capacity-planner | ✅ (27차) |
| 5 | anomaly-detector | ✅ (28차) |
| 6 | net-monitor | ✅ (29차) |
| 7 | workload-correlator | ✅ (30차, 본 차수) |

**P0 + P1 + P2 전체 PRD 범위 구현 완료.** 관제 Agent 11종(내장 2 + ADDON 9) 전부 라이브 검증.
