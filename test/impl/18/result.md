# 시험 결과 — Iteration 18: 알림 채널 연동 + 관제 어시스턴트 E2E (P0 완결)

- 일시: 2026-07-22
- 판정: **PASS** (자동 6/6 + 라이브 파이프라인 + E2E)

## 자동 시험 (pytest)

```
uv run pytest test/impl/18/ -q → 6 passed
```

| ID | 결과 | 비고 |
|----|------|------|
| TC-18-01 webhook 토큰 검증 | PASS | 누락/오류 토큰 401 |
| TC-18-02 수신·저장 | PASS | stored=1, alertname/hostname 파라미터 확인 |
| TC-18-03 외부 중계 | PASS | notify_webhook_url 설정 시 POST 1회 (1차 실패 → `_forward_external` 직접 시험으로 재작성: httpx 전역 패치가 ASGI 테스트 클라이언트 오염) |
| TC-18-04 중계 실패 내성 | PASS | 예외 전파 없음 |
| TC-18-05 history 조회 | PASS | 200 + rows |
| TC-18-06 history 미인증 | PASS | 401/403 |

## 라이브 파이프라인 (TC-18-07)

`MOCK_ANOMALY=1` 재기동 후 약 1분:
- Prometheus alerts: GPUXidError(firing), GPUEccDbeIncrease(firing), GPUOverTemperature(pending), RAIDDegraded(firing)
- Alertmanager → `POST /api/alerts/webhook` 수신 → `tbl_alert_history` 3건 저장 확인
  (GPUXidError·GPUEccDbeIncrease: gpu-node-01/gpu3, RAIDDegraded: gpu-node-01)

## 관제 어시스턴트 E2E (TC-18-08)

- 환경: ANTHROPIC_API_KEY 미설정 → Ollama(llama3.2) 폴백 경로.
- SSE 흐름 확인: `intent` → `agent_start` → `delta` → `done`.
- 발견·수정: `_addon_api_specs` 가 tools 형 addon(gpu-monitor/hw-monitor)에 CRUD 경로를 안내해
  Ollama 가 `GET /api/addon/gpu-monitor` 호출 → 404. **tools 형 분기 추가**
  (`/tools/{tool_name}` 감지 시 `GET .../tools`, `POST .../tools/{name}` 안내) → 재시험에서
  올바른 경로 호출 확인.
- 제약: Ollama 폴백은 tool_use 미지원 — intent 분류·Domain Agent tool_use 루프 전체는
  `ANTHROPIC_API_KEY` 설정 시 동작 (README LLM 사전 설정 가이드 기재). 코드 경로는
  impl/14~16 자동시험으로 검증 완료.

## P0 상태

| P0 항목 | 상태 |
|---------|------|
| GPU 메트릭 수집 | ✅ (14차) |
| HW 메트릭 수집 | ✅ (14차) |
| 통합 대시보드 | ✅ (15차) |
| 필수 알람 + 채널 | ✅ (14차 규칙 + 18차 Alertmanager→webhook→이력·외부중계) |
| Multi AI Agent 관제 어시스턴트 | ✅ (14·16차 구현 + 18차 E2E — Claude 키는 운영 설정 사항) |
