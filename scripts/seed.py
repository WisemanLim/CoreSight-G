#!/usr/bin/env python3
"""시드 스크립트 — 기본 설정 + 테스트 데이터 삽입.

Usage:
    uv run python scripts/seed.py
    make seed

포함 내용:
  - tbl_settings: LLM 기본값 (ollama, claude 모델명, setup_completed=false)
  - tbl_agent_config: ExampleAgent 기본 설정
  - tbl_users: supervisor(admin/Admin123!) + admin(test-admin/Admin123!) + user(test-user/User123!)
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings as _settings
from app.core.security import hash_password
from app.db import execute_write, fetch_one, run_migrations, apply_column_migrations


# env var / .env.* 파일 값 우선 반영 — 하드코딩 대신 settings.* 사용
SETTINGS = [
    ("orchestrator_model",  _settings.orchestrator_model, "Orchestrator LLM 모델"),
    ("domain_agent_model",  _settings.domain_agent_model, "Domain Agent LLM 모델"),
    ("ollama_base_url",     _settings.ollama_base_url,    "Ollama 서버 주소"),
    ("ollama_model",        _settings.ollama_model,       "Ollama 기본 모델"),
    ("fallback_enabled",    "true",                       "LLM Fallback 활성화"),
    ("setup_completed",     "false",                      "Setup Wizard 완료"),
]

AGENT_CONFIGS: list = []

TEST_USERS = [
    ("supervisor",     "supervisor",     "supervisor123!", "supervisor"),
    ("test-admin","테스트관리자",  "Admin123!", "admin"),
    ("test-user", "테스트사용자",  "User123!",  "user"),
]


async def main() -> None:
    # 스키마 보장 (아직 없으면 생성)
    await run_migrations()
    await apply_column_migrations()

    # tbl_settings
    for key, value, desc in SETTINGS:
        await execute_write(
            "INSERT OR IGNORE INTO tbl_settings (key, value, description) VALUES (?,?,?)",
            (key, value, desc),
        )
        print(f"[seed] settings: {key} = {value}")

    # tbl_agent_config
    for agent_key, agent_name, is_enabled, nav_group, sort_order in AGENT_CONFIGS:
        await execute_write(
            "INSERT OR IGNORE INTO tbl_agent_config "
            "(agent_key, agent_name, is_enabled, nav_group, sort_order) VALUES (?,?,?,?,?)",
            (agent_key, agent_name, is_enabled, nav_group, sort_order),
        )
        print(f"[seed] agent_config: {agent_key}")

    # tbl_users
    for user_id, username, password, role in TEST_USERS:
        row = await fetch_one("SELECT 1 FROM tbl_users WHERE user_id=?", (user_id,))
        if row:
            print(f"[seed] users: {user_id} (이미 존재, 건너뜀)")
        else:
            await execute_write(
                "INSERT INTO tbl_users (user_id, username, password, role) VALUES (?,?,?,?)",
                (user_id, username, hash_password(password), role),
            )
            print(f"[seed] users: {user_id} ({role}) 생성")

    print("\n[seed] 완료!")
    print("  supervisor: supervisor / supervisor123!")
    print("  admin:      test-admin / Admin123!")
    print("  user:       test-user / User123!")


if __name__ == "__main__":
    asyncio.run(main())
