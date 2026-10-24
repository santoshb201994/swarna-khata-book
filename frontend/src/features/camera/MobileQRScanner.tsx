/**
 * MobileQRScanner – camera-only, QR-code-only scanner for mobile browsers.
 *
 * Architecture:
 *  • Gets camera stream via getUserMedia with rear-facing preference.
 *  • Attaches stream to a <video> element that is always mounted in the DOM.
 *  • Polls frames with requestAnimationFrame rather than setInterval so the
 *    loop is always in sync with the browser's rendering pipeline.
 *  • Draws each frame onto a hidden <canvas> and calls ZXing's
 *    BrowserQRCodeReader.decodeFromCanvas() synchronously.
 *  • A second centre-crop canvas handles small / distant tags.
 */
import React, {
  useEffect,
  useRef,
  useState,
  useCallback,
} from 'react';
import { BrowserQRCodeReader } from '@zxing/browser';
import { BarcodeFormat, DecodeHintType } from '@zxing/library';
import {
  Camera,
  CameraOff,
  AlertCircle,
  RefreshCw,
  CheckCircle2,
} from 'lucide-react';

/* ─── helpers ─────────────────────────────────────────────────────────────── */

/** Lightweight beep so the user knows a scan fired. */
function beep() {
  try {
    const Ctx = (window as any).AudioContext ?? (window as any).webkitAudioContext;
    if (!Ctx) return;
    const ac  = new Ctx() as AudioContext;
    const osc = ac.createOscillator();
    const g   = ac.createGain();
    osc.type = 'sine';
    osc.frequency.value = 880;
    g.gain.setValueAtTime(0.25, ac.currentTime);
    g.gain.exponentialRampToValueAtTime(0.001, ac.currentTime + 0.12);
    osc.connect(g);
    g.connect(ac.destination);
    osc.start();
    osc.stop(ac.currentTime + 0.12);
  } catch { /* ignore */ }
}

/** Build a ZXing reader configured for QR-only with maximum decode effort. */
function makeReader() {
  const hints = new Map<DecodeHintType, any>();
  hints.set(DecodeHintType.POSSIBLE_FORMATS, [BarcodeFormat.QR_CODE]);
  hints.set(DecodeHintType.TRY_HARDER, true);
  hints.set(DecodeHintType.CHARACTER_SET, 'UTF-8');
  return new BrowserQRCodeReader(hints);
}

/** Returns true once `video` has actual pixel data. */
function isVideoReady(video: HTMLVideoElement): boolean {
  return (
    video.readyState >= HTMLMediaElement.HAVE_CURRENT_DATA &&
    video.videoWidth > 0 &&
    video.videoHeight > 0 &&
    !video.paused &&
    !video.ended
  );
}

/* ─── component ────────────────────────────────────────────────────────────── */

interface MobileQRScannerProps {
  onScan: (text: string) => void;
  cooldownMs?: number;
}

type ScannerState = 'idle' | 'requesting' | 'active' | 'error';

