import React, { useRef, useState, useEffect } from 'react';
import { X, Printer, Download, CheckCircle2, ShieldCheck, AlertCircle, Camera, RefreshCw, Copy, Check } from 'lucide-react';
import { BrowserQRCodeReader } from '@zxing/browser';
import type { Product } from '../../types';
import { getQRPayload, generateQRDataUrl, validateQRPayload } from '../../utils/qrPayload';
import api from '../../api/client';
import toast from 'react-hot-toast';

interface QRTagModalProps {
  isOpen: boolean;
  onClose: () => void;
  product: Product | null;
}

export const QRTagModal: React.FC<QRTagModalProps> = ({ isOpen, onClose, product }) => {
  const printAreaRef = useRef<HTMLDivElement>(null);
  const [activeTab, setActiveTab] = useState<'tag' | 'verify'>('tag');
  const [qrDataUrl, setQrDataUrl] = useState<string>('');
  const [isGenerating, setIsGenerating] = useState<boolean>(true);
  const [copiedPayload, setCopiedPayload] = useState<boolean>(false);

  // Verification state
  const [isVerifying, setIsVerifying] = useState<boolean>(false);
  const [isCameraActive, setIsCameraActive] = useState<boolean>(false);
  const [manualPayloadInput, setManualPayloadInput] = useState<string>('');
  const [verificationResult, setVerificationResult] = useState<{
    status: 'idle' | 'success' | 'error';
    message: string;
    printedCount?: number;
  }>({ status: 'idle', message: '' });

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const controlsRef = useRef<any>(null);

  const canonicalPayload = product ? getQRPayload(product.qr_token || product.sku) : '';

  // Generate QR dynamically whenever product changes
  useEffect(() => {
    let isSubscribed = true;
    if (isOpen && product) {
      setIsGenerating(true);
      const token = product.qr_token || product.sku;
      generateQRDataUrl(token, { width: 300, margin: 1 })
        .then((url) => {
          if (isSubscribed) {
            setQrDataUrl(url);
            setIsGenerating(false);
          }
        })
        .catch((err) => {
          console.error('Failed to generate dynamic QR:', err);
          if (isSubscribed) {
            setIsGenerating(false);
          }
        });
    }
    return () => {
      isSubscribed = false;
    };
  }, [isOpen, product]);

  // Clean up camera on tab switch or close
  useEffect(() => {
    if (!isOpen || activeTab !== 'verify') {
      stopCameraScanner();
    }
  }, [isOpen, activeTab]);

  if (!isOpen || !product) return null;

  const handlePrint = () => {
    window.print();
  };

  const handleCopyPayload = () => {
    if (!canonicalPayload) return;
    navigator.clipboard.writeText(canonicalPayload);
    setCopiedPayload(true);
    toast.success('Canonical QR Payload copied!');
    setTimeout(() => setCopiedPayload(false), 2000);
  };

  const startCameraScanner = async () => {
    setIsCameraActive(true);
    setVerificationResult({ status: 'idle', message: '' });

    try {
      const codeReader = new BrowserQRCodeReader();
      const videoElement = videoRef.current;
      if (!videoElement) return;

      const controls = await codeReader.decodeFromVideoDevice(
        undefined,
        videoElement,
        (result, error) => {
          if (result) {
            const scannedText = result.getText();
            stopCameraScanner();
            verifyPayload(scannedText);
          }
          if (error && !(error.name === 'NotFoundException')) {
            // normal frame scan miss
          }
        }
      );
      controlsRef.current = controls;
    } catch (err: any) {
      console.warn('Camera verification scanner failed to start:', err);
      toast.error('Could not access camera for tag verification.');
      setIsCameraActive(false);
    }
  };

  const stopCameraScanner = () => {
    if (controlsRef.current) {
      try {
        controlsRef.current.stop();
      } catch {
        // ignore
      }
      controlsRef.current = null;
    }
    setIsCameraActive(false);
  };

  const verifyPayload = async (scannedPayload: string) => {
    if (!product) return;
    setIsVerifying(true);

    // 1. Local validation check
    const localVal = validateQRPayload(scannedPayload, product.qr_token, product.sku);

    try {
      const tokenToQuery = product.qr_token || product.sku;
      const res = await api.post(`/pos/items/${tokenToQuery}/verify-tag/`, {
        scanned_payload: scannedPayload.trim(),
      });

      if (res.data.match) {
        setVerificationResult({
          status: 'success',
          message: 'Verified Physical Tag! Tag matches this jewellery item and is ready for inventory.',
          printedCount: res.data.printed_count,
        });
        toast.success('Physical Tag Verified Successfully!');
      } else {
        setVerificationResult({
          status: 'error',
          message: res.data.message || 'Scanned tag payload does not match this item.',
        });
        toast.error('Tag Mismatch!');
      }
    } catch {
      // Fallback to client-side validation if offline or endpoint error
      if (localVal.match) {
        setVerificationResult({
          status: 'success',
          message: localVal.message,
        });
        toast.success('Verified locally against item identity!');
      } else {
        setVerificationResult({
          status: 'error',
          message: localVal.message,
        });
        toast.error('Tag Mismatch!');
      }
    } finally {
      setIsVerifying(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-xs p-4">
      <div className="bg-white rounded-3xl shadow-2xl w-full max-w-lg overflow-hidden border border-slate-200">
        {/* Header */}
        <div className="flex justify-between items-center px-6 py-4 border-b border-slate-100 bg-slate-50">
          <div>
            <h3 className="text-base font-bold text-slate-900">Jewellery QR Barcode Tag</h3>
            <p className="text-xs text-slate-500 font-mono">
              Payload: {canonicalPayload.substring(0, 24)}...
            </p>
          </div>
          <button
            onClick={() => {
              stopCameraScanner();
              onClose();
            }}
            className="text-slate-400 hover:text-slate-600 p-1.5 rounded-full hover:bg-slate-200 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Selector */}
        <div className="flex border-b border-slate-200 bg-slate-100/60 px-6 pt-3 gap-2">
          <button
            type="button"
            onClick={() => setActiveTab('tag')}
            className={`px-4 py-2 text-xs font-bold rounded-t-xl transition ${
              activeTab === 'tag'
                ? 'bg-white text-amber-700 shadow-xs border-t-2 border-amber-600'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Tag & Print
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('verify')}
            className={`px-4 py-2 text-xs font-bold rounded-t-xl transition flex items-center gap-1.5 ${
              activeTab === 'verify'
                ? 'bg-white text-amber-700 shadow-xs border-t-2 border-amber-600'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>Verify Physical Tag</span>
          </button>
        </div>

        {activeTab === 'tag' ? (
          <div className="p-6 flex flex-col items-center">
            {/* Real Jewellery Physical Tag Layout */}
            <div
              ref={printAreaRef}
              className="w-80 bg-white border-2 border-dashed border-amber-500 rounded-2xl p-4 shadow-sm text-center flex flex-col items-center print:border-solid print:shadow-none"
            >
              <div className="text-xs font-black tracking-widest text-amber-800 uppercase mb-0.5">
                SWARNA KHATA
              </div>
              <div className="text-[9px] font-semibold text-slate-500 mb-2 tracking-wider">
                JEWELLERS & BULLION
              </div>

              {/* Dynamic QR Display */}
              <div className="p-2.5 bg-white rounded-xl border border-slate-200 shadow-inner mb-3">
                {isGenerating ? (
                  <div className="w-36 h-36 flex items-center justify-center text-xs text-slate-400">
                    <RefreshCw className="w-5 h-5 animate-spin text-amber-600" />
                  </div>
                ) : qrDataUrl ? (
                  <img
                    src={qrDataUrl}
                    alt={`QR for ${product.sku}`}
                    className="w-36 h-36 object-contain"
                  />
                ) : (
                  <div className="w-36 h-36 bg-slate-100 rounded-lg flex items-center justify-center text-xs text-slate-400">
                    No QR generated
                  </div>
                )}
              </div>

              {/* Product Specs Box */}
              <div className="w-full text-left bg-amber-50/70 p-2.5 rounded-xl border border-amber-200 text-xs space-y-1">
                <div className="flex justify-between">
                  <span className="font-semibold text-slate-600">SKU:</span>
                  <span className="font-mono font-bold text-slate-900">{product.sku}</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-semibold text-slate-600">Design:</span>
                  <span className="font-medium text-slate-800 truncate max-w-[170px]">{product.name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-semibold text-slate-600">Purity:</span>
                  <span className="font-bold text-amber-900">{product.purity_name || '22KT (916)'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-semibold text-slate-600">Gross Wt:</span>
                  <span className="font-mono text-slate-800">{Number(product.gross_weight).toFixed(3)} g</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-semibold text-slate-600">Net Wt:</span>
                  <span className="font-mono font-bold text-emerald-700">{Number(product.net_weight).toFixed(3)} g</span>
                </div>
                {product.huid && (
                  <div className="flex justify-between">
                    <span className="font-semibold text-slate-600">HUID:</span>
                    <span className="font-mono text-[10px] text-indigo-700 font-bold">{product.huid}</span>
                  </div>
                )}
              </div>

              {/* Canonical Payload pill */}
              <div className="mt-2.5 flex items-center justify-between w-full px-2 py-1 bg-slate-50 border border-slate-200 rounded-lg text-[10px] text-slate-600 font-mono">
                <span className="truncate max-w-[210px]">{canonicalPayload}</span>
                <button
                  type="button"
                  onClick={handleCopyPayload}
                  className="text-amber-700 hover:text-amber-900 p-0.5"
                  title="Copy payload"
                >
                  {copiedPayload ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                </button>
              </div>

              <div className="mt-2 text-[9px] text-slate-400 tracking-wider">
                SCAN AT POS TO BILL
              </div>
            </div>

            {/* Actions */}
            <div className="mt-6 flex items-center gap-3 w-full">
              <button
                onClick={handlePrint}
                className="flex-1 flex items-center justify-center gap-2 py-2.5 bg-amber-600 hover:bg-amber-700 text-white font-medium rounded-xl shadow-sm transition"
              >
                <Printer className="w-4 h-4" />
                <span>Print Tag</span>
              </button>
              {qrDataUrl && (
                <a
                  href={qrDataUrl}
                  download={`tag_${product.sku}.png`}
                  className="flex items-center justify-center gap-2 px-4 py-2.5 border border-slate-300 text-slate-700 font-medium rounded-xl hover:bg-slate-50 transition"
                >
                  <Download className="w-4 h-4" />
                  <span>Save PNG</span>
                </a>
              )}
            </div>
          </div>
        ) : (
          /* Verification Tab */
          <div className="p-6 space-y-4">
            <div className="text-center space-y-1">
              <h4 className="text-sm font-bold text-slate-800">Physical Tag Verification</h4>
              <p className="text-xs text-slate-500">
                Confirm your printed physical tag matches this item's identity before attaching it.
              </p>
            </div>

            {/* Status Banner */}
            {verificationResult.status === 'success' && (
              <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-2xl flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
                <div className="text-xs">
                  <p className="font-bold text-emerald-900">Tag Verified & Valid!</p>
                  <p className="text-emerald-700 mt-0.5">{verificationResult.message}</p>
                  {verificationResult.printedCount !== undefined && (
                    <p className="text-emerald-800 font-semibold mt-1">
                      Total print verifications: {verificationResult.printedCount}
                    </p>
                  )}
                </div>
              </div>
            )}

            {verificationResult.status === 'error' && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-2xl flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
                <div className="text-xs">
                  <p className="font-bold text-red-900">Verification Failed</p>
                  <p className="text-red-700 mt-0.5">{verificationResult.message}</p>
                </div>
              </div>
            )}

            {/* Camera View */}
            <div className="border border-slate-200 rounded-2xl overflow-hidden bg-slate-900 aspect-4/3 relative flex items-center justify-center">
              <video
                ref={videoRef}
                className={`w-full h-full object-cover ${isCameraActive ? 'block' : 'hidden'}`}
                autoPlay
                playsInline
                muted
              />

              {!isCameraActive && (
                <div className="text-center p-6 space-y-3">
                  <Camera className="w-10 h-10 text-slate-500 mx-auto" />
                  <p className="text-xs text-slate-400">
                    Use your device camera to scan the printed physical jewellery tag
                  </p>
                  <button
                    type="button"
                    onClick={startCameraScanner}
                    className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white font-medium rounded-xl text-xs transition"
                  >
                    Start Camera Verification
                  </button>
                </div>
              )}

              {isCameraActive && (
                <div className="absolute inset-0 pointer-events-none flex flex-col items-center justify-center p-6">
                  <div className="w-48 h-48 border-2 border-emerald-400 rounded-2xl relative animate-pulse shadow-[0_0_20px_rgba(52,211,153,0.3)]" />
                  <p className="text-[11px] text-white/90 bg-black/60 px-3 py-1 rounded-full mt-3 backdrop-blur-xs">
                    Align printed tag within frame
                  </p>
                </div>
              )}
            </div>

            {isCameraActive && (
              <button
                type="button"
                onClick={stopCameraScanner}
                className="w-full py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium rounded-xl text-xs transition"
              >
                Stop Camera
              </button>
            )}

            {/* Manual Verification Input */}
            <div className="pt-2 border-t border-slate-100">
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                Or paste scanned barcode / payload:
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={manualPayloadInput}
                  onChange={(e) => setManualPayloadInput(e.target.value)}
                  placeholder="e.g. SKB:a8f31c92-..."
                  className="flex-1 px-3 py-2 border border-slate-300 rounded-xl text-xs font-mono focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                />
                <button
                  type="button"
                  disabled={!manualPayloadInput.trim() || isVerifying}
                  onClick={() => verifyPayload(manualPayloadInput.trim())}
                  className="px-4 py-2 bg-slate-900 hover:bg-slate-800 disabled:opacity-50 text-white font-medium rounded-xl text-xs transition"
                >
                  {isVerifying ? 'Checking...' : 'Verify'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
