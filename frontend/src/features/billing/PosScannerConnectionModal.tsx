import React, { useState, useEffect, useRef } from 'react';
import {
  Smartphone,
  X,
  CheckCircle2,
  RefreshCw,
  Copy,
  Check,
  Radio,
} from 'lucide-react';
import api from '../../api/client';
import toast from 'react-hot-toast';

interface PosScannerConnectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  activeSessionId: string | null;
  isMobileConnected: boolean;
  mobileDeviceInfo?: string | null;
  onSessionStarted: (sessionId: string) => void;
  onSessionRevoked: () => void;
}

export const PosScannerConnectionModal: React.FC<PosScannerConnectionModalProps> = ({
  isOpen,
  onClose,
  activeSessionId,
  isMobileConnected,
  mobileDeviceInfo,
  onSessionStarted,
  onSessionRevoked,
}) => {
  const [qrDataUrl, setQrDataUrl] = useState<string | null>(null);
  const [scannerUrl, setScannerUrl] = useState<string>('');
  const [pairingCode, setPairingCode] = useState<string>('');
  const [expiresIn, setExpiresIn] = useState<number>(300);
  const [isLoading, setIsLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [customHost, setCustomHost] = useState(window.location.host);

  const countdownTimerRef = useRef<any>(null);

  const generateNewPairing = async (hostOverride?: string) => {
    try {
      setIsLoading(true);
      const effectiveHost = hostOverride || customHost || window.location.host;
      // Mobile camera permissions strictly require HTTPS
      const protocol = 'https:';
      const baseUrl = `${protocol}//${effectiveHost}`;

      const res = await api.post('/pos/pairing/start/', {
        base_url: baseUrl,
      });

      const data = res.data;
      setQrDataUrl(data.qr_data_url);
      setScannerUrl(data.scanner_url);
      setPairingCode(data.pairing_code);
      setExpiresIn(data.expires_in_seconds || 300);

      if (data.detected_lan_ip && (!customHost || customHost.includes('localhost') || customHost.includes('127.0.0.1'))) {
        setCustomHost(`${data.detected_lan_ip}:5173`);
      }

      onSessionStarted(data.session_id);
    } catch {
      toast.error('Failed to initiate pairing session. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      if (!qrDataUrl || !activeSessionId) {
        generateNewPairing();
      }
    } else {
      clearInterval(countdownTimerRef.current);
    }
  }, [isOpen, qrDataUrl, activeSessionId]);

  // Countdown timer
  useEffect(() => {
    if (!isOpen || expiresIn <= 0) return;
    countdownTimerRef.current = setInterval(() => {
      setExpiresIn((prev) => Math.max(0, prev - 1));
    }, 1000);

    return () => clearInterval(countdownTimerRef.current);
  }, [isOpen, expiresIn]);

  const handleCopy = () => {
    if (!scannerUrl) return;
    navigator.clipboard.writeText(scannerUrl);
    setCopied(true);
    toast.success('Scanner link copied to clipboard!');
    setTimeout(() => setCopied(false), 2000);
  };

  const handleRevoke = async () => {
    if (!activeSessionId) return;
    try {
      await api.post('/pos/pairing/revoke/', {
        session_id: activeSessionId,
      });
      toast.success('Mobile scanner disconnected.');
      onSessionRevoked();
      setQrDataUrl(null);
      setScannerUrl('');
    } catch {
      toast.error('Failed to revoke session.');
    }
  };

  if (!isOpen) return null;

  const minutes = Math.floor(expiresIn / 60);
  const seconds = expiresIn % 60;
  const timeFormatted = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;

  return (
    <div
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 overflow-y-auto"
    >
      <div className="bg-white rounded-3xl shadow-2xl w-full max-w-lg overflow-hidden border border-slate-200 animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="flex justify-between items-center px-6 py-4 border-b border-slate-100 bg-gradient-to-r from-amber-500/10 via-amber-500/5 to-transparent">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-amber-600 text-white rounded-xl shadow-xs">
              <Smartphone className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-black text-slate-800 tracking-tight">
                  Connect Mobile QR Scanner
                </h3>
                {isMobileConnected && (
                  <span className="px-2 py-0.5 text-[10px] font-bold bg-emerald-100 text-emerald-800 rounded-full border border-emerald-300">
                    Live 12h
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-500">Wireless real-time tag scanner for phone camera</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 rounded-xl transition"
            title="Close this popup (keeps scanner live in background)"
          >
            <X className="w-4 h-4" />
            <span>Close Window</span>
          </button>
        </div>

        {/* Body Content */}
        <div className="p-6 space-y-6">
          {/* Live Status Indicator Box */}
          <div
            className={`p-4 rounded-2xl border transition flex items-center justify-between ${
              isMobileConnected
                ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
                : 'bg-amber-50/70 border-amber-200 text-amber-900'
            }`}
          >
            <div className="flex items-center gap-3">
              <div
                className={`w-3 h-3 rounded-full ${
                  isMobileConnected ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500 animate-ping'
                }`}
              />
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider">
                  {isMobileConnected ? 'Mobile Phone Connected' : 'Waiting for phone to scan...'}
                </h4>
                <p className="text-[11px] opacity-80 mt-0.5">
                  {isMobileConnected
                    ? mobileDeviceInfo || 'Phone camera linked. Scanned items add directly to cart.'
                    : 'Open your phone camera and scan the pairing code below.'}
                </p>
              </div>
            </div>

            {isMobileConnected ? (
              <span className="flex items-center gap-1 px-2.5 py-1 bg-emerald-600 text-white font-bold text-[10px] rounded-lg shadow-xs">
                <Check className="w-3.5 h-3.5" /> ACTIVE
              </span>
            ) : (
              <span className="px-2.5 py-1 bg-amber-200/70 text-amber-900 font-mono text-xs font-bold rounded-lg">
                {timeFormatted}
              </span>
            )}
          </div>

          {/* Pairing QR Display */}
          <div className="flex flex-col items-center justify-center p-6 bg-slate-50 rounded-2xl border border-slate-200/80 space-y-4">
            {isLoading ? (
              <div className="w-48 h-48 flex flex-col items-center justify-center text-slate-400 space-y-2">
                <div className="w-8 h-8 border-3 border-amber-600 border-t-transparent rounded-full animate-spin" />
                <span className="text-xs">Generating secure code...</span>
              </div>
            ) : qrDataUrl ? (
              <div className="relative group">
                <img
                  src={qrDataUrl}
                  alt="Pairing QR Code"
                  className="w-52 h-52 object-contain bg-white p-3 rounded-2xl shadow-sm border border-slate-200"
                />
                {isMobileConnected && (
                  <div className="absolute inset-0 bg-white/90 backdrop-blur-xs rounded-2xl flex flex-col items-center justify-center p-4 text-center">
                    <CheckCircle2 className="w-12 h-12 text-emerald-500 mb-2" />
                    <h5 className="font-bold text-sm text-slate-800">Phone Paired!</h5>
                    <p className="text-xs text-slate-500 mt-1">
                      Ready to scan jewellery tags with phone camera.
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <button
                onClick={() => generateNewPairing()}
                className="flex items-center gap-2 px-4 py-2 bg-amber-600 text-white text-xs font-bold rounded-xl"
              >
                <RefreshCw className="w-4 h-4" /> Generate New Pairing QR
              </button>
            )}

            {/* Direct Link Copy & Pairing Code */}
            {scannerUrl && !isMobileConnected && (
              <div className="w-full space-y-2 text-center">
                <div className="flex items-center justify-center gap-2 text-xs font-mono bg-white px-3 py-1.5 rounded-xl border border-slate-200">
                  <span className="text-slate-400 text-[11px] font-sans">Single-Use Code:</span>
                  <span className="font-bold text-slate-800">{pairingCode.slice(0, 8)}...</span>
                </div>
                <div className="flex gap-2">
                  <input
                    type="text"
                    readOnly
                    value={scannerUrl}
                    className="flex-1 px-3 py-1.5 text-[11px] font-mono bg-white border border-slate-200 rounded-xl text-slate-500 select-all"
                  />
                  <button
                    onClick={handleCopy}
                    className="flex items-center gap-1 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-xl border border-slate-300 transition"
                  >
                    {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copied ? 'Copied' : 'Copy'}</span>
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Network Host Settings Box */}
          <div className="p-3.5 bg-slate-50 rounded-2xl border border-slate-200 text-xs space-y-2.5">
            <div className="flex items-center justify-between text-slate-700 font-bold">
              <span className="flex items-center gap-1.5">
                <Radio className="w-3.5 h-3.5 text-amber-600" />
                <span>Wi-Fi Network Pairing Address</span>
              </span>
              <span className="text-[10px] text-amber-800 bg-amber-100 font-mono px-2 py-0.5 rounded-full">
                Must be Laptop Wi-Fi IP
              </span>
            </div>

            <div className="flex gap-2">
              <input
                type="text"
                placeholder="e.g. 192.168.0.102:5173"
                value={customHost}
                onChange={(e) => setCustomHost(e.target.value)}
                className="flex-1 px-3 py-1.5 text-xs bg-white border border-slate-300 rounded-xl font-mono focus:ring-2 focus:ring-amber-500/20 focus:outline-hidden"
              />
              <button
                type="button"
                onClick={() => generateNewPairing(customHost)}
                className="px-3.5 py-1.5 bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs rounded-xl shadow-xs transition"
              >
                Apply IP
              </button>
            </div>

            <div className="p-2.5 bg-amber-500/10 border border-amber-500/20 rounded-xl text-[11px] text-amber-900 space-y-1">
              <p className="font-semibold">🔒 First Time HTTPS Setup on Phone:</p>
              <ul className="list-disc pl-4 space-y-0.5 text-[10px] text-slate-600">
                <li>
                  <b>Camera requires HTTPS:</b> The QR code opens over <code>https://</code> so your mobile browser unlocks rear camera hardware.
                </li>
                <li>
                  <b>First time warning:</b> When your phone shows <i>"Connection is not private"</i>, tap <b>Advanced → Proceed to {customHost} (unsafe)</b> (on Chrome) or <b>Show Details → visit this website</b> (on Safari).
                </li>
                <li>
                  Once accepted, your rear camera activates automatically!
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-4 border-t border-slate-100 bg-slate-50 flex flex-col gap-3">
          <div className="flex justify-between items-center w-full">
            {activeSessionId && (
              <button
                onClick={handleRevoke}
                className="text-xs font-semibold text-rose-600 hover:text-rose-700 hover:underline"
              >
                Disconnect Phone
              </button>
            )}

            <div className="flex items-center gap-2.5 ml-auto">
              <button
                onClick={() => generateNewPairing()}
                disabled={isLoading}
                className="flex items-center gap-1.5 px-3.5 py-2 border border-slate-300 hover:bg-slate-100 text-slate-700 text-xs font-bold rounded-xl transition"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
                <span>Regenerate</span>
              </button>

              {isMobileConnected ? (
                <button
                  onClick={onClose}
                  className="flex items-center gap-2 px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow-md transition active:scale-95"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Phone Connected — Close Window</span>
                </button>
              ) : (
                <button
                  onClick={onClose}
                  className="flex items-center gap-1.5 px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold rounded-xl shadow-sm transition active:scale-95"
                >
                  <X className="w-3.5 h-3.5" />
                  <span>Close Window</span>
                </button>
              )}
            </div>
          </div>

          <div className="text-[11px] text-slate-500 bg-amber-500/10 border border-amber-500/20 px-3 py-1.5 rounded-lg flex items-center justify-between">
            <span>
              💡 <b>Live 12-Hour Pairing:</b> The phone stays linked in the background for 12 hours or until you log out. You can safely close this window anytime.
            </span>
            <button
              onClick={onClose}
              className="text-amber-900 font-bold hover:underline shrink-0 ml-2"
            >
              Dismiss
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
