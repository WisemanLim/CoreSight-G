"""DB 초기화·마이그레이션·시드 헬퍼."""
import logging

from app.core.config import settings
from app.core.security import hash_password

logger = logging.getLogger("uvicorn.error")

_IS_SQLITE = settings.database_url.startswith("sqlite")
_PH = "?" if _IS_SQLITE else "%s"


def _db_path() -> str:
    return settings.database_url.replace("sqlite:///./", "./").replace("sqlite:///", "")


async def fetch_one(sql: str, params: tuple = ()) -> dict | None:
    if _IS_SQLITE:
        import aiosqlite
        async with aiosqlite.connect(_db_path()) as conn:
            conn.row_factory = aiosqlite.Row
            async with conn.execute(sql, params) as cur:
                row = await cur.fetchone()
                return dict(row) if row else None
    else:
        import psycopg2, psycopg2.extras  # noqa: E401
        conn = psycopg2.connect(settings.database_url)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params)
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None


async def fetch_all(sql: str, params: tuple = ()) -> list[dict]:
    if _IS_SQLITE:
        import aiosqlite
        async with aiosqlite.connect(_db_path()) as conn:
            conn.row_factory = aiosqlite.Row
            async with conn.execute(sql, params) as cur:
                rows = await cur.fetchall()
                return [dict(r) for r in rows]
    else:
        import psycopg2, psycopg2.extras  # noqa: E401
        conn = psycopg2.connect(settings.database_url)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params)
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]


async def execute_write(sql: str, params: tuple = ()) -> None:
    if _IS_SQLITE:
        import aiosqlite
        async with aiosqlite.connect(_db_path()) as conn:
            await conn.execute(sql, params)
            await conn.commit()
    else:
        import psycopg2
        conn = psycopg2.connect(settings.database_url)
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        conn.close()


async def execute_insert(sql: str, params: tuple = ()) -> int:
    """INSERT 실행 후 생성된 row id 반환."""
    if _IS_SQLITE:
        import aiosqlite
        async with aiosqlite.connect(_db_path()) as conn:
            cur = await conn.execute(sql, params)
            await conn.commit()
            return cur.lastrowid or 0
    else:
        import psycopg2
        pg_sql = sql.rstrip().rstrip(";") + " RETURNING id"
        conn = psycopg2.connect(settings.database_url)
        cur = conn.cursor()
        cur.execute(pg_sql, params)
        row = cur.fetchone()
        conn.commit()
        conn.close()
        return row[0] if row else 0


async def run_migrations() -> None:
    """SQL 파일 순차 실행 (idempotent — IF NOT EXISTS 전제)."""
    import glob

    sql_dir = "sql/sqlite" if _IS_SQLITE else "sql/pg"
    sql_files = sorted(glob.glob(f"{sql_dir}/*.sql"))
    if not sql_files:
        return

    if _IS_SQLITE:
        import aiosqlite
        async with aiosqlite.connect(_db_path()) as conn:
            for path in sql_files:
                with open(path) as f:
                    await conn.executescript(f.read())
            await conn.commit()
    else:
        import psycopg2
        conn = psycopg2.connect(settings.database_url)
        conn.autocommit = True
        cur = conn.cursor()
        for path in sql_files:
            with open(path) as f:
                cur.execute(f.read())
        conn.close()

    logger.info("[db] migrations OK (%d files, %s)", len(sql_files), sql_dir)


def _apply_pg_column_migrations() -> None:
    """PostgreSQL: ADD COLUMN IF NOT EXISTS (멱등, PostgreSQL 9.6+)."""
    import psycopg2
    migrations = [
        "ALTER TABLE tbl_agent_config ADD COLUMN IF NOT EXISTS model TEXT",
        "ALTER TABLE tbl_agent_config ADD COLUMN IF NOT EXISTS system_prompt TEXT",
        "ALTER TABLE tbl_agent_config ADD COLUMN IF NOT EXISTS is_required INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE tbl_users ADD COLUMN IF NOT EXISTS totp_secret TEXT",
        "ALTER TABLE tbl_users ADD COLUMN IF NOT EXISTS totp_enabled INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE tbl_users ADD COLUMN IF NOT EXISTS custom_instructions TEXT",
        "ALTER TABLE tbl_addon_agents ADD COLUMN IF NOT EXISTS has_app INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE tbl_addon_agents ADD COLUMN IF NOT EXISTS agent_type TEXT NOT NULL DEFAULT 'app'",
        "ALTER TABLE tbl_addon_agents ADD COLUMN IF NOT EXISTS meta_json TEXT",
        # F23: tbl_agent_registry v2 columns
        "ALTER TABLE tbl_agent_registry ADD COLUMN IF NOT EXISTS agent_type TEXT NOT NULL DEFAULT 'service'",
        "ALTER TABLE tbl_agent_registry ADD COLUMN IF NOT EXISTS capabilities_json TEXT",
        "ALTER TABLE tbl_agent_registry ADD COLUMN IF NOT EXISTS agent_card_json TEXT",
        "ALTER TABLE tbl_agent_registry ADD COLUMN IF NOT EXISTS lifecycle_state TEXT NOT NULL DEFAULT 'active'",
        "ALTER TABLE tbl_agent_registry ADD COLUMN IF NOT EXISTS health_score NUMERIC(5,4) NOT NULL DEFAULT 1.0",
        "ALTER TABLE tbl_agent_registry ADD COLUMN IF NOT EXISTS last_heartbeat_at TIMESTAMP",
        "ALTER TABLE tbl_agent_registry ADD COLUMN IF NOT EXISTS lease_expires_at TIMESTAMP",
        # F23: tbl_addon_agent_capabilities (new table)
        """CREATE TABLE IF NOT EXISTS tbl_addon_agent_capabilities (
            id SERIAL PRIMARY KEY, agent_key VARCHAR(50) NOT NULL,
            capability_key VARCHAR(100) NOT NULL, verb VARCHAR(50) NOT NULL,
            domain VARCHAR(200) NOT NULL, description TEXT,
            input_schema TEXT, output_schema TEXT, qos_json TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            UNIQUE(agent_key, capability_key))""",
    ]
    conn = psycopg2.connect(settings.database_url)
    conn.autocommit = True
    cur = conn.cursor()
    for sql in migrations:
        try:
            cur.execute(sql)
        except Exception as e:
            logger.warning("[db] pg column migration skip: %s", e)
    conn.close()
    logger.info("[db] pg column migrations OK")


