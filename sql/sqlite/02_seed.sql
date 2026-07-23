-- coresight-g — 기본 시드 데이터 (idempotent, SQLite)

INSERT OR IGNORE INTO tbl_agent_config (agent_key, agent_name, is_enabled, is_required, nav_group, sort_order)
VALUES ('general', 'Orchestrator', 1, 1, '기본 Agent', 0);
UPDATE tbl_agent_config SET agent_name = 'Orchestrator', is_required = 1 WHERE agent_key = 'general';

INSERT OR IGNORE INTO tbl_agent_config (agent_key, agent_name, is_enabled, is_required, nav_group, sort_order)
VALUES ('chat', 'AI 어시스턴트', 1, 1, '기본 Agent', 1);
UPDATE tbl_agent_config SET agent_name = 'AI 어시스턴트', is_required = 1 WHERE agent_key = 'chat';

DELETE FROM tbl_agent_config WHERE agent_key = 'example';

-- Example Agent(board) 제거됨 — 도메인 Addon Agent 는 ZIP 업로드 또는 시드로 등록
DELETE FROM tbl_addon_agents WHERE agent_key = 'board';
DELETE FROM tbl_agent_config WHERE agent_key = 'board';

-- P1 Addon 에이전트는 agent_config(내장) 미등록 — ADDON 섹션·is_active 로 관리
DELETE FROM tbl_agent_config WHERE agent_key = 'log_analysis';
DELETE FROM tbl_agent_config WHERE agent_key = 'trace_analysis';

-- 관제 Agent 구현체 — addon-agents/zip/ ZIP 관리 (PRD §7 관제 Agent 배포 구조)
INSERT OR IGNORE INTO tbl_addon_agents
  (agent_key, agent_name, router_path, api_prefix, has_app, has_front, agent_type, is_builtin, is_active, uploaded_by)
VALUES
  ('gpu-monitor', 'GPU 모니터링 Agent', 'addon-agents/zip/gpu-monitor/gpu-monitor-app.py',
   '/api/addon/gpu-monitor', 1, 0, 'monitoring', 1, 1, 'system'),
  ('hw-monitor', '하드웨어 Agent', 'addon-agents/zip/hw-monitor/hw-monitor-app.py',
   '/api/addon/hw-monitor', 1, 0, 'monitoring', 1, 1, 'system');
UPDATE tbl_addon_agents SET router_path='addon-agents/zip/gpu-monitor/gpu-monitor-app.py',
  api_prefix='/api/addon/gpu-monitor', agent_type='monitoring', is_builtin=1 WHERE agent_key='gpu-monitor';
UPDATE tbl_addon_agents SET router_path='addon-agents/zip/hw-monitor/hw-monitor-app.py',
  api_prefix='/api/addon/hw-monitor', agent_type='monitoring', is_builtin=1 WHERE agent_key='hw-monitor';

INSERT OR IGNORE INTO tbl_addon_agents
  (agent_key, agent_name, router_path, api_prefix, has_app, has_front, agent_type, is_builtin, is_active, uploaded_by)
VALUES
  ('log-analyzer', '로그 분석 Agent', 'addon-agents/zip/log-analyzer/log-analyzer-app.py',
   '/api/addon/log-analyzer', 1, 0, 'monitoring', 0, 1, 'system');
UPDATE tbl_addon_agents SET router_path='addon-agents/zip/log-analyzer/log-analyzer-app.py',
  api_prefix='/api/addon/log-analyzer', agent_type='monitoring', is_builtin=0 WHERE agent_key='log-analyzer';

-- 관제 Domain Agent (PRD §7)
INSERT OR IGNORE INTO tbl_agent_config (agent_key, agent_name, is_enabled, is_required, nav_group, sort_order)
VALUES ('gpu_monitoring', 'GPU 모니터링 Agent', 1, 0, '관제 Agent', 2);
UPDATE tbl_agent_config SET agent_name = 'GPU 모니터링 Agent', nav_group = '관제 Agent' WHERE agent_key = 'gpu_monitoring';

INSERT OR IGNORE INTO tbl_agent_config (agent_key, agent_name, is_enabled, is_required, nav_group, sort_order)
VALUES ('hardware', '하드웨어 Agent', 1, 0, '관제 Agent', 3);
UPDATE tbl_agent_config SET agent_name = '하드웨어 Agent', nav_group = '관제 Agent' WHERE agent_key = 'hardware';


INSERT OR IGNORE INTO tbl_addon_agents
  (agent_key, agent_name, router_path, api_prefix, has_app, has_front, agent_type, is_builtin, is_active, uploaded_by)
VALUES
  ('trace-monitor', '트레이스 분석 Agent', 'addon-agents/zip/trace-monitor/trace-monitor-app.py',
   '/api/addon/trace-monitor', 1, 0, 'monitoring', 0, 1, 'system');
UPDATE tbl_addon_agents SET router_path='addon-agents/zip/trace-monitor/trace-monitor-app.py',
  api_prefix='/api/addon/trace-monitor', agent_type='monitoring', is_builtin=0 WHERE agent_key='trace-monitor';

INSERT OR IGNORE INTO tbl_addon_agents
  (agent_key, agent_name, router_path, api_prefix, has_app, has_front, agent_type, is_builtin, is_active, uploaded_by)
VALUES
  ('storage-monitor', '스토리지 진단 Agent', 'addon-agents/zip/storage-monitor/storage-monitor-app.py',
   '/api/addon/storage-monitor', 1, 0, 'monitoring', 0, 1, 'system');
