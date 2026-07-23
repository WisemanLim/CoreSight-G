# 시험 시나리오 — Iteration 14: GPU/HW 메트릭 수집 계층 + 관제 Domain Agent (PRD P0)

## 범위
- Prometheus 연동 서비스(`app/services/prometheus.py`)
- 메트릭 조회 API(`/api/metrics/gpu|hardware|alerts|query`)
- GPUMonitoringAgent / HardwareAgent (ExampleAgent 대체)
- Orchestrator intent 확장(gpu_monitoring/hardware)
- compose: prometheus + gpu-mock-exporter + 알람 규칙 7종

## 테스트 케이스

| ID | 내용 | 방법 | 기대 결과 |
|----|------|------|----------|
| TC-14-01 | gpu_snapshot 메트릭 병합 | prometheus.query 모킹 | GPU 별 dict 병합 + vram_used_percent 계산 |
| TC-14-02 | hardware_snapshot 노드 필터 | query 모킹 (Hostname 없는 샘플 포함) | Hostname 없는 샘플 제외, psu_failed 기본 0 |
| TC-14-03 | Prometheus 연결 실패 | httpx 오류 모킹 | PrometheusError 발생 |
| TC-14-04 | /api/metrics/* 미인증 | 토큰 없이 호출 | 401/403 |
| TC-14-05 | /api/metrics/gpu 정상 | 서비스 모킹 + 인증 오버라이드 | 200 + gpus 배열 |
| TC-14-06 | /api/metrics/gpu Prometheus 다운 | 서비스 PrometheusError 모킹 | 503 |
| TC-14-07 | Agent tool executor 오류 내성 | PrometheusError 모킹 | {"error": ...} 반환 (예외 전파 없음) |
| TC-14-08 | Orchestrator 배선 | import 검사 | _AGENT_MAP 에 gpu_monitoring/hardware, ExampleAgent 부재 |
| TC-14-09 | (통합, 수동) mock exporter→Prometheus→API | 라이브 스택 curl | GPU 4장 스냅샷 + 알람 규칙 7종 로드 |

## 실행
```bash
uv run pytest test/impl/14/ -v
```
TC-14-09 는 `make up` (prometheus + gpu-mock-exporter 기동) 후 수동 curl — result.md 에 기록.
