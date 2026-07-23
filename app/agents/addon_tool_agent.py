"""AddonToolAgent — addon ZIP 구현체의 tool 을 tool_use 루프로 프록시하는 범용 Domain Agent.

관제 Agent 구현체(도구 정의·실행 로직·시스템 프롬프트)는 core 가 아니라
`addon-agents/zip/<agent>/<agent>-app.py` 에 있다 (PRD §7 관제 Agent 배포 구조).
이 클래스는 addon_agent_loader 가 이미 import 한 모듈(`sys.modules["addon_<key>"]`)에서
`_TOOLS` / `TOOL_EXECUTORS` / `SYSTEM_PROMPT` 를 읽어 BaseAgent 인터페이스로 노출만 한다.
"""
import sys
from typing import Any

from app.agents.base_agent import BaseAgent


class AddonToolAgent(BaseAgent):
    """addon 모듈의 tool 세트를 사용하는 Domain Agent. addon_key 별 서브클래스로 사용."""

    addon_key: str = ""  # 서브클래스에서 지정 (예: "gpu-monitor")

    def _module(self) -> Any | None:
        return sys.modules.get(f"addon_{self.addon_key}")

    def get_system_prompt(self) -> str:
        mod = self._module()
        prompt = getattr(mod, "SYSTEM_PROMPT", None) if mod else None
        if prompt:
            return prompt
        return (
            f"당신은 CoreSight-G 플랫폼의 관제 어시스턴트입니다. "
            f"'{self.addon_key}' addon 이 배포되지 않아 도구를 사용할 수 없습니다. "
            f"관리자에게 addon 배포(에이전트 관리 → Addon 등록)를 안내하세요."
        )

    def get_tools(self) -> list[dict[str, Any]]:
        mod = self._module()
        return list(getattr(mod, "_TOOLS", [])) if mod else []

    def get_tool_executors(self) -> dict[str, Any]:
        mod = self._module()
        return dict(getattr(mod, "TOOL_EXECUTORS", {})) if mod else {}


def addon_agent_cls(key: str, agent_key_alias: str | None = None) -> type[AddonToolAgent]:
    """addon_key 가 고정된 AddonToolAgent 서브클래스 생성 (Orchestrator _AGENT_MAP 용)."""
    return type(
        f"AddonToolAgent_{key.replace('-', '_')}",
        (AddonToolAgent,),
        {"addon_key": key, "agent_key": agent_key_alias or key},
    )
