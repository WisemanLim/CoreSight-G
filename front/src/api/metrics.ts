import client from "./client";

export interface GpuMetric {
  hostname: string;
  gpu: string;
  util_percent?: number;
  vram_used_mib?: number;
  vram_total_mib?: number;
  vram_used_percent?: number;
  temperature_c?: number;
  power_watts?: number;
  xid_errors?: number;
  ecc_dbe_total?: number;
}

export interface HardwareNode {
  hostname: string;
  cpu_usage_percent?: number;
  memory_total_bytes?: number;
  memory_available_bytes?: number;
  raid_degraded?: number;
  psu_failed?: number;
  inlet_temp_celsius?: number;
}

export interface ActiveAlert {
  labels: Record<string, string>;
  annotations: Record<string, string>;
  state: string; // firing | pending
  activeAt: string;
  value: string;
}

export interface GpuUtilSeries {
  hostname: string;
  gpu: string;
  points: [number, number][]; // [unix_ts, util]
}

export async function getGpuMetrics(): Promise<GpuMetric[]> {
  const { data } = await client.get<{ gpus: GpuMetric[] }>("/metrics/gpu");
  return data.gpus;
}

export async function getHardwareMetrics(): Promise<HardwareNode[]> {
  const { data } = await client.get<{ nodes: HardwareNode[] }>("/metrics/hardware");
  return data.nodes;
}

export async function getAlerts(): Promise<ActiveAlert[]> {
  const { data } = await client.get<{ alerts: ActiveAlert[] }>("/metrics/alerts");
  return data.alerts;
}

export async function getGpuHistory(minutes = 30, step = 60): Promise<GpuUtilSeries[]> {
  const { data } = await client.get<{ series: GpuUtilSeries[] }>("/metrics/gpu/history", {
    params: { minutes, step },
  });
  return data.series;
}
