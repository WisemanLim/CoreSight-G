"""Phase 16 — 관제 Agent addon-agents/zip 분리 시험."""
import importlib.util
import os
import sys
import types
import zipfile
from pathlib import Path

import pytest

os.environ.setdefault("ENV", "local")

ZIP_DIR = Path("addon-agents/zip")


# ── TC-16-01: AddonToolAgent 모듈 위임 ──────────────────────────────────────

def test_addon_tool_agent_delegates_to_module():
    from app.agents.addon_tool_agent import addon_agent_cls

    fake = types.ModuleType("addon_fake-mon")
    fake._TOOLS = [{"name": "t1", "description": "d", "input_schema": {"type": "object"}}]

    async def t1(tool_input):
        return {"ok": True}

    fake.TOOL_EXECUTORS = {"t1": t1}
    fake.SYSTEM_PROMPT = "fake prompt"
    sys.modules["addon_fake-mon"] = fake
    try:
        agent = addon_agent_cls("fake-mon")()
        assert agent.get_tools() == fake._TOOLS
        assert set(agent.get_tool_executors()) == {"t1"}
        assert agent.get_system_prompt() == "fake prompt"
    finally:
        del sys.modules["addon_fake-mon"]


# ── TC-16-02: addon 미배포 폴백 ─────────────────────────────────────────────

def test_addon_tool_agent_fallback_when_missing():
    from app.agents.addon_tool_agent import addon_agent_cls

    agent = addon_agent_cls("not-deployed")()
    assert agent.get_tools() == []
    assert agent.get_tool_executors() == {}
    assert "not-deployed" in agent.get_system_prompt()


# ── TC-16-03: orchestrator 배선 + core 구현체 제거 ──────────────────────────

def test_orchestrator_uses_addon_agents():
    from app.agents import orchestrator as orc

    assert orc._AGENT_MAP["gpu_monitoring"].addon_key == "gpu-monitor"
    assert orc._AGENT_MAP["hardware"].addon_key == "hw-monitor"

    with pytest.raises(ImportError):
        import app.agents.gpu_monitoring_agent  # noqa: F401
    with pytest.raises(ImportError):
        import app.agents.hardware_agent  # noqa: F401


# ── TC-16-04: addon 모듈 규약 (loader 와 동일 방식 로드) ────────────────────

@pytest.mark.parametrize("key", ["gpu-monitor", "hw-monitor"])
def test_addon_module_contract(key):
    path = ZIP_DIR / key / f"{key}-app.py"
    spec = importlib.util.spec_from_file_location(f"testload_{key}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert getattr(module, "router", None) is not None
    tools = module._TOOLS
    executors = module.TOOL_EXECUTORS
    assert {t["name"] for t in tools} == set(executors)  # tool ↔ executor 일치
    assert isinstance(module.SYSTEM_PROMPT, str) and module.SYSTEM_PROMPT


# ── TC-16-05: ZIP 패키지 구성 ───────────────────────────────────────────────

@pytest.mark.parametrize("key", ["gpu-monitor", "hw-monitor"])
def test_zip_package_contents(key):
    with zipfile.ZipFile(ZIP_DIR / f"{key}.zip") as zf:
        names = set(zf.namelist())
    assert names == {f"{key}-app.py", f"{key}-meta.json", f"{key}-worker-guide.md"}
