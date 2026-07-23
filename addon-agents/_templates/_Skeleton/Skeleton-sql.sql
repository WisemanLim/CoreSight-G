-- Skeleton Addon Agent 스키마. [CUSTOMIZE] 도메인 테이블로 교체하세요.
CREATE TABLE IF NOT EXISTS tbl_skeleton_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  note TEXT DEFAULT '',
  created_by TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
