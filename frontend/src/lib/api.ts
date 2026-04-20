import type { DashboardSnapshot } from '../types';

const DEFAULT_API_BASE_URL = 'http://127.0.0.1:8000';

function getApiBaseUrl() {
  return import.meta.env.VITE_API_BASE_URL ?? DEFAULT_API_BASE_URL;
}

async function requestJson(path: string, options?: RequestInit) {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options?.headers ?? {}),
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`Request to ${path} failed with status ${response.status}`);
  }

  return response.json() as Promise<DashboardSnapshot>;
}

export async function fetchDashboardState() {
  return requestJson('/api/state');
}

export async function runBackendPipeline() {
  const response = await fetch(`${getApiBaseUrl()}/api/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) {
    throw new Error(`Pipeline run failed with status ${response.status}`);
  }

  const payload = (await response.json()) as { state?: DashboardSnapshot };
  if (!payload.state) {
    throw new Error('Pipeline run returned no dashboard state');
  }

  return payload.state;
}