export const MobileQRScanner: React.FC<MobileQRScannerProps> = ({
  onScan,
  cooldownMs = 3000,
}) => {
  /* DOM */
  const videoRef       = useRef<HTMLVideoElement>(null!);
  const canvasRef      = useRef<HTMLCanvasElement>(null!);
  const cropCanvasRef  = useRef<HTMLCanvasElement>(null!);

  /* scanning state */
  const readerRef      = useRef<BrowserQRCodeReader | null>(null);
  const streamRef      = useRef<MediaStream | null>(null);
  const rafRef         = useRef<number | null>(null);
  const mountedRef     = useRef(true);
  const busyRef        = useRef(false);           // guard against concurrent decode calls
  const lastTextRef    = useRef<string | null>(null);
  const lastTimeRef    = useRef(0);
  const onScanRef      = useRef(onScan);
  onScanRef.current    = onScan;

  const [state, setState]       = useState<ScannerState>('idle');
  const [errorMsg, setErrorMsg] = useState('');
  const [lastScan, setLastScan] = useState<string | null>(null);
  const [scanCount, setScanCount] = useState(0);   // key bump for animation re-trigger
  const lastDecodeTimeRef       = useRef(0);

  /* ── cleanup on unmount ─────────────────────────────────────────────────── */
  useEffect(() => {
    mountedRef.current = true;
    if (!readerRef.current) {
      readerRef.current = makeReader();
    }
    return () => {
      mountedRef.current = false;
      stopStream();
      if (rafRef.current != null) cancelAnimationFrame(rafRef.current);
    };
  }, []);

  /* ── stream helpers ─────────────────────────────────────────────────────── */
  function stopStream() {
    if (rafRef.current != null) {
      cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(t => { try { t.stop(); } catch { /**/ } });
      streamRef.current = null;
    }
    // detach from video but DON'T null the element itself
    const v = videoRef.current;
    if (v) {
      v.pause();
      v.srcObject = null;
    }
  }

  /* ── RAF decode loop ────────────────────────────────────────────────────── */
  function startDecodeLoop() {
    if (!readerRef.current) return;

    const canvas     = canvasRef.current;
    const cropCanvas = cropCanvasRef.current;
    if (!canvas || !cropCanvas) return;

    const ctx     = canvas.getContext('2d', { willReadFrequently: true });
    const cropCtx = cropCanvas.getContext('2d', { willReadFrequently: true });
    if (!ctx) return;

    const loop = () => {
      if (!mountedRef.current) return;

      const video = videoRef.current;

      /* schedule next frame first so the loop never stalls */
      rafRef.current = requestAnimationFrame(loop);

      if (!video || !isVideoReady(video) || busyRef.current) return;
      if (!streamRef.current) return;

      // Throttle heavy ZXing decode to ~11 FPS (90ms)
      // Keeps UI thread completely free so video streams at 60 FPS without stutter or lag
      const now = performance.now();
      if (now - lastDecodeTimeRef.current < 90) return;
      lastDecodeTimeRef.current = now;

      busyRef.current = true;

      try {
        const reader = readerRef.current!;
        const vw = video.videoWidth;
        const vh = video.videoHeight;

        /* ── Pass 1: full-frame (downscaled to max 1280px) ── */
        const MAX = 1280;
        let fw = vw, fh = vh;
        if (fw > MAX || fh > MAX) {
          if (fw > fh) { fh = Math.round(fh * MAX / fw); fw = MAX; }
          else         { fw = Math.round(fw * MAX / fh); fh = MAX; }
        }
        if (canvas.width !== fw || canvas.height !== fh) {
          canvas.width  = fw;
          canvas.height = fh;
        }
        ctx.drawImage(video, 0, 0, fw, fh);

        let result: any = null;
        try { result = reader.decodeFromCanvas(canvas); } catch { /* no QR */ }

        /* ── Pass 2: centre-crop at native resolution (covers small tags) ── */
        if (!result && cropCtx) {
          const size = Math.floor(Math.min(vw, vh) * 0.6);
          const ox   = Math.floor((vw - size) / 2);
          const oy   = Math.floor((vh - size) / 2);
          if (cropCanvas.width !== size || cropCanvas.height !== size) {
            cropCanvas.width  = size;
            cropCanvas.height = size;
          }
          cropCtx.drawImage(video, ox, oy, size, size, 0, 0, size, size);
          try { result = reader.decodeFromCanvas(cropCanvas); } catch { /* no QR */ }
        }

        if (result) {
          const text = (result.getText() ?? '').trim();
          if (text) {
            const now  = Date.now();
            const same = text === lastTextRef.current;
            const cool = now - lastTimeRef.current < cooldownMs;

            if (!same || !cool) {
              lastTextRef.current = text;
              lastTimeRef.current = now;
              setLastScan(text);
              setScanCount(c => c + 1);
              beep();
              try { navigator.vibrate?.([50, 30, 50]); } catch { /**/ }
              onScanRef.current(text);
            }
          }
        }
      } catch { /* ignore single-frame decode errors */ } finally {
        busyRef.current = false;
      }
    };

    rafRef.current = requestAnimationFrame(loop);
  }

  /* ── start camera ───────────────────────────────────────────────────────── */
  const startCamera = useCallback(async () => {
    setErrorMsg('');
    setState('requesting');
    busyRef.current = false;

    /* Stop any pre-existing stream first */
    if (rafRef.current != null) { cancelAnimationFrame(rafRef.current); rafRef.current = null; }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(t => { try { t.stop(); } catch { /**/ } });
      streamRef.current = null;
    }

    if (!navigator.mediaDevices?.getUserMedia) {
      setErrorMsg('Camera API unavailable. Access the page via https:// on the same network.');
      setState('error');
      return;
    }

    try {
      /* Single constraint request — let the browser pick the best resolution.
         Avoid width/height ideals that cause a failed first attempt + retry delay. */
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: false,
        video: { facingMode: { ideal: 'environment' } },
      });

      if (!mountedRef.current) { stream.getTracks().forEach(t => t.stop()); return; }

      streamRef.current = stream;

      /* Initialise (or reuse) ZXing reader */
      if (!readerRef.current) readerRef.current = makeReader();

      /* Attach stream — let autoplay attribute handle play(), no await needed */
      const video = videoRef.current;
      video.srcObject = stream;

      /* Non-blocking play attempt — the decode loop checks isVideoReady() each frame,
         so we don't need to wait here. Camera appears immediately. */
      video.play().catch(() => { /* autoplay policy handled in loop */ });

      /* Show the viewfinder right away, decode loop will start producing results
         as soon as the first valid frame is available */
      setState('active');
      startDecodeLoop();

    } catch (err: any) {
      let msg = 'Could not access camera. Please check permissions.';
      if (err?.name === 'NotAllowedError' || err?.name === 'PermissionDeniedError') {
        msg = 'Camera permission denied. Tap the camera icon in your browser address bar and allow access.';
      } else if (err?.name === 'NotFoundError') {
        msg = 'No camera found on this device.';
      } else if (err?.name === 'NotReadableError') {
        msg = 'Camera is in use by another app. Close it and retry.';
      } else if (window.location.protocol !== 'https:' && window.location.hostname !== 'localhost') {
        msg = 'Camera requires HTTPS. Open this page via https:// to enable scanning.';
      }
      setErrorMsg(msg);
      setState('error');
    }
  }, [cooldownMs]);

  /* ── stop camera ────────────────────────────────────────────────────────── */
  const stopCamera = useCallback(() => {
    stopStream();
    if (mountedRef.current) setState('idle');
  }, []);

  /* ── auto-start on mount ────────────────────────────────────────────────── */
  useEffect(() => {
    startCamera();
    return stopCamera;
  }, []); // deliberately empty – run once

  /* ─── render ──────────────────────────────────────────────────────────── */
  const isActive = state === 'active';

  return (
    <div className="relative w-full max-w-md mx-auto bg-slate-950 rounded-3xl overflow-hidden shadow-2xl border border-slate-800 flex flex-col select-none">

      {/* ── Video viewport ── */}
      <div className="relative w-full aspect-square bg-black overflow-hidden flex items-center justify-center">

        {/*
          The <video> element is ALWAYS in the DOM so the ref is always valid.
          We hide it while not active to avoid a flash of black on first render.
        */}
        <video
          ref={videoRef}
          playsInline
          muted
          autoPlay
          className="w-full h-full object-cover"
          style={{ display: state === 'active' || state === 'requesting' ? 'block' : 'none' }}
        />

        {/* Hidden canvases – used for frame capture only, never shown */}
        {/* eslint-disable-next-line jsx-a11y/media-has-caption */}
        <canvas ref={canvasRef}     style={{ display: 'none' }} />
        <canvas ref={cropCanvasRef} style={{ display: 'none' }} />

        {/* Idle state */}
        {state === 'idle' && (
          <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-6 bg-slate-900">
            <Camera className="w-16 h-16 text-slate-600 mb-4" />
            <p className="text-slate-400 text-sm">Camera is stopped</p>
          </div>
        )}

        {/* Requesting / starting state */}
        {state === 'requesting' && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-900">
            <div className="w-10 h-10 border-4 border-amber-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-slate-400 text-xs mt-4">Starting camera…</p>
          </div>
        )}

        {/* Active: QR targeting reticle */}
        {isActive && (
          <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
            {/* dark vignette around the reticle */}
            <div className="absolute inset-0 bg-black/30" />
            <div className="relative z-10 w-56 h-56">
              {/* white square outline */}
              <div className="absolute inset-0 border-2 border-white/60 rounded-xl" />
              {/* amber corner accents */}
              <div className="absolute top-0 left-0  w-7 h-7 border-t-4 border-l-4 border-amber-400 rounded-tl-xl" />
              <div className="absolute top-0 right-0 w-7 h-7 border-t-4 border-r-4 border-amber-400 rounded-tr-xl" />
              <div className="absolute bottom-0 left-0  w-7 h-7 border-b-4 border-l-4 border-amber-400 rounded-bl-xl" />
              <div className="absolute bottom-0 right-0 w-7 h-7 border-b-4 border-r-4 border-amber-400 rounded-br-xl" />
              {/* scan line */}
              <div className="absolute inset-x-4 top-1/2 h-0.5 -translate-y-1/2 bg-amber-400/80 shadow-[0_0_10px_#fbbf24] animate-pulse" />
              <p className="absolute -bottom-7 left-1/2 -translate-x-1/2 whitespace-nowrap text-[11px] font-semibold text-amber-200/90 uppercase tracking-wider">
                Point at jewellery tag QR
              </p>
            </div>
          </div>
        )}

        {/* Error state */}
        {state === 'error' && (
          <div className="absolute inset-0 bg-slate-900/96 flex flex-col items-center justify-center p-6 text-center gap-4">
            <div className="p-3 bg-red-500/20 text-red-400 rounded-2xl border border-red-500/30">
              <AlertCircle className="w-10 h-10" />
            </div>
            <div>
              <h4 className="text-white font-bold text-sm">Camera Unavailable</h4>
              <p className="text-slate-400 text-xs mt-1 max-w-xs leading-relaxed">{errorMsg}</p>
            </div>
            <button
              onClick={startCamera}
              className="flex items-center gap-2 px-5 py-2.5 bg-amber-600 hover:bg-amber-500 active:scale-95 text-white font-bold text-xs rounded-xl transition"
            >
              <RefreshCw className="w-4 h-4" />
              Retry Camera
            </button>
          </div>
        )}

        {/* Last-scanned badge */}
        {lastScan && isActive && (
          <div
            key={scanCount}
            className="absolute top-4 left-4 right-4 flex justify-center"
          >
            <div className="bg-emerald-950/95 border border-emerald-500/50 backdrop-blur px-3 py-1.5 rounded-full flex items-center gap-2 text-emerald-300 text-xs font-semibold shadow-lg max-w-full">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span className="truncate">Decoded: {lastScan}</span>
            </div>
          </div>
        )}
      </div>

      {/* ── Controls bar ── */}
      <div className="p-4 bg-slate-900 border-t border-slate-800 flex items-center justify-between gap-3">
        {/* Status indicator */}
        <div className="flex items-center gap-2">
          <span className={`w-2.5 h-2.5 rounded-full shrink-0 ${
            isActive ? 'bg-emerald-500 animate-ping' :
            state === 'requesting' ? 'bg-amber-400 animate-pulse' :
            state === 'error' ? 'bg-red-500' :
            'bg-slate-600'
          }`} />
          <span className="text-xs font-medium text-slate-300">
            {isActive ? 'Rear Camera Active' :
             state === 'requesting' ? 'Starting…' :
             state === 'error' ? 'Camera Error' :
             'Camera Stopped'}
          </span>
        </div>

        {/* Action buttons */}
        <div className="flex items-center gap-2">
          {isActive ? (
            <button
              onClick={stopCamera}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 active:scale-95 text-slate-200 text-xs font-semibold rounded-xl border border-slate-700 transition"
            >
              <CameraOff className="w-3.5 h-3.5 text-slate-400" />
              Stop
            </button>
          ) : (
            <button
              onClick={startCamera}
              disabled={state === 'requesting'}
              className="flex items-center gap-1.5 px-3.5 py-1.5 bg-amber-600 hover:bg-amber-500 active:scale-95 text-white text-xs font-bold rounded-xl shadow-sm transition disabled:opacity-50"
            >
              <Camera className="w-3.5 h-3.5" />
              {state === 'requesting' ? 'Starting…' : 'Start'}
            </button>
          )}

          {lastScan && (
            <button
              onClick={() => { lastTextRef.current = null; setLastScan(null); }}
              className="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 active:scale-95 text-slate-400 hover:text-slate-200 text-xs rounded-xl border border-slate-700 transition"
              title="Clear cooldown so same QR can be scanned again immediately"
            >
              Rescan
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
