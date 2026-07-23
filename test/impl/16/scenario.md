# 시험 시나리오 — Iteration 16: 관제 Agent 구현체 addon-agents/zip 분리 (PRD §7)

## 범위
- `addon-agents/zip/{gpu-monitor,hw-monitor}/` — `<agent>-app.py`(router+`_TOOLS`+`TOOL_EXECUTORS`+`SYSTEM_PROMPT`)
  + `<agent>-meta.json` + `<agent>-worker-guide.md` + 패키징 `<agent>.zip`
- core: `app/agents/addon_tool_agent.py`(범용 프록시) 신설, `gpu_monitoring_agent.py`/`hardware_agent.py` 삭제
- orchestrator/_AGENT_MAP·A2A·MCP → AddonToolAgent 로 재배선
- 시드: tbl_addon_agents 에 gpu-monitor/hw-monitor (is_builtin=1, agent_type=monitoring)

## 테스트 케이스

| ID | 내용 | 방법 | 기대 결과 |
|----|------|------|----------|
| TC-16-01 | AddonToolAgent 모듈 위임 | fake 모듈 sys.modules 주입 | _TOOLS/TOOL_EXECUTORS/SYSTEM_PROMPT 그대로 노출 |
| TC-16-02 | addon 미배포 폴백 | 모듈 없음 | tools=[], 안내 프롬프트 |
| TC-16-03 | orchestrator 배선 | import 검사 | _AGENT_MAP addon_key 매핑, core 관제 Agent 파일 부재 |
| TC-16-04 | addon 모듈 규약 | importlib 로 양쪽 app.py 로드 | router + _TOOLS ↔ TOOL_EXECUTORS 이름 일치 |
| TC-16-05 | ZIP 패키지 | zipfile 검사 | app.py/meta.json/guide.md 3파일 포함 |
| TC-16-06 | (수동, 라이브) 로더 복원 | pm2 재기동 로그 | restored 2/2, /api/addon/*-monitor/tools 200 |

## 실행
```bash
uv run pytest test/impl/16/ -v
```
