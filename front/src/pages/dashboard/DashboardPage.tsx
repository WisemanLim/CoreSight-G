/**
 * DashboardPage — GPU + 서버 하드웨어 통합 대시보드 (PRD §3 P0).
 * 15s 폴링(Prometheus scrape 주기와 동일). 노드 단위 상관 조회 + 활성 알람 배너.
 */
import { useCallback, useEffect, useState } from "react";
import client from "../../api/client";
import { listAgentConfigs } from "../../api/agentConfig";
import { listAddonAgents } from "../../api/addonAgents";
import { useLocale } from "../../hooks/useLocale";
import {
  getAlerts,
  getGpuHistory,
  getGpuMetrics,
  getHardwareMetrics,
  type ActiveAlert,
  type GpuMetric,
  type GpuUtilSeries,
  type HardwareNode,
} from "../../api/metrics";

/** 활성 addon 의 대시보드 위젯 (GET /api/addon/<key>/status 규약). 미제공 addon 은 스킵. */
interface AddonWidget {
  key: string;
  name: string;
  data: Record<string, unknown>;
}

// GPU/HW 는 전용 섹션이 있으므로 위젯 그리드에서 제외
const DEDICATED_SECTION_ADDONS = new Set(["gpu-monitor", "hw-monitor"]);

// addon_key → 에이전트 관리(관제 Agent) 토글 키 매핑. 미등록 addon 은 '-'→'_' 규약으로 유도
const ADDON_CONFIG_KEY: Record<string, string> = {
  "gpu-monitor": "gpu_monitoring",
  "hw-monitor": "hardware",
  "log-analyzer": "log_analysis",
  "trace-monitor": "trace_analysis",
};

function configKeyOf(addonKey: string): string {
  return ADDON_CONFIG_KEY[addonKey] ?? addonKey.replace(/-/g, "_");
}

const REFRESH_MS = 15_000;

/* ── 색상 헬퍼 ─────────────────────────────────────────── */

function barColor(pct: number, warn: number, crit: number): string {
  if (pct >= crit) return "bg-red-500";
  if (pct >= warn) return "bg-amber-500";
  return "bg-blue-500";
}

function Bar({ pct, warn, crit }: Readonly<{ pct: number; warn: number; crit: number }>) {
  return (
    <div className="h-1.5 w-full rounded-full bg-gray-200 dark:bg-gray-700 overflow-hidden">
      <div
        className={`h-full rounded-full transition-all ${barColor(pct, warn, crit)}`}
        style={{ width: `${Math.min(100, Math.max(0, pct))}%` }}
      />
    </div>
  );
}

