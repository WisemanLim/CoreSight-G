import axios from "axios";
import client from "./client";

export interface AddonAgent {
  id: number;
  agent_key: string;
  agent_name: string;
  api_prefix: string;
  has_app: boolean;
  has_front: boolean;
  is_builtin: boolean;
  is_active: boolean;
  uploaded_by: string | null;
  uploaded_at: string;
}

export async function listAddonAgents(): Promise<AddonAgent[]> {
  const { data } = await client.get<{ addons: AddonAgent[] }>("/addon-agents/");
  return data.addons ?? [];
}

export async function uploadAddonAgent(
  file: File,
  force = false
): Promise<{ agent_key: string; agent_name: string; message: string }> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await client.post(`/addon-agents/upload?force=${force}`, form);
  return data;
}

export async function toggleAddonAgent(
  key: string
): Promise<{ agent_key: string; is_active: boolean }> {
  const { data } = await client.patch(`/addon-agents/${key}/toggle`);
  return data;
}

export async function deleteAddonAgent(key: string): Promise<void> {
  await client.delete(`/addon-agents/${key}`);
}

export interface AddonTemplate {
  name: string;
  filename: string;
}

export async function listTemplates(): Promise<AddonTemplate[]> {
  const { data } = await client.get<{ templates: AddonTemplate[] }>("/addon-agents/templates/list");
  return data.templates ?? [];
}

export async function getGuide(): Promise<string> {
  const { data } = await client.get<{ content: string }>("/addon-agents/guide");
  return data.content ?? "";
}

export async function patchAddonAgent(
  key: string,
  body: { agent_name?: string }
): Promise<void> {
  await client.patch(`/addon-agents/${key}`, body);
}

export interface ScaffoldRequest {
  agent_name: string;
  agent_type: string;
  description?: string;
  domain?: string;
}

export async function scaffoldAgent(req: ScaffoldRequest): Promise<Blob> {
  const token = localStorage.getItem("token");
  const res = await fetch("/api/addon-agents/scaffold", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as { detail?: string }).detail ?? "Scaffold failed");
  }
  return res.blob();
}

export interface CatalogEntry {
  agent_key: string;
  agent_name: string;
  api_prefix: string;
  agent_type: string;
  is_active: boolean;
}

export async function getCatalog(agentType?: string): Promise<Record<string, CatalogEntry[]>> {
  const url = agentType ? `/addon-agents/catalog?agent_type=${agentType}` : "/addon-agents/catalog";
  const { data } = await client.get<{ catalog: Record<string, CatalogEntry[]> }>(url);
  return data.catalog ?? {};
}

export interface McpTool {
  name: string;
  description: string;
}

export interface McpClientConfig {
  description: string;
  config: object;
}

export interface McpGuide {
  agent_key: string;
  mcp_url: string;
  proxy_port: number | null;
  server_host?: string;
  is_alive: boolean;
  transport: string;
  protocol: string;
  active_tools_count: number;
  active_tools: McpTool[];
  client_configs: Record<string, McpClientConfig>;
}

export async function getMcpAgentGuide(agentKey: string): Promise<McpGuide> {
  const { data } = await axios.get<McpGuide>(`/mcp/${agentKey}/guide`);
  return data;
}
