/**
 * Dynamic resolution of backend REST and WebSocket URLs.
 * Handles both local Vite proxy mode and decoupled cloud hosting (e.g. Vercel frontend -> Render backend).
 */

export function getApiBaseUrl(): string {
  const envUrl = import.meta.env.VITE_BACKEND_URL || import.meta.env.VITE_API_BASE_URL;
  if (envUrl) {
    const cleaned = envUrl.replace(/\/+$/, '');
    return cleaned.endsWith('/api') ? cleaned : `${cleaned}/api`;
  }
  return '/api';
}

export function getWsBaseUrl(): string {
  const envUrl = import.meta.env.VITE_BACKEND_URL || import.meta.env.VITE_API_BASE_URL;
  if (envUrl && envUrl.startsWith('http')) {
    const parsed = new URL(envUrl);
    const wsProto = parsed.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${wsProto}//${parsed.host}/ws`;
  }
  const localProto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${localProto}//${window.location.host}/ws`;
}
