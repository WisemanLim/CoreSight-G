# 시험 시나리오 — Iteration 30: P2-7 워크로드 상관 Addon (workload-correlator) — P2 로드맵 완결

## 범위
- mock exporter: `DCGM_FI_DEV_GPU_PROCESS_MEM_USED{gpu,pid,job_id,user}` 고정 3프로세스
  (job-7a1: GPU0+1 분산학습/alice, job-9f3: GPU2/bob)
- `addon-agents/zip/workload-correlator/` — Addon-first, ADDON 등록(is_builtin=0),
  intent `workload_correlation`, `/status` 위젯

## 테스트 케이스

| ID | 내용 | 기대 결과 |
|----|------|----------|
| TC-30-01 | addon 모듈 규약 | router + tool↔executor 3종 일치 + SYSTEM_PROMPT |
| TC-30-02 | 프로세스 맵 조회 | 원본 리스트 정렬 |
| TC-30-03 | job 집계 | job_id 합산 메모리·GPU 목록·내림차순 |
| TC-30-04 | user 집계 | user 합산 메모리·GPU 목록·내림차순 |
| TC-30-05 | Prometheus 다운 내성 | 3개 도구 모두 error dict |
| TC-30-06 | orchestrator 배선 | workload_correlation → workload-correlator |
| TC-30-07 | ZIP+시드 정합 | is_builtin=0, agent_config 미등록 |
| TC-30-08 | (라이브) E2E | loader 11/11, job-7a1 이 GPU0+1 분산 학습으로 정확히 집계 |