async def apply_column_migrations() -> None:
    """기존 DB에 누락된 컬럼을 추가한다 (ALTER TABLE, 멱등)."""
    if not _IS_SQLITE:
        _apply_pg_column_migrations()
        return
    import aiosqlite
    async with aiosqlite.connect(_db_path()) as conn:
        async with conn.execute("PRAGMA table_info(tbl_agent_config)") as cur:
            cols = {row[1] async for row in cur}
        for col, typedef in [
            ("model", "TEXT"),
            ("system_prompt", "TEXT"),
            ("is_required", "INTEGER NOT NULL DEFAULT 0"),
        ]:
            col_name = col.split()[0]
            if col_name not in cols:
                await conn.execute(f"ALTER TABLE tbl_agent_config ADD COLUMN {col} {typedef}")
                logger.info("[db] added column tbl_agent_config.%s", col_name)

    # tbl_users — TOTP columns
    async with aiosqlite.connect(_db_path()) as conn:
        async with conn.execute("PRAGMA table_info(tbl_users)") as cur:
            user_cols = {row[1] async for row in cur}
        for col, typedef in [
            ("totp_secret", "TEXT"),
            ("totp_enabled", "INTEGER NOT NULL DEFAULT 0"),
            ("custom_instructions", "TEXT"),
        ]:
            col_name = col.split()[0]
            if col_name not in user_cols:
                await conn.execute(f"ALTER TABLE tbl_users ADD COLUMN {col_name} {typedef}")
                logger.info("[db] added column tbl_users.%s", col_name)
        await conn.commit()

    # tbl_addon_agents — has_app + agent_type + meta_json columns (F22)
    async with aiosqlite.connect(_db_path()) as conn:
        async with conn.execute("PRAGMA table_info(tbl_addon_agents)") as cur:
            addon_cols = {row[1] async for row in cur}
        for col, typedef in [
            ("has_app", "INTEGER NOT NULL DEFAULT 0"),
            ("agent_type", "TEXT NOT NULL DEFAULT 'app'"),
            ("meta_json", "TEXT"),
        ]:
            if col not in addon_cols:
                await conn.execute(f"ALTER TABLE tbl_addon_agents ADD COLUMN {col} {typedef}")
                logger.info("[db] added column tbl_addon_agents.%s", col)
        await conn.commit()

    # tbl_agent_registry — F23 v2 columns
    async with aiosqlite.connect(_db_path()) as conn:
        async with conn.execute("PRAGMA table_info(tbl_agent_registry)") as cur:
            reg_cols = {row[1] async for row in cur}
        for col, typedef in [
            ("agent_type", "TEXT NOT NULL DEFAULT 'service'"),
            ("capabilities_json", "TEXT"),
            ("agent_card_json", "TEXT"),
            ("lifecycle_state", "TEXT NOT NULL DEFAULT 'active'"),
            ("health_score", "REAL NOT NULL DEFAULT 1.0"),
            ("last_heartbeat_at", "TIMESTAMP"),
            ("lease_expires_at", "TIMESTAMP"),
        ]:
            if col not in reg_cols:
                await conn.execute(f"ALTER TABLE tbl_agent_registry ADD COLUMN {col} {typedef}")
                logger.info("[db] added column tbl_agent_registry.%s", col)
        # tbl_addon_agent_capabilities (새 테이블)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS tbl_addon_agent_capabilities (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_key      TEXT NOT NULL,
                capability_key TEXT NOT NULL,
                verb           TEXT NOT NULL,
                domain         TEXT NOT NULL,
                description    TEXT,
                input_schema   TEXT,
                output_schema  TEXT,
                qos_json       TEXT,
                created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(agent_key, capability_key)
            )
        """)
        await conn.commit()
        logger.info("[db] tbl_addon_agent_capabilities ensured")


async def seed_default_admin() -> None:
    """DEFAULT_ADMIN_USER_ID/PASSWORD 환경변수 설정 시에만 기본 관리자 계정 생성."""
    if not settings.default_admin_user_id or not settings.default_admin_password:
        return
    row = await fetch_one("SELECT COUNT(*) as cnt FROM tbl_users")
    if row and row["cnt"] == 0:
        await execute_write(
            f"INSERT INTO tbl_users (user_id, username, password, role) VALUES ({_PH},{_PH},{_PH},{_PH})",
            (
                settings.default_admin_user_id,
                settings.default_admin_user_id,
                hash_password(settings.default_admin_password),
                "supervisor",
            ),
        )
        logger.info("[db] default admin created: %s", settings.default_admin_user_id)
