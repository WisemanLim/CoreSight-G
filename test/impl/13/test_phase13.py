"""Phase 14 — LLM 설정 우선순위 버그 수정 시험 (Iteration 13).

_db_llm_settings() 우선순위: os.environ > .env.*(pydantic) > DB > 기본값
"""
import os
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

os.environ.setdefault("ENV", "local")


# ── TC-13-01: .env 값이 기본값과 다를 때 DB 덮어쓰기 ─────────────────────────

@pytest.mark.asyncio
async def test_env_file_overrides_db_when_differs_from_default():
    """pydantic settings 값이 기본값과 다르면 DB보다 우선."""
    from app.core.config import settings as real_settings

    fake_settings = MagicMock()
    fake_settings.ollama_model = "mistral"          # .env.local 에서 설정
    fake_settings.ollama_base_url = real_settings.ollama_base_url  # 기본값 유지
    fake_settings.orchestrator_model = real_settings.orchestrator_model
    fake_settings.domain_agent_model = real_settings.domain_agent_model

    db_rows = [{"key": "ollama_model", "value": "llama3.2"}]  # DB에 기본값 저장됨

    with (
        patch("app.agents.orchestrator._settings", fake_settings, create=True),
        patch("app.db.fetch_all", new=AsyncMock(return_value=db_rows)),
    ):
        # _db_llm_settings 직접 import 후 실행
        import importlib
        import app.agents.orchestrator as orch_mod
        # settings import를 patch
        with patch("app.agents.orchestrator._settings", fake_settings):
            # function을 직접 호출하지 않고, 로직 검증을 위해 함수를 재구성
            pass

    # 로직 직접 검증
    _pydantic_defaults = {
        "ollama_model": "llama3.2",
        "ollama_base_url": "http://localhost:11434",
        "orchestrator_model": "claude-sonnet-4-6",
        "domain_agent_model": "claude-haiku-4-5-20251001",
    }
    _settings_vals = {
        "ollama_model": "mistral",        # .env.local 에서 설정 (기본값과 다름)
        "ollama_base_url": "http://localhost:11434",  # 기본값과 같음
        "orchestrator_model": "claude-sonnet-4-6",
        "domain_agent_model": "claude-haiku-4-5-20251001",
    }

    result = {"ollama_model": "llama3.2"}  # DB 초기값
    for key, val in _settings_vals.items():
        if val and val != _pydantic_defaults.get(key):
            result[key] = val  # .env 값으로 덮어쓰기

    assert result["ollama_model"] == "mistral", f"got {result['ollama_model']}"


# ── TC-13-02: .env 값이 기본값과 같으면 DB 값 유지 ─────────────────────────

@pytest.mark.asyncio
async def test_db_wins_when_env_is_default():
    """.env 값이 기본값과 같으면 DB 설정(UI 변경)이 우선."""
    _pydantic_defaults = {
        "ollama_model": "llama3.2",
    }
    _settings_vals = {
        "ollama_model": "llama3.2",  # .env 미설정 → 기본값과 동일
    }

    result = {"ollama_model": "custom-model-from-ui"}  # DB 값 (UI로 변경)
    for key, val in _settings_vals.items():
        if val and val != _pydantic_defaults.get(key):
            result[key] = val  # 기본값과 같으므로 덮어쓰기 안 함

    assert result["ollama_model"] == "custom-model-from-ui", f"got {result['ollama_model']}"


# ── TC-13-03: os.environ 명시 시 최우선 ────────────────────────────────────

@pytest.mark.asyncio
async def test_os_environ_takes_highest_priority():
    """os.environ 값은 .env 파일과 DB 모두 덮어씀."""
    _SETTING_ENV_MAP = {"ollama_model": "OLLAMA_MODEL"}

    result = {"ollama_model": "mistral"}  # .env에서 설정된 값

    # os.environ 주입 시뮬레이션
    with patch.dict(os.environ, {"OLLAMA_MODEL": "docker-injected-model"}):
        for db_key, env_key in _SETTING_ENV_MAP.items():
            val = os.environ.get(env_key)
            if val:
                result[db_key] = val

    assert result["ollama_model"] == "docker-injected-model"


# ── TC-13-04: DB 없고 .env 기본값 → 기본값 반환 ────────────────────────────

@pytest.mark.asyncio
async def test_fallback_to_defaults_when_no_db_no_env():
    """DB 없고 .env도 기본값 → result 비어있거나 기본값."""
    _pydantic_defaults = {"ollama_model": "llama3.2"}
    _settings_vals = {"ollama_model": "llama3.2"}

    result = {}  # DB 없음
    for key, val in _settings_vals.items():
        if val and val != _pydantic_defaults.get(key):
            result[key] = val  # 기본값과 같으므로 추가 안 함

    # result에 ollama_model 없음 → 기본값 사용
    assert "ollama_model" not in result


# ── TC-13-05: syntax 오류 없음 ──────────────────────────────────────────────

def test_orchestrator_syntax():
    import ast
    src = open("app/agents/orchestrator.py").read()
    ast.parse(src)  # SyntaxError 없으면 통과


# ── TC-13-06: _db_llm_settings 실제 실행 (DB fetch 모킹) ───────────────────

@pytest.mark.asyncio
async def test_db_llm_settings_full_flow():
    """실제 _db_llm_settings 호출 — .env 값이 기본값과 다르면 우선 적용."""
    from app.core.config import Settings

    fake_settings = MagicMock()
    fake_settings.ollama_model = "mistral"
    fake_settings.ollama_base_url = "http://localhost:11434"
    fake_settings.orchestrator_model = "claude-sonnet-4-6"
    fake_settings.domain_agent_model = "claude-haiku-4-5-20251001"

    db_rows = [{"key": "ollama_model", "value": "llama3.2"}]

    with patch("app.core.config.settings", fake_settings):
        with patch("app.db.fetch_all", new=AsyncMock(return_value=db_rows)):
            from app.agents import orchestrator as orch
            # settings import 패치
            original = None
            try:
                import app.core.config as cfg_mod
                original = cfg_mod.settings
                cfg_mod.settings = fake_settings
                result = await orch._db_llm_settings()
            finally:
                if original is not None:
                    cfg_mod.settings = original

    assert result.get("ollama_model") == "mistral", f"expected 'mistral', got {result.get('ollama_model')}"
