# workload-correlator — 워크로드-GPU 상관분석 Addon Agent 가이드 (PRD P2-7)

## 역할
프로세스별 GPU 메모리 점유를 job_id/user 메타데이터와 연계 집계 — "누가/어떤 잡이 어느 GPU 를
얼마나 쓰는지" 답한다. P2 로드맵의 마지막 항목.
근거: `.docs/gpu_server_monitoring_scale_guide.md` "GPU 노드/잡/파드 상관분석",
GPU 모니터링 목적 "프로세스별 원인 분석".

## 파일 규약
| 파일 | 용도 |
|------|------|
| `workload-correlator-app.py` | FastAPI router (`/api/addon/workload-correlator/*`) + `_TOOLS` + `TOOL_EXECUTORS` export |
| `workload-correlator-meta.json` | agent_type/capabilities |
| `workload-correlator.zip` | 업로드용 패키지 |

## 도구
| tool | 설명 |
|------|------|
| `get_gpu_process_map` | GPU 별 활성 프로세스(pid/job_id/user/메모리 점유) 원본 목록 |
| `get_usage_by_job` | job_id 단위 집계(총 메모리·사용 GPU 목록), 내림차순 |
| `get_usage_by_user` | user 단위 집계, 내림차순 |

## 메트릭 규약 (운영 전환 시 DCGM Exporter 가 제공하는 process accounting 필드)
`DCGM_FI_DEV_GPU_PROCESS_MEM_USED{gpu,pid,job_id,user,Hostname}` —
K8s 환경은 `job_id`→파드/잡 이름, Slurm 은 `job_id`→SLURM_JOB_ID 매핑 권장.
로컬 mock exporter 는 고정 3프로세스(job-7a1: GPU0+1 분산 학습, job-9f3: GPU2 단일)로 시뮬레이션.

## 대시보드 위젯 (`GET /status`)
`{active_processes, active_jobs}` — 활성화 시 자동 표시.

## 수동 점검
```bash
curl http://localhost:8100/api/addon/workload-correlator/status -H "Authorization: Bearer $TOKEN"
curl -X POST http://localhost:8100/api/addon/workload-correlator/tools/get_usage_by_job \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{}'
```
