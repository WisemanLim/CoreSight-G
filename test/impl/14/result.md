# 시험 결과 — Iteration 14: GPU/HW 메트릭 수집 계층 + 관제 Domain Agent

- 일시: 2026-07-22
- 판정: **PASS** (자동 9/9 + 수동 통합 1/1)

## 자동 시험 (pytest)

```
uv run pytest test/impl/14/ -v
9 passed in 0.31s
```

| ID | 결과 | 비고 |
|----|------|------|
| TC-14-01 gpu_snapshot 병합 | PASS | vram_used_percent 50.0 계산 확인 |
| TC-14-02 hardware_snapshot 필터 | PASS | Hostname 없는 샘플 제외 + psu_failed=0 보정 |
| TC-14-03 연결 실패 | PASS | PrometheusError 발생 |
| TC-14-04 미인증 401/403 | PASS | gpu/hardware/alerts 3종 |
| TC-14-05 /api/metrics/gpu 200 | PASS | 서비스 모킹 |
| TC-14-06 Prometheus 다운 503 | PASS | |
| TC-14-07 tool executor 오류 내성 | PASS | {"error": ...} 반환, 예외 미전파 |
| TC-14-08 Orchestrator 배선 | PASS | gpu_monitoring/hardware 등록, ExampleAgent 제거 |
| + tools 스키마 일치 | PASS | tool ↔ executor 이름 일치 |

## 수동 통합 (TC-14-09, 라이브 스택)

- `docker compose up -d prometheus gpu-mock-exporter` → 기동 OK
- mock exporter `/metrics`: DCGM 메트릭 GPU 4장 노출 확인
- Prometheus targets: `dcgm` job `up` / 알람 규칙 7종 로드
  (GPUXidError, GPUEccDbeIncrease, GPUOverTemperature, GPUMemoryHigh, RAIDDegraded, PSUFailure, ExporterDown)
- `GET /api/metrics/gpu` (test-admin 토큰): GPU 4장 스냅샷 + vram_used_percent 응답 확인
- `GET /api/metrics/hardware`: gpu-node-01 CPU/메모리/RAID/PSU/온도 응답 확인
- `GET /api/metrics/alerts`: `{"alerts":[]}` (정상 상태 — MOCK_ANOMALY=1 시 발화 예정)

## 발견·수정 사항

1. `hardware_snapshot` 의 `or vector(0)` 폴백이 Hostname 없는 가짜 "cluster" 노드를 생성
   → Hostname 라벨 없는 샘플 제외 + psu_failed 결측 시 0 보정으로 수정 후 재시험 PASS.

## 알려진 이슈 (본 차수 범위 밖, 레거시)

- `test/impl/1,3,4,5` 상당수 ERROR/FAILED — 템플릿 시절부터 라이브 서버·시드 계정
  (`admin`) 전제의 통합 시험. 현 로컬 시드 계정은 `test-admin`/`supervisor`.
- `test/impl/5::test_t3_mcp_tools_call` FAILED — 제거된 ExampleAgent 의 `get_example_data`
  tool 호출. 레거시 차수 문서 보존 원칙에 따라 수정하지 않음.
- `test/impl/6` MCP config 시험 중 원격 URL ping 으로 전체 suite 행(hang) —
  개별 차수 실행(`pytest test/impl/14/`) 권장. 레거시 차수 정리는 후속 결정 필요.
