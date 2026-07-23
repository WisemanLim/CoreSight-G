import { useEffect, useState } from "react";
import { listAgentConfigs, patchAgentConfig, AgentConfig } from "../../api/agentConfig";
import {
  listAddonAgents, toggleAddonAgent, deleteAddonAgent, AddonAgent,
} from "../../api/addonAgents";
import { getMcpStatus, deleteMcpConfig, McpStatusColor } from "../../api/mcpConfig";
import { getAuth } from "../../store/auth";
import { useLocale } from "../../hooks/useLocale";
import AgentBuilderModal from "./AgentBuilderModal";
import McpGuideModal from "./McpGuideModal";
import McpEditModal from "./McpEditModal";

function IcRequired() {
  return (
    <span className="inline-flex items-center border-2 border-red-500 text-red-500 text-[9px] font-black px-1.5 py-0.5 rounded-sm tracking-widest uppercase leading-none select-none font-mono">
      REQUIRED
    </span>
  );
}

function Toggle({ checked, onChange }: { checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <button
      onClick={() => onChange(!checked)}
      className={`relative inline-flex h-7 w-16 items-center rounded-full transition-colors ${
        checked ? "bg-blue-600" : "bg-gray-300 dark:bg-gray-600"
      }`}
    >
      {checked ? (
        <>
          <span className="pl-2 text-[11px] font-bold text-white">ON</span>
          <span className="absolute right-1 inline-block h-5 w-5 rounded-full bg-white shadow" />
        </>
      ) : (
        <>
          <span className="absolute left-1 inline-block h-5 w-5 rounded-full bg-white shadow" />
          <span className="pr-2 ml-auto text-[11px] font-bold text-gray-500">OFF</span>
        </>
      )}
    </button>
  );
}

function IcPencil() {
  return (
    <svg viewBox="0 0 16 16" fill="currentColor" className="w-3.5 h-3.5">
      <path d="M11.013 1.427a1.75 1.75 0 0 1 2.474 0l1.086 1.086a1.75 1.75 0 0 1 0 2.474l-8.61 8.61c-.21.21-.47.364-.756.445l-3.251.93a.75.75 0 0 1-.927-.928l.929-3.25c.081-.286.235-.547.445-.758l8.61-8.61zm1.414 1.06a.25.25 0 0 0-.354 0L10.811 3.75l1.439 1.44 1.263-1.263a.25.25 0 0 0 0-.354l-1.086-1.086zM11.189 6.25 9.75 4.81 3.198 11.36a.25.25 0 0 0-.064.108l-.558 1.953 1.953-.558a.249.249 0 0 0 .108-.064z" />
    </svg>
  );
}

function IcTrash() {
  return (
    <svg viewBox="0 0 16 16" fill="currentColor" className="w-3.5 h-3.5">
      <path d="M6.5 1h3a.5.5 0 0 1 .5.5v1H6v-1a.5.5 0 0 1 .5-.5ZM11 2.5v-1A1.5 1.5 0 0 0 9.5 0h-3A1.5 1.5 0 0 0 5 1.5v1H1.5a.5.5 0 0 0 0 1h.538l.853 10.66A2 2 0 0 0 4.885 16h6.23a2 2 0 0 0 1.994-1.84l.853-10.66h.538a.5.5 0 0 0 0-1H11Zm1.958 1-.846 10.58a1 1 0 0 1-.997.92h-6.23a1 1 0 0 1-.997-.92L3.042 3.5h9.916ZM6.5 5a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 .5-.5Zm3 0a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 .5-.5Z" />
    </svg>
  );
}

function IcMinusCircle() {
  return (
    <svg viewBox="0 0 16 16" fill="currentColor" className="w-4 h-4">
      <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0ZM4.5 7.5a.5.5 0 0 0 0 1h7a.5.5 0 0 0 0-1h-7Z" />
    </svg>
  );
}

