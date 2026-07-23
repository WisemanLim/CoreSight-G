# 시험 시나리오 — Iteration 18: 알림 채널 연동 (P0 완결) + 관제 어시스턴트 E2E

## 범위
- Alertmanager (compose `alertmanager`, group_wait 10s) — Prometheus `alerting` 연결
- `POST /api/alerts/webhook` (Bearer 토큰 검증, tbl_alert_history 저장, notify_webhook_url 중계)
- `GET /api/alerts/history` (인증, 최신순, limit)
- P0 "Multi AI Agent 기반 관제 어시스턴트" E2E — 자연어 질의 → intent → addon tool_use → SSE

## 테스트 케이스

| ID | 내용 | 방법 | 기대 결과 |
|----|------|------|----------|
| TC-18-01 | webhook 토큰 검증 | 잘못된/누락 토큰 | 401 |
| TC-18-02 | webhook 수신·저장 | 유효 토큰 + Alertmanager 형식 payload | 200 {stored:N}, DB 행 생성 |
| TC-18-03 | 외부 중계 | notify_webhook_url 설정 + httpx 모킹 | 외부 POST 1회 호출 |
| TC-18-04 | 외부 중계 실패 내성 | httpx 예외 모킹 | 수신 응답은 200 유지 |
| TC-18-05 | history 조회 | 인증 오버라이드 | 200, 최신순, limit 반영 |
| TC-18-06 | history 미인증 | 토큰 없이 | 401/403 |
| TC-18-07 | (라이브) 알람 파이프라인 | MOCK_ANOMALY=1 → 규칙 발화 → Alertmanager → webhook | tbl_alert_history 에 GPUXidError 등 저장 |
| TC-18-08 | (라이브) 관제 어시스턴트 E2E | `/api/agent/chat/stream` "GPU 상태 알려줘" | intent=gpu_monitoring → tool_call/tool_result → delta SSE |

## 실행
```bash
uv run pytest test/impl/18/ -v
```
