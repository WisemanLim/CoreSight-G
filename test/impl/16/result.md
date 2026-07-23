# 시험 결과 — Iteration 16: 관제 Agent 구현체 addon-agents/zip 분리

- 일시: 2026-07-22
- 판정: **PASS** (자동 7/7 + 회귀 14·15차 13/13 + 라이브 검증)

## 자동 시험 (pytest)

```
uv run pytest test/impl/16/ -v   → 7 passed
uv run pytest test/impl/14/ test/impl/15/ test/impl/16/ -q → 20 passed
```

| ID | 결과 | 비고 |
|----|------|------|
| TC-16-01 AddonToolAgent 모듈 위임 | PASS | fake 모듈 _TOOLS/EXECUTORS/PROMPT 그대로 노출 |
| TC-16-02 미배포 폴백 | PASS | tools=[], 배포 안내 프롬프트 |
| TC-16-03 orchestrator 배선 + core 구현체 제거 | PASS | addon_key 매핑, ImportError 확인 |
| TC-16-04 addon 모듈 규약 (gpu/hw) | PASS | router + tool↔executor 일치 + SYSTEM_PROMPT |
| TC-16-05 ZIP 패키지 (gpu/hw) | PASS | app.py/meta.json/guide.md 3파일 |

## 라이브 검증 (TC-16-06)

- 재기동 로그: `[addon_loader] loaded gpu-monitor → /api/addon/gpu-monitor`,
  `loaded hw-monitor → /api/addon/hw-monitor`, `restored 2/2 addon(s) from DB`
- `GET /api/addon/gpu-monitor/tools`: 도구 3종
- `POST /api/addon/gpu-monitor/tools/get_gpu_snapshot`: GPU 4장 스냅샷
- `GET /api/addon/hw-monitor/status`: `{"node_count":1,"faulty":0,"healthy":1}`

## 변경 요약

- 신설: `addon-agents/zip/{gpu-monitor,hw-monitor}/` (app.py + meta.json + worker-guide.md + zip),
  `app/agents/addon_tool_agent.py` (범용 프록시 — `sys.modules["addon_<key>"]` 의
  `_TOOLS`/`TOOL_EXECUTORS`/`SYSTEM_PROMPT` 위임)
- 삭제: `app/agents/gpu_monitoring_agent.py`, `app/agents/hardware_agent.py` (core 구현체 제거)
- 재배선: orchestrator `_AGENT_MAP`(addon_agent_cls), router_a2a, router_mcp
- 시드: tbl_addon_agents 에 gpu-monitor/hw-monitor (is_builtin=1, agent_type=monitoring, 멱등)
- impl/14 시험 3건을 신 아키텍처 기준으로 개정 (개정 사유 주석 명시, 본 result 는 원본 유지)

## 비고

- core 에 남는 것: Orchestrator, AI Assistant(general), 범용 AddonToolAgent 인프라.
  관제 도구 로직·프롬프트는 전부 zip 구현체 — 요구사항 "Orchestrator·AI Assistant 외 addon 분리" 충족.
- addon 업로드 UI(에이전트 관리 → Addon 등록)로 `<agent>.zip` 재배포 가능 (핫 디플로이).