function McpGlobe({ color }: { color?: McpStatusColor }) {
  const isOnline = color === "green";
  const isOffline = color === "red" || color === "orange";
  const title = isOnline ? "MCP 온라인" : isOffline ? "MCP 오프라인" : "MCP 상태 확인 중";
  const strokeColor = isOnline ? "text-green-500" : isOffline ? "text-red-500" : "text-gray-300 dark:text-gray-600";

  return (
    <span className={`relative inline-flex shrink-0 ${!isOnline && !isOffline ? "animate-pulse" : ""}`} title={title}>
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.1" className={`w-4 h-4 ${strokeColor}`}>
        <circle cx="8" cy="8" r="6.5" />
        <ellipse cx="8" cy="8" rx="2.6" ry="6.5" />
        <line x1="1.5" y1="8" x2="14.5" y2="8" />
        <line x1="2.2" y1="5.2" x2="13.8" y2="5.2" />
        <line x1="2.2" y1="10.8" x2="13.8" y2="10.8" />
      </svg>
      {isOffline && (
        <svg viewBox="0 0 16 16" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round" className="w-4 h-4 absolute inset-0">
          <line x1="4" y1="4" x2="12" y2="12" />
          <line x1="12" y1="4" x2="4" y2="12" />
        </svg>
      )}
    </span>
  );
}