function Sparkline({ points }: Readonly<{ points: [number, number][] }>) {
  if (points.length < 2) return null;
  const w = 120;
  const h = 28;
  const xs = points.map((p) => p[0]);
  const min = Math.min(...xs);
  const max = Math.max(...xs);
  const path = points
    .map(([ts, v], i) => {
      const x = ((ts - min) / (max - min || 1)) * w;
      const y = h - (Math.min(100, v) / 100) * h;
      return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
  return (
    <svg width={w} height={h} className="text-blue-500" aria-hidden>
      <path d={path} fill="none" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  );
}

/* ── 페이지 ────────────────────────────────────────────── */

export default function DashboardPage() {
  const { t } = useLocale();
  const [gpus, setGpus] = useState<GpuMetric[]>([]);
  const [nodes, setNodes] = useState<HardwareNode[]>([]);
  const [alerts, setAlerts] = useState<ActiveAlert[]>([]);
  const [history, setHistory] = useState<GpuUtilSeries[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [updatedAt, setUpdatedAt] = useState<Date | null>(null);
  // 관제 Agent 활성화 연동: 비활성 Agent 의 섹션은 숨김 (조회 실패 시 기본 표시 유지)
  const [enabled, setEnabled] = useState<Record<string, boolean>>({
    gpu_monitoring: true,
    hardware: true,
  });
  const [widgets, setWidgets] = useState<AddonWidget[]>([]);

  const load = useCallback(async () => {
    // Agent 활성화 상태 (실패해도 대시보드 자체는 유지)
    let enabledMap: Record<string, boolean> = { gpu_monitoring: true, hardware: true };
    try {
      const configs = await listAgentConfigs();
      enabledMap = Object.fromEntries(configs.map((c) => [c.agent_key, !!c.is_enabled]));
      setEnabled(enabledMap);
    } catch {
      /* 활성화 조회 실패 → 기본값으로 전체 표시 */
    }

    try {
      const [g, n, a, h] = await Promise.all([
        enabledMap.gpu_monitoring !== false ? getGpuMetrics() : Promise.resolve([]),
        enabledMap.hardware !== false ? getHardwareMetrics() : Promise.resolve([]),
        getAlerts(),
        enabledMap.gpu_monitoring !== false ? getGpuHistory(30, 60) : Promise.resolve([]),
      ]);
      setGpus(g);
      setNodes(n);
      setAlerts(a);
      setHistory(h);
      setError(null);
      setUpdatedAt(new Date());
    } catch (e) {
      const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(detail ?? t("dashboard.loadError"));
    }

    // 활성 addon 위젯 — /status 미제공(404)·다운(503)·네트워크 오류는 조용히 스킵 (필수 예외처리)
    try {
      const addons = await listAddonAgents();
      // addon 자체 활성(is_active) + 에이전트 관리의 관제 Agent 토글(agent_config) 둘 다 만족해야 표시
      const active = addons.filter(
        (ad) =>
          ad.is_active &&
          !DEDICATED_SECTION_ADDONS.has(ad.agent_key) &&
          enabledMap[configKeyOf(ad.agent_key)] !== false,
      );
      const results = await Promise.all(
        active.map(async (ad): Promise<AddonWidget | null> => {
          try {
            const { data } = await client.get(`/addon/${ad.agent_key}/status`);
            return data && typeof data === "object"
              ? { key: ad.agent_key, name: ad.agent_name, data }
              : null;
          } catch {
            return null; // 위젯 미제공 addon — 에러 없이 제외
          }
        }),
      );
      setWidgets(results.filter((w): w is AddonWidget => w !== null));
    } catch {
      setWidgets([]);
    }
  }, [t]);

  useEffect(() => {
    load();
    const timer = setInterval(load, REFRESH_MS);
    return () => clearInterval(timer);
  }, [load]);

  const firing = alerts.filter((a) => a.state === "firing");
  const seriesOf = (g: GpuMetric) =>
    history.find((s) => s.hostname === g.hostname && s.gpu === g.gpu)?.points ?? [];

  return (
    <div className="p-6 space-y-6 max-w-5xl">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-gray-800 dark:text-gray-100">{t("dashboard.title")}</h1>
        <span className="text-xs text-gray-400 dark:text-gray-500">
          {updatedAt ? `${t("dashboard.updated")} ${updatedAt.toLocaleTimeString()}` : ""}
        </span>
      </div>

      {/* 오류 배너 */}
      {error && (
        <div className="rounded-xl border border-amber-300 dark:border-amber-700 bg-amber-50 dark:bg-amber-900/20 px-4 py-3 text-sm text-amber-800 dark:text-amber-300">
          {error}
        </div>
      )}

      {/* 활성 알람 배너 */}
      <section>
        <h2 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-3">
          {t("dashboard.alerts")} ({firing.length})
        </h2>
        {firing.length === 0 ? (
          <div className="rounded-xl border border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/20 px-4 py-3 text-sm text-green-700 dark:text-green-400">
            {t("dashboard.noAlerts")}
          </div>
        ) : (
          <div className="space-y-2">
            {firing.map((a) => (
              <div
                key={`${a.labels.alertname}-${a.labels.gpu ?? ""}-${a.labels.Hostname ?? ""}`}
                className="rounded-xl border border-red-300 dark:border-red-700 bg-red-50 dark:bg-red-900/20 px-4 py-3"
              >
                <p className="text-sm font-semibold text-red-700 dark:text-red-400">
                  [{a.labels.severity}] {a.labels.alertname}
                </p>
                <p className="text-xs text-red-600 dark:text-red-300">{a.annotations.summary}</p>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* GPU 카드 그리드 — gpu_monitoring Agent 활성 시에만 */}
      {enabled.gpu_monitoring !== false && (
      <section>
        <h2 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-3">
          GPU
        </h2>
        {gpus.length === 0 ? (
          <p className="text-sm text-gray-400 dark:text-gray-500">{t("dashboard.noData")}</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {gpus.map((g) => {
              const hasFault = (g.xid_errors ?? 0) > 0 || (g.ecc_dbe_total ?? 0) > 0;
              return (
                <div
                  key={`${g.hostname}-${g.gpu}`}
                  className={`rounded-xl border bg-white dark:bg-gray-800 p-4 space-y-3 ${
                    hasFault
                      ? "border-red-400 dark:border-red-600"
                      : "border-gray-200 dark:border-gray-700"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-semibold text-gray-800 dark:text-gray-100">
                      {g.hostname} · GPU {g.gpu}
                    </p>
                    <div className="flex items-center gap-1.5">
                      {hasFault && (
                        <span className="text-xs px-2 py-0.5 rounded-full bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-400 font-semibold">
                          XID {g.xid_errors ?? 0} · ECC {g.ecc_dbe_total ?? 0}
                        </span>
                      )}
                      <Sparkline points={seriesOf(g)} />
                    </div>
                  </div>

                  <div className="space-y-2 text-xs text-gray-500 dark:text-gray-400">
                    <div>
                      <div className="flex justify-between mb-0.5">
                        <span>Util</span>
                        <span>{(g.util_percent ?? 0).toFixed(0)}%</span>
                      </div>
                      <Bar pct={g.util_percent ?? 0} warn={101} crit={101} />
                    </div>
                    <div>
                      <div className="flex justify-between mb-0.5">
                        <span>VRAM</span>
                        <span>
                          {((g.vram_used_mib ?? 0) / 1024).toFixed(1)} / {((g.vram_total_mib ?? 0) / 1024).toFixed(0)} GiB
                          ({(g.vram_used_percent ?? 0).toFixed(0)}%)
                        </span>
                      </div>
                      <Bar pct={g.vram_used_percent ?? 0} warn={80} crit={90} />
                    </div>
                    <div className="flex justify-between">
                      <span>
                        {t("dashboard.temp")}{" "}
                        <b className={(g.temperature_c ?? 0) > 85 ? "text-red-500" : ""}>
                          {(g.temperature_c ?? 0).toFixed(0)}°C
                        </b>
                      </span>
                      <span>
                        {t("dashboard.power")} <b>{(g.power_watts ?? 0).toFixed(0)} W</b>
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>

      )}

      {/* 하드웨어 노드 테이블 — hardware Agent 활성 시에만 */}
      {enabled.hardware !== false && (
      <section>
        <h2 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-3">
          {t("dashboard.hardware")}
        </h2>
        {nodes.length === 0 ? (
          <p className="text-sm text-gray-400 dark:text-gray-500">{t("dashboard.noData")}</p>
        ) : (
          <div className="rounded-xl border border-gray-200 dark:border-gray-700 overflow-x-auto">
            <table className="w-full text-sm bg-white dark:bg-gray-800">
              <thead>
                <tr className="text-left text-xs text-gray-400 dark:text-gray-500 border-b border-gray-100 dark:border-gray-700">
                  <th className="px-4 py-2.5 font-medium">{t("dashboard.node")}</th>
                  <th className="px-4 py-2.5 font-medium">CPU</th>
                  <th className="px-4 py-2.5 font-medium">{t("dashboard.memory")}</th>
                  <th className="px-4 py-2.5 font-medium">RAID</th>
                  <th className="px-4 py-2.5 font-medium">PSU</th>
                  <th className="px-4 py-2.5 font-medium">{t("dashboard.inletTemp")}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                {nodes.map((n) => {
                  const memPct =
                    n.memory_total_bytes && n.memory_available_bytes != null
                      ? (1 - n.memory_available_bytes / n.memory_total_bytes) * 100
                      : null;
                  const raidBad = (n.raid_degraded ?? 0) > 0;
                  const psuBad = (n.psu_failed ?? 0) > 0;
                  return (
                    <tr key={n.hostname} className="text-gray-700 dark:text-gray-300">
                      <td className="px-4 py-2.5 font-medium">{n.hostname}</td>
                      <td className="px-4 py-2.5">{(n.cpu_usage_percent ?? 0).toFixed(0)}%</td>
                      <td className="px-4 py-2.5">{memPct == null ? "—" : `${memPct.toFixed(0)}%`}</td>
                      <td className={`px-4 py-2.5 font-semibold ${raidBad ? "text-red-500" : "text-green-600 dark:text-green-400"}`}>
                        {raidBad ? "DEGRADED" : "OK"}
                      </td>
                      <td className={`px-4 py-2.5 font-semibold ${psuBad ? "text-red-500" : "text-green-600 dark:text-green-400"}`}>
                        {psuBad ? `FAIL(${n.psu_failed})` : "OK"}
                      </td>
                      <td className="px-4 py-2.5">{(n.inlet_temp_celsius ?? 0).toFixed(1)}°C</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>
      )}

      {/* 활성 Addon 관제 위젯 — /status 제공 addon 만 (미제공은 자동 스킵) */}
      {widgets.length > 0 && (
        <section>
          <h2 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-3">
            {t("dashboard.agentWidgets")}
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {widgets.map((w) => (
              <div
                key={w.key}
                className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4"
              >
                <p className="text-sm font-semibold text-gray-800 dark:text-gray-100 mb-2">{w.name}</p>
                <dl className="space-y-1 text-xs text-gray-500 dark:text-gray-400">
                  {Object.entries(w.data)
                    .filter(([, v]) => typeof v === "number" || typeof v === "string" || typeof v === "boolean")
                    .slice(0, 6)
                    .map(([k, v]) => (
                      <div key={k} className="flex justify-between gap-2">
                        <dt className="truncate">{k}</dt>
                        <dd className="font-medium text-gray-700 dark:text-gray-200">{String(v)}</dd>
                      </div>
                    ))}
                </dl>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
