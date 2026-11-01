import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { MobileQRScanner } from '../camera/MobileQRScanner';
import {
  Smartphone,
  CheckCircle2,
  AlertCircle,
  Wifi,
  WifiOff,
  ShoppingBag,
  RefreshCw,
} from 'lucide-react';
import axios from 'axios';
import { getApiBaseUrl, getWsBaseUrl } from '../../utils/backendUrl';

interface ScannedHistoryItem {
  id: string;
  name: string;
  sku: string;
  purity: string;
  netWeight: string;
  timestamp: number;
}

export const MobileScannerPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('session_id') || '';
  const pairingCode = searchParams.get('code') || '';
  const tenantParam = searchParams.get('tenant') || '';

  const [tenantSchema, setTenantSchema] = useState<string>(() => {
    if (!sessionId) return tenantParam;
    return sessionStorage.getItem(`pos_tenant_${sessionId}`) || tenantParam || '';
  });

  const [mobileToken, setMobileToken] = useState<string | null>(() => {
    if (!sessionId) return null;
    try {
      const cached = sessionStorage.getItem(`pos_mobile_${sessionId}`);
      if (cached) {
        const parsed = JSON.parse(cached);
        return parsed.token || null;
      }
    } catch {
      // ignore
    }
    return null;
  });

  const [storeInfo, setStoreInfo] = useState<{ userName: string; branchName: string } | null>(() => {
    if (!sessionId) return null;
    try {
      const cached = sessionStorage.getItem(`pos_mobile_${sessionId}`);
      if (cached) {
        const parsed = JSON.parse(cached);
        return parsed.storeInfo || null;
      }
    } catch {
      // ignore
    }
    return null;
  });

  const [pairingError, setPairingError] = useState<string | null>(null);
  const [isRedeeming, setIsRedeeming] = useState(false);

  const [wsStatus, setWsStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected');
  const [laptopConnected, setLaptopConnected] = useState<boolean>(true);
  const [scanHistory, setScanHistory] = useState<ScannedHistoryItem[]>([]);
  const [latestScanResult, setLatestScanResult] = useState<{
    status: 'success' | 'error';
    message: string;
  } | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const pingIntervalRef = useRef<any>(null);
  const reconnectTimeoutRef = useRef<any>(null);
  const hasRequestedRef = useRef<boolean>(false);

  // 1. Redeem single-use pairing code with backend
  useEffect(() => {
    if (mobileToken) {
      // Already authenticated via cached session
      return;
    }

    if (!sessionId || !pairingCode) {
      setPairingError('Missing pairing session ID or pairing code. Please scan the QR code on the laptop POS.');
      return;
    }

    if (hasRequestedRef.current) {
      // Guard against React StrictMode duplicate effect invocation
      return;
    }
    hasRequestedRef.current = true;

    const redeemCode = async () => {
      try {
        setIsRedeeming(true);
        setPairingError(null);

        const res = await axios.post(`${getApiBaseUrl()}/pos/pairing/redeem/`, {
          session_id: sessionId,
          pairing_code: pairingCode,
          device_info: `${navigator.userAgent.slice(0, 80)}`,
          tenant_schema: tenantSchema || tenantParam || undefined,
        });

        const { mobile_token, user_name, branch_name, tenant_schema: serverTenant } = res.data;
        const newStoreInfo = { userName: user_name, branchName: branch_name };
        const resolvedTenant = serverTenant || tenantSchema || tenantParam || '';

        setMobileToken(mobile_token);
        setStoreInfo(newStoreInfo);
        if (resolvedTenant) {
          setTenantSchema(resolvedTenant);
        }

        try {
          sessionStorage.setItem(
            `pos_mobile_${sessionId}`,
            JSON.stringify({ token: mobile_token, storeInfo: newStoreInfo })
          );
          if (resolvedTenant) {
            sessionStorage.setItem(`pos_tenant_${sessionId}`, resolvedTenant);
          }
        } catch {
          // ignore
        }

        // Clean URL to prevent pairing code replay on reload
        const newUrl = `${window.location.pathname}?session_id=${sessionId}${
          resolvedTenant ? `&tenant=${encodeURIComponent(resolvedTenant)}` : ''
        }`;
        window.history.replaceState({}, document.title, newUrl);
      } catch (err: any) {
        const msg = err.response?.data?.error || 'Failed to pair device. Code may be invalid or expired.';
        setPairingError(msg);
      } finally {
        setIsRedeeming(false);
      }
    };

    redeemCode();
  }, [sessionId, pairingCode, mobileToken]);

  // 2. Manage WebSocket connection
  const connectWebSocket = useCallback(() => {
    if (!sessionId || !mobileToken) return;

    if (wsRef.current) {
      try {
        wsRef.current.close();
      } catch {
        // ignore
      }
      wsRef.current = null;
    }

    const wsBase = getWsBaseUrl();
    const wsUrl = `${wsBase}/mobile/?session_id=${encodeURIComponent(
      sessionId
    )}&token=${encodeURIComponent(mobileToken)}&tenant=${encodeURIComponent(
      tenantSchema || ''
    )}&device_info=${encodeURIComponent(navigator.userAgent.slice(0, 60))}`;

    setWsStatus('connecting');

    try {
      const socket = new WebSocket(wsUrl);
      wsRef.current = socket;

      socket.onopen = () => {
        setWsStatus('connected');
        // Heartbeat ping every 20 seconds
        clearInterval(pingIntervalRef.current);
        pingIntervalRef.current = setInterval(() => {
          if (socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ type: 'ping' }));
          }
        }, 20000);
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'connection_established') {
            setLaptopConnected(Boolean(data.laptop_connected));
          } else if (data.type === 'laptop_status') {
            setLaptopConnected(data.status === 'connected');
          } else if (data.type === 'scan_ack') {
            if (data.status === 'success') {
              setLatestScanResult({
                status: 'success',
                message: `Added: ${data.item_name} (${data.sku}) • ${data.net_weight}g pure`,
              });
              setScanHistory((prev) => [
                {
                  id: data.event_id || String(Date.now()),
                  name: data.item_name,
                  sku: data.sku,
                  purity: data.purity,
                  netWeight: data.net_weight,
                  timestamp: Date.now(),
                },
                ...prev.slice(0, 9),
              ]);
            } else if (data.status === 'duplicate') {
              setLatestScanResult({
                status: 'success',
                message: 'Item already added to cart.',
              });
            }
          } else if (data.type === 'scan_error') {
            setLatestScanResult({
              status: 'error',
              message: data.error || 'Failed to add item to POS cart.',
            });
          } else if (data.type === 'session_revoked') {
            setPairingError('POS Operator disconnected this mobile scanner session.');
            socket.close();
          }
        } catch (e) {
          console.warn('Error parsing incoming WebSocket message:', e);
        }
      };

      socket.onclose = (e) => {
        setWsStatus('disconnected');
        clearInterval(pingIntervalRef.current);
        // Reconnect after 3s if token is still valid
        if (e.code !== 4403 && e.code !== 4404 && e.code !== 4401 && !pairingError) {
          clearTimeout(reconnectTimeoutRef.current);
          reconnectTimeoutRef.current = setTimeout(() => {
            connectWebSocket();
          }, 3000);
        }
      };

      socket.onerror = () => {
        setWsStatus('disconnected');
      };
    } catch (err) {
      console.error('WebSocket connection error:', err);
      setWsStatus('disconnected');
    }
  }, [mobileToken, pairingError, sessionId]);

  useEffect(() => {
    if (mobileToken) {
      connectWebSocket();
    }
    return () => {
      clearInterval(pingIntervalRef.current);
      clearTimeout(reconnectTimeoutRef.current);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connectWebSocket, mobileToken]);

  // 3. Handle Scanned QR code
  const handleQRScanned = async (qrData: string) => {
    const cleanPayload = (qrData || '').trim();
    if (!cleanPayload) return;

    const eventId =
      typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function'
        ? crypto.randomUUID()
        : `evt_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
    const timestamp = Date.now();

    // Prefer active WebSocket
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: 'scan_event',
          event_id: eventId,
          qr_payload: cleanPayload,
          timestamp,
        })
      );
      setLatestScanResult({
        status: 'success',
        message: 'Tag scanned! Sending to laptop POS...',
      });
    } else if (mobileToken) {
      // Robust HTTP fallback
      try {
        const res = await axios.post(
          `${getApiBaseUrl()}/pos/pairing/scan/`,
          {
            event_id: eventId,
            qr_payload: cleanPayload,
            timestamp,
          },
          {
            headers: {
              Authorization: `Bearer ${mobileToken}`,
              'X-Tenant': tenantSchema || 'demo',
            },
          }
        );
        const prod = res.data.product;
        if (prod) {
          setLatestScanResult({
            status: 'success',
            message: `Added: ${prod.name} (${prod.sku})`,
          });
          setScanHistory((prev) => [
            {
              id: eventId,
              name: prod.name,
              sku: prod.sku,
              purity: prod.purity_name,
              netWeight: prod.net_weight,
              timestamp,
            },
            ...prev.slice(0, 9),
          ]);
        }
      } catch (err: any) {
        const msg = err.response?.data?.error || 'Item not found or inactive';
        setLatestScanResult({ status: 'error', message: msg });
      }
    } else {
      setLatestScanResult({
        status: 'error',
        message: 'Device not paired with POS. Please scan pairing QR again.',
      });
    }
  };

  // Error screen if pairing failed
  if (pairingError) {
    return (
      <div className="min-h-screen bg-slate-950 text-white flex flex-col items-center justify-center p-6 text-center">
        <div className="p-4 bg-red-500/20 text-red-400 rounded-3xl border border-red-500/30 mb-4">
          <AlertCircle className="w-12 h-12" />
        </div>
        <h2 className="text-xl font-bold mb-2">Pairing Session Inactive</h2>
        <p className="text-slate-400 text-xs max-w-sm mb-6">{pairingError}</p>
        <button
          onClick={() => window.location.reload()}
          className="flex items-center gap-2 px-6 py-3 bg-amber-600 hover:bg-amber-500 text-white font-bold text-sm rounded-xl shadow-lg transition"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Reload / Try Again</span>
        </button>
      </div>
    );
  }

  // Loading redemption
  if (isRedeeming) {
    return (
      <div className="min-h-screen bg-slate-950 text-white flex flex-col items-center justify-center p-6 text-center space-y-4">
        <div className="w-12 h-12 border-4 border-amber-500 border-t-transparent rounded-full animate-spin" />
        <h3 className="font-bold text-base text-slate-200">Pairing with Laptop POS...</h3>
        <p className="text-slate-400 text-xs">Verifying single-use pairing code with backend</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Mobile Top Header */}
      <header className="px-4 py-3 bg-slate-900/90 backdrop-blur-md border-b border-slate-800 flex items-center justify-between sticky top-0 z-20">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-gradient-to-tr from-amber-600 to-amber-500 text-white rounded-xl shadow-sm">
            <Smartphone className="w-5 h-5" />
          </div>
          <div>
            <h1 className="font-black text-sm text-amber-400 tracking-tight flex items-center gap-1.5">
              <span>Swarna Khata</span>
              <span className="text-[10px] px-1.5 py-0.2 bg-amber-500/20 text-amber-300 rounded-md font-mono">
                Mobile POS
              </span>
            </h1>
            <p className="text-[11px] text-slate-400">
              {storeInfo ? `${storeInfo.branchName} (${storeInfo.userName})` : 'Wireless Tag Scanner'}
            </p>
          </div>
        </div>

        {/* Live Status Indicator */}
        <div className="flex items-center gap-1.5">
          {wsStatus === 'connected' ? (
            <div className="flex items-center gap-1.5 px-2.5 py-1 bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 rounded-full text-[11px] font-semibold">
              <Wifi className="w-3.5 h-3.5 animate-pulse" />
              <span>Live POS Sync</span>
            </div>
          ) : (
            <div className="flex items-center gap-1.5 px-2.5 py-1 bg-amber-500/15 border border-amber-500/30 text-amber-400 rounded-full text-[11px] font-semibold">
              <WifiOff className="w-3.5 h-3.5" />
              <span>{wsStatus === 'connecting' ? 'Connecting...' : 'Offline'}</span>
            </div>
          )}
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 p-4 max-w-md mx-auto w-full space-y-4">
        {/* Latest Scan Result Banner */}
        {latestScanResult && (
          <div
            className={`p-3.5 rounded-2xl border flex items-center gap-3 transition shadow-lg ${
              latestScanResult.status === 'success'
                ? 'bg-emerald-950/80 border-emerald-500/40 text-emerald-200'
                : 'bg-red-950/80 border-red-500/40 text-red-200'
            }`}
          >
            {latestScanResult.status === 'success' ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
            ) : (
              <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
            )}
            <p className="text-xs font-medium leading-tight flex-1">{latestScanResult.message}</p>
          </div>
        )}

        {/* QR Camera Scanner View */}
        <MobileQRScanner onScan={handleQRScanned} />

        {/* Laptop Pairing Status Card */}
        <div className="bg-slate-900/80 p-3.5 rounded-2xl border border-slate-800 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2.5">
            <ShoppingBag className="w-4 h-4 text-amber-500" />
            <span className="text-slate-300">
              {laptopConnected ? 'Laptop POS Cart Ready' : 'Laptop POS Waiting...'}
            </span>
          </div>
          <span
            className={`px-2 py-0.5 rounded-md font-mono text-[10px] font-bold ${
              laptopConnected
                ? 'bg-emerald-500/20 text-emerald-400'
                : 'bg-amber-500/20 text-amber-400'
            }`}
          >
            {laptopConnected ? 'LINKED' : 'PAUSED'}
          </span>
        </div>

        {/* Recent Scans In This Session */}
        {scanHistory.length > 0 && (
          <div className="space-y-2 pt-2">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center justify-between">
              <span>Scanned Items ({scanHistory.length})</span>
              <span className="text-[10px] text-amber-400 font-normal">Pushed to POS</span>
            </h3>
            <div className="space-y-1.5 max-h-48 overflow-y-auto divide-y divide-slate-800/60 bg-slate-900/60 rounded-2xl border border-slate-800 p-2">
              {scanHistory.map((item) => (
                <div key={item.id} className="pt-1.5 first:pt-0 flex items-center justify-between text-xs">
                  <div>
                    <h4 className="font-semibold text-slate-200 line-clamp-1">{item.name}</h4>
                    <span className="text-[11px] text-slate-500 font-mono">
                      {item.sku} • {item.purity}
                    </span>
                  </div>
                  <div className="text-right">
                    <span className="font-mono text-emerald-400 font-bold">{item.netWeight}g</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
};