UPDATE tbl_addon_agents SET router_path='addon-agents/zip/storage-monitor/storage-monitor-app.py',
  api_prefix='/api/addon/storage-monitor', agent_type='monitoring', is_builtin=0 WHERE agent_key='storage-monitor';

INSERT OR IGNORE INTO tbl_addon_agents
  (agent_key, agent_name, router_path, api_prefix, has_app, has_front, agent_type, is_builtin, is_active, uploaded_by)
VALUES
  ('bmc-monitor', 'BMC/IPMI Agent', 'addon-agents/zip/bmc-monitor/bmc-monitor-app.py',
   '/api/addon/bmc-monitor', 1, 0, 'monitoring', 0, 1, 'system');
UPDATE tbl_addon_agents SET router_path='addon-agents/zip/bmc-monitor/bmc-monitor-app.py',
  api_prefix='/api/addon/bmc-monitor', agent_type='monitoring', is_builtin=0 WHERE agent_key='bmc-monitor';
UPDATE tbl_addon_agents SET agent_name='BMC/IPMI Agent' WHERE agent_key='bmc-monitor';

INSERT OR IGNORE INTO tbl_addon_agents
  (agent_key, agent_name, router_path, api_prefix, has_app, has_front, agent_type, is_builtin, is_active, uploaded_by)
VALUES
  ('gpu-profiler', 'GPU 프로파일링 Agent', 'addon-agents/zip/gpu-profiler/gpu-profiler-app.py',
   '/api/addon/gpu-profiler', 1, 0, 'monitoring', 0, 1, 'system');
UPDATE tbl_addon_agents SET router_path='addon-agents/zip/gpu-profiler/gpu-profiler-app.py',
  api_prefix='/api/addon/gpu-profiler', agent_type='monitoring', is_builtin=0 WHERE agent_key='gpu-profiler';

INSERT OR IGNORE INTO tbl_addon_agents
  (agent_key, agent_name, router_path, api_prefix, has_app, has_front, agent_type, is_builtin, is_active, uploaded_by)
VALUES
  ('capacity-planner', '용량 계획 Agent', 'addon-agents/zip/capacity-planner/capacity-planner-app.py',
   '/api/addon/capacity-planner', 1, 0, 'monitoring', 0, 1, 'system');
UPDATE tbl_addon_agents SET router_path='addon-agents/zip/capacity-planner/capacity-planner-app.py',
  api_prefix='/api/addon/capacity-planner', agent_type='monitoring', is_builtin=0 WHERE agent_key='capacity-planner';

INSERT OR IGNORE INTO tbl_addon_agents
  (agent_key, agent_name, router_path, api_prefix, has_app, has_front, agent_type, is_builtin, is_active, uploaded_by)
VALUES
  ('anomaly-detector', '이상 탐지 Agent', 'addon-agents/zip/anomaly-detector/anomaly-detector-app.py',
   '/api/addon/anomaly-detector', 1, 0, 'monitoring', 0, 1, 'system');
UPDATE tbl_addon_agents SET router_path='addon-agents/zip/anomaly-detector/anomaly-detector-app.py',
  api_prefix='/api/addon/anomaly-detector', agent_type='monitoring', is_builtin=0 WHERE agent_key='anomaly-detector';

INSERT OR IGNORE INTO tbl_addon_agents
  (agent_key, agent_name, router_path, api_prefix, has_app, has_front, agent_type, is_builtin, is_active, uploaded_by)
VALUES
  ('net-monitor', '네트워크 모니터링 Agent', 'addon-agents/zip/net-monitor/net-monitor-app.py',
   '/api/addon/net-monitor', 1, 0, 'monitoring', 0, 1, 'system');
UPDATE tbl_addon_agents SET router_path='addon-agents/zip/net-monitor/net-monitor-app.py',
  api_prefix='/api/addon/net-monitor', agent_type='monitoring', is_builtin=0 WHERE agent_key='net-monitor';

INSERT OR IGNORE INTO tbl_addon_agents
  (agent_key, agent_name, router_path, api_prefix, has_app, has_front, agent_type, is_builtin, is_active, uploaded_by)
VALUES
  ('workload-correlator', '워크로드 상관 Agent', 'addon-agents/zip/workload-correlator/workload-correlator-app.py',
   '/api/addon/workload-correlator', 1, 0, 'monitoring', 0, 1, 'system');
UPDATE tbl_addon_agents SET router_path='addon-agents/zip/workload-correlator/workload-correlator-app.py',
  api_prefix='/api/addon/workload-correlator', agent_type='monitoring', is_builtin=0 WHERE agent_key='workload-correlator';


INSERT OR IGNORE INTO tbl_settings (key, value, description) VALUES
  ('orchestrator_model',  'claude-sonnet-4-6',       'Orchestrator LLM 모델'),
  ('domain_agent_model',  'claude-haiku-4-5-20251001','Domain Agent LLM 모델'),
  ('ollama_base_url',     'http://localhost:11434',    'Ollama 서버 주소'),
  ('ollama_model',        'llama3.2',                  'Ollama 기본 모델'),
  ('fallback_enabled',    'true',                      'LLM Fallback 활성화'),
  ('setup_completed',     'false',                     'Setup Wizard 완료'),
  ('system_custom_instructions', '',                  '시스템 전체 맞춤지침 (모든 사용자에게 적용)'),
  ('user_custom_instructions',   '',                  '사용자 공통 맞춤지침 (Supervisor가 정의하는 사용자 공통 제약·지침)');