export default function AgentsPage() {
  const { t } = useLocale();
  const user = getAuth();
  const isAdmin = user?.role === "supervisor" || user?.role === "admin";

  const [configs, setConfigs] = useState<AgentConfig[]>([]);
  const [addons, setAddons]   = useState<AddonAgent[]>([]);
  const [loadingKey, setLoadingKey] = useState<string | null>(null);
  const [showBuilder, setShowBuilder] = useState(false);
  const [deleteKey, setDeleteKey]     = useState<string | null>(null);

  // MCP state
  const [mcpStatus, setMcpStatus]   = useState<Record<string, McpStatusColor>>({});
  const [mcpGuideKey, setMcpGuideKey] = useState<{ key: string; name: string } | null>(null);
  const [mcpEditKey, setMcpEditKey]   = useState<{ key: string; name: string } | null>(null);
  const [mcpDeleteKey, setMcpDeleteKey] = useState<string | null>(null);

  async function loadMcpStatuses(cfgs: AgentConfig[], ads: AddonAgent[]) {
    const keys = [
      ...cfgs.filter((c) => !c.is_required && c.is_enabled).map((c) => c.agent_key),
      ...ads.filter((a) => a.is_active).map((a) => a.agent_key),
    ];
    if (keys.length === 0) return;
    const results = await Promise.allSettled(keys.map((k) => getMcpStatus(k)));
    setMcpStatus((prev) => {
      const next = { ...prev };
      results.forEach((r, i) => {
        next[keys[i]] = r.status === "fulfilled" ? r.value.status : "red";
      });
      return next;
    });
  }

  async function refreshMcpStatus(key: string) {
    try {
      const s = await getMcpStatus(key);
      setMcpStatus((prev) => ({ ...prev, [key]: s.status }));
    } catch { /* noop */ }
  }

  async function reload() {
    const [c, a] = await Promise.all([listAgentConfigs(), listAddonAgents()]);
    setConfigs(c);
    setAddons(a);
    loadMcpStatuses(c, a);
  }

  useEffect(() => { reload(); }, []);

  async function handleToggle(key: string, enabled: boolean) {
    setLoadingKey(key);
    try {
      await patchAgentConfig(key, { is_enabled: enabled });
      setConfigs((prev) => prev.map((c) => (c.agent_key === key ? { ...c, is_enabled: enabled } : c)));
      window.dispatchEvent(new CustomEvent("agentConfigChanged"));
      refreshMcpStatus(key);
    } catch { /* ignore */ } finally {
      setLoadingKey(null);
    }
  }

  async function handleDeleteAddon(key: string) {
    try {
      await deleteAddonAgent(key);
      setDeleteKey(null);
      await reload();
      window.dispatchEvent(new CustomEvent("agentConfigChanged"));
    } catch { /* ignore */ }
  }

  async function handleToggleAddon(key: string) {
    setLoadingKey(key);
    try {
      const result = await toggleAddonAgent(key);
      setAddons((prev) => prev.map((a) => (a.agent_key === key ? { ...a, is_active: result.is_active } : a)));
      window.dispatchEvent(new CustomEvent("agentConfigChanged"));
      refreshMcpStatus(key);
    } catch { /* ignore */ } finally {
      setLoadingKey(null);
    }
  }

  async function handleMcpDelete(key: string) {
    try {
      await deleteMcpConfig(key);
    } catch { /* might not exist */ }
    setMcpDeleteKey(null);
    refreshMcpStatus(key);
  }

  function handleMcpSaved(key: string) {
    refreshMcpStatus(key);
  }

  function handleModalChanged() {
    reload();
    window.dispatchEvent(new CustomEvent("agentConfigChanged"));
  }

  const userAddonKeys = new Set(addons.filter((a) => !a.is_builtin).map((a) => a.agent_key));
  const builtinConfigs = configs.filter((c) => !userAddonKeys.has(c.agent_key));
  // nav_group 별 분리 (기본 Agent / 관제 Agent / ...) — 등장 순서 유지
  const builtinGroups: { name: string; items: typeof builtinConfigs }[] = [];
  for (const c of builtinConfigs) {
    const name = c.nav_group ?? t("common.default");
    const g = builtinGroups.find((x) => x.name === name);
    if (g) g.items.push(c);
    else builtinGroups.push({ name, items: [c] });
  }
  if (builtinGroups.length === 0) builtinGroups.push({ name: t("agent.builtin"), items: [] });
  const userAddons = addons.filter((a) => !a.is_builtin);

  // Shared MCP controls block
  function McpControls({ agentKey, agentName }: { agentKey: string; agentName: string }) {
    const status = mcpStatus[agentKey];
    return (
      <div className="flex items-center gap-1 border border-gray-200 dark:border-gray-600 rounded-md px-1.5 py-0.5 bg-gray-50 dark:bg-gray-700/40">
        {status === "green" ? (
          <button
            type="button"
            onClick={() => setMcpGuideKey({ key: agentKey, name: agentName })}
            className="transition-opacity hover:opacity-70"
            title={t("mcp.guide")}
          >
            <McpGlobe color={status} />
          </button>
        ) : (
          <McpGlobe color={status} />
        )}
        {isAdmin && (
          <>
            <button
              type="button"
              onClick={() => setMcpEditKey({ key: agentKey, name: agentName })}
              className="text-gray-400 dark:text-gray-500 hover:text-blue-500 dark:hover:text-blue-400 transition-colors"
              title={t("mcp.editTitle")}
            >
              <IcPencil />
            </button>
            {mcpDeleteKey === agentKey ? (
              <div className="flex items-center gap-1">
                <button
                  type="button"
                  onClick={() => handleMcpDelete(agentKey)}
                  className="text-xs px-1.5 py-0.5 rounded bg-red-500 text-white hover:bg-red-600 transition-colors"
                >
                  {t("mcp.deleteConfigConfirm")}
                </button>
                <button
                  type="button"
                  onClick={() => setMcpDeleteKey(null)}
                  className="text-xs px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300"
                >
                  {t("common.cancel")}
                </button>
              </div>
            ) : (
              <button
                type="button"
                onClick={() => setMcpDeleteKey(agentKey)}
                className="text-gray-300 dark:text-gray-600 hover:text-red-400 dark:hover:text-red-400 transition-colors"
                title={t("mcp.deleteConfig")}
              >
                <IcTrash />
              </button>
            )}
          </>
        )}
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 max-w-3xl">
      <h1 className="text-xl font-bold text-gray-800 dark:text-gray-100">{t("agent.management")}</h1>

      {/* Built-in Agents — nav_group 별 분리 (기본 Agent / 관제 Agent / ...) */}
      {builtinGroups.map((group) => (
      <section key={group.name}>
        <h2 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-3">
          {group.name}
        </h2>
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 divide-y divide-gray-100 dark:divide-gray-700">
          {group.items.length === 0 ? (
            <p className="text-sm text-gray-400 dark:text-gray-500 px-4 py-3">{t("agent.noAgents")}</p>
          ) : group.items.map((c) => (
            <div key={c.agent_key} className="flex items-center justify-between px-4 py-3">
              <div>
                <p className="text-sm font-medium text-gray-800 dark:text-gray-100">{c.agent_name}</p>
                <p className="text-xs text-gray-400 dark:text-gray-500">
                  {c.agent_key} · {c.nav_group ?? t("common.default")}
                </p>
              </div>
              <div className="flex items-center gap-1.5">
                {c.is_required ? (
                  <IcRequired />
                ) : isAdmin ? (
                  <Toggle checked={!!c.is_enabled} onChange={(v) => handleToggle(c.agent_key, v)} />
                ) : (
                  <span className={`text-xs px-2 py-0.5 rounded-full ${
                    c.is_enabled
                      ? "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400"
                      : "bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400"
                  }`}>
                    {c.is_enabled ? t("common.active") : t("common.inactive")}
                  </span>
                )}
                {loadingKey === c.agent_key && (
                  <span className="text-xs text-gray-400 dark:text-gray-500">{t("common.saving")}</span>
                )}
                {/* MCP controls — non-required, enabled */}
                {!c.is_required && !!c.is_enabled && (
                  <McpControls agentKey={c.agent_key} agentName={c.agent_name} />
                )}
              </div>
            </div>
          ))}
        </div>
      </section>
      ))}

      {/* Addon Agents */}
      <section>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
            {t("agent.addon")}
          </h2>
          {isAdmin && (
            <button
              type="button"
              onClick={() => setShowBuilder(true)}
              className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg bg-linear-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold transition-all"
            >
              <span>✦</span>
              새 Agent 만들기
            </button>
          )}
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 divide-y divide-gray-100 dark:divide-gray-700">
          {userAddons.length === 0 ? (
            <p className="text-sm text-gray-400 dark:text-gray-500 px-4 py-3">{t("agent.noAddon")}</p>
          ) : userAddons.map((a) => (
            <div key={a.agent_key} className="flex items-center justify-between px-4 py-3 gap-3">
              {/* Name / prefix */}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-800 dark:text-gray-100 truncate">{a.agent_name}</p>
                <p className="text-xs text-gray-400 dark:text-gray-500">{a.api_prefix}</p>
              </div>

              {/* Controls */}
              <div className="flex items-center gap-2 shrink-0">
                {/* Toggle */}
                {isAdmin ? (
                  <Toggle checked={!!a.is_active} onChange={() => handleToggleAddon(a.agent_key)} />
                ) : (
                  <span className={`text-xs px-2 py-0.5 rounded-full ${
                    a.is_active
                      ? "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400"
                      : "bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400"
                  }`}>
                    {a.is_active ? t("common.active") : t("common.inactive")}
                  </span>
                )}

                {loadingKey === a.agent_key && (
                  <span className="text-xs text-gray-400 dark:text-gray-500">{t("common.saving")}</span>
                )}

                {/* MCP controls — only when active */}
                {!!a.is_active && (
                  <McpControls agentKey={a.agent_key} agentName={a.agent_name} />
                )}

                {/* Addon delete — admin only */}
                {isAdmin && (
                  deleteKey === a.agent_key ? (
                    <div className="flex items-center gap-1">
                      <button
                        type="button"
                        onClick={() => handleDeleteAddon(a.agent_key)}
                        className="text-xs px-2 py-1 rounded-lg bg-red-500 text-white hover:bg-red-600 transition-colors"
                      >
                        {t("agent.deleteConfirm2")}
                      </button>
                      <button
                        type="button"
                        onClick={() => setDeleteKey(null)}
                        className="text-xs px-2 py-1 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300"
                      >
                        {t("common.cancel")}
                      </button>
                    </div>
                  ) : (
                    <button
                      type="button"
                      onClick={() => setDeleteKey(a.agent_key)}
                      className="text-gray-300 dark:text-gray-600 hover:text-red-500 dark:hover:text-red-400 transition-colors"
                      title={t("common.delete")}
                    >
                      <IcMinusCircle />
                    </button>
                  )
                )}
              </div>
            </div>
          ))}
        </div>
      </section>

      {showBuilder && (
        <AgentBuilderModal
          onClose={() => setShowBuilder(false)}
          onDeployed={() => { setShowBuilder(false); handleModalChanged(); }}
          onChanged={handleModalChanged}
        />
      )}

      {mcpGuideKey && (
        <McpGuideModal
          agentKey={mcpGuideKey.key}
          agentName={mcpGuideKey.name}
          onClose={() => setMcpGuideKey(null)}
        />
      )}

      {mcpEditKey && (
        <McpEditModal
          agentKey={mcpEditKey.key}
          agentName={mcpEditKey.name}
          onClose={() => setMcpEditKey(null)}
          onSaved={() => handleMcpSaved(mcpEditKey.key)}
        />
      )}
    </div>
  );
}
