import React, { useState } from 'react';
import {
  X,
  Download,
  Calendar,
  FileSpreadsheet,
  CheckCircle2,
  ShieldCheck,
  HardDriveDownload,
  Database,
  Layers,
  Sparkles,
  Loader2,
} from 'lucide-react';
import api from '../../api/client';
import toast from 'react-hot-toast';

interface ExportDataModalProps {
  isOpen: boolean;
  onClose: () => void;
  shopName?: string;
}

export const ExportDataModal: React.FC<ExportDataModalProps> = ({
  isOpen,
  onClose,
  shopName,
}) => {
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [isDownloading, setIsDownloading] = useState<boolean>(false);
  const [activePreset, setActivePreset] = useState<'all' | '30d' | '90d' | 'fy'>('all');

  if (!isOpen) return null;

  // Preset Date Handlers
  const handlePresetChange = (preset: 'all' | '30d' | '90d' | 'fy') => {
    setActivePreset(preset);
    const today = new Date();
    const pad = (n: number) => n.toString().padStart(2, '0');
    const toYMD = (d: Date) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;

    if (preset === 'all') {
      setStartDate('');
      setEndDate('');
    } else if (preset === '30d') {
      const past = new Date();
      past.setDate(today.getDate() - 30);
      setStartDate(toYMD(past));
      setEndDate(toYMD(today));
    } else if (preset === '90d') {
      const past = new Date();
      past.setDate(today.getDate() - 90);
      setStartDate(toYMD(past));
      setEndDate(toYMD(today));
    } else if (preset === 'fy') {
      // Indian Financial Year: April 1 to March 31
      const year = today.getMonth() >= 3 ? today.getFullYear() : today.getFullYear() - 1;
      setStartDate(`${year}-04-01`);
      setEndDate(`${year + 1}-03-31`);
    }
  };

  const handleDownload = async () => {
    if (startDate && endDate && startDate > endDate) {
      toast.error('Start Date cannot be after End Date.');
      return;
    }

    try {
      setIsDownloading(true);
      const loadingToast = toast.loading('Compiling and streaming store data archive...');

      const params: Record<string, string> = {};
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;

      const response = await api.get('/export/shop/', {
        params,
        responseType: 'blob',
      });

      // Extract filename from Content-Disposition if present
      let filename = `swarna_khata_export_${new Date().toISOString().slice(0, 10)}.zip`;
      const disposition = response.headers['content-disposition'];
      if (disposition && disposition.includes('filename=')) {
        const match = disposition.match(/filename="?([^";]+)"?/);
        if (match && match[1]) {
          filename = match[1];
        }
      }

      // Create download trigger
      const blob = new Blob([response.data], { type: 'application/zip' });
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(downloadUrl);

      toast.dismiss(loadingToast);
      toast.success('Store data archive downloaded successfully!');
      onClose();
    } catch (err: any) {
      console.error('Export download failed:', err);
      toast.error(
        err.response?.status === 403
          ? 'Permission denied: Store Owner or Superadmin role required.'
          : 'Failed to generate export archive. Please try again.'
      );
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in duration-200">
      <div className="bg-white rounded-3xl shadow-2xl border border-slate-200 w-full max-w-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="px-6 py-5 bg-gradient-to-r from-amber-600 via-amber-500 to-amber-700 text-white flex items-center justify-between shadow-md">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white/20 backdrop-blur-md rounded-2xl flex items-center justify-center text-white shadow-inner">
              <HardDriveDownload className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-black tracking-tight">Export Store Data Archive</h2>
                <span className="px-2 py-0.5 rounded-full bg-white/25 text-white text-[10px] font-bold uppercase tracking-wider">
                  Owner Level 80+
                </span>
              </div>
              <p className="text-xs text-amber-100 font-medium">
                {shopName ? `${shopName} • ` : ''}Download complete CSV datasets & audit manifest in a single compressed ZIP
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            disabled={isDownloading}
            className="p-2 text-white/80 hover:text-white hover:bg-white/10 rounded-xl transition cursor-pointer"
            aria-label="Close modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-6">
          {/* Preset Buttons */}
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
              Time Period Filter
            </label>
            <div className="grid grid-cols-4 gap-2">
              <button
                type="button"
                onClick={() => handlePresetChange('all')}
                className={`py-2 px-3 text-xs font-bold rounded-xl border transition ${
                  activePreset === 'all'
                    ? 'bg-amber-500 text-slate-950 border-amber-600 shadow-xs'
                    : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                }`}
              >
                All Time
              </button>
              <button
                type="button"
                onClick={() => handlePresetChange('30d')}
                className={`py-2 px-3 text-xs font-bold rounded-xl border transition ${
                  activePreset === '30d'
                    ? 'bg-amber-500 text-slate-950 border-amber-600 shadow-xs'
                    : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                }`}
              >
                Last 30 Days
              </button>
              <button
                type="button"
                onClick={() => handlePresetChange('90d')}
                className={`py-2 px-3 text-xs font-bold rounded-xl border transition ${
                  activePreset === '90d'
                    ? 'bg-amber-500 text-slate-950 border-amber-600 shadow-xs'
                    : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                }`}
              >
                Last 90 Days
              </button>
              <button
                type="button"
                onClick={() => handlePresetChange('fy')}
                className={`py-2 px-3 text-xs font-bold rounded-xl border transition ${
                  activePreset === 'fy'
                    ? 'bg-amber-500 text-slate-950 border-amber-600 shadow-xs'
                    : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                }`}
              >
                Current FY
              </button>
            </div>
          </div>

          {/* Date Pickers */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 bg-slate-50/75 p-4 rounded-2xl border border-slate-200/80">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1 flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-amber-600" />
                From Date (Optional)
              </label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => {
                  setStartDate(e.target.value);
                  setActivePreset('all');
                }}
                className="w-full px-3 py-2 bg-white border border-slate-300 rounded-xl text-xs font-medium text-slate-800 focus:outline-hidden focus:ring-2 focus:ring-amber-500/30"
              />
              <span className="text-[10px] text-slate-400 mt-1 block">Leave empty for start of history</span>
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1 flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-amber-600" />
                To Date (Optional)
              </label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => {
                  setEndDate(e.target.value);
                  setActivePreset('all');
                }}
                className="w-full px-3 py-2 bg-white border border-slate-300 rounded-xl text-xs font-medium text-slate-800 focus:outline-hidden focus:ring-2 focus:ring-amber-500/30"
              />
              <span className="text-[10px] text-slate-400 mt-1 block">Leave empty for latest records</span>
            </div>
          </div>

          {/* Included Datasets Checklist */}
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-amber-600" />
              Included Datasets in Download (.ZIP)
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
              <div className="flex items-center gap-2 p-2.5 bg-slate-50 border border-slate-200/80 rounded-xl">
                <FileSpreadsheet className="w-4 h-4 text-emerald-600 shrink-0" />
                <div>
                  <div className="font-bold text-slate-800">Sales & Invoices</div>
                  <div className="text-[10px] text-slate-500">sales_invoices.csv, sale_items.csv, payments.csv</div>
                </div>
              </div>

              <div className="flex items-center gap-2 p-2.5 bg-slate-50 border border-slate-200/80 rounded-xl">
                <Database className="w-4 h-4 text-amber-600 shrink-0" />
                <div>
                  <div className="font-bold text-slate-800">Inventory & Stock</div>
                  <div className="text-[10px] text-slate-500">inventory_products.csv, stock_movements.csv</div>
                </div>
              </div>

              <div className="flex items-center gap-2 p-2.5 bg-slate-50 border border-slate-200/80 rounded-xl">
                <Sparkles className="w-4 h-4 text-indigo-600 shrink-0" />
                <div>
                  <div className="font-bold text-slate-800">Accounting & Daybook</div>
                  <div className="text-[10px] text-slate-500">daybook_cash.csv, gold_rates_history.csv</div>
                </div>
              </div>

              <div className="flex items-center gap-2 p-2.5 bg-slate-50 border border-slate-200/80 rounded-xl">
                <CheckCircle2 className="w-4 h-4 text-cyan-600 shrink-0" />
                <div>
                  <div className="font-bold text-slate-800">Directory & Manifest</div>
                  <div className="text-[10px] text-slate-500">customers.csv, showroom_staff.csv, export_manifest.json</div>
                </div>
              </div>
            </div>
          </div>

          {/* Enterprise Production Safeguards Note */}
          <div className="p-3.5 bg-amber-50/70 border border-amber-200 rounded-2xl flex items-start gap-3">
            <ShieldCheck className="w-5 h-5 text-amber-700 shrink-0 mt-0.5" />
            <div className="text-xs text-amber-900 leading-relaxed">
              <span className="font-bold">Enterprise Architectural Safeguards: </span>
              Export is streamed directly using database cursors and chunked temp-file buffering to prevent memory spikes.
              Files are encoded with <span className="font-mono font-semibold">UTF-8-SIG</span> for seamless native opening in Microsoft Excel with Kannada and English characters. Sensitive password credentials are automatically sanitized.
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-slate-50 border-t border-slate-200 flex items-center justify-between">
          <div className="text-xs text-slate-500">
            {startDate || endDate ? (
              <span>Filtering from <span className="font-bold text-slate-700">{startDate || 'inception'}</span> to <span className="font-bold text-slate-700">{endDate || 'today'}</span></span>
            ) : (
              <span>Full Historical Store Archive</span>
            )}
          </div>
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={onClose}
              disabled={isDownloading}
              className="px-4 py-2 text-xs font-bold text-slate-600 hover:text-slate-800 hover:bg-slate-200/60 rounded-xl transition cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleDownload}
              disabled={isDownloading}
              className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-700 hover:to-amber-600 text-white font-black text-xs rounded-xl shadow-md shadow-amber-600/20 transition active:scale-95 disabled:opacity-50 cursor-pointer"
            >
              {isDownloading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Preparing Archive...</span>
                </>
              ) : (
                <>
                  <Download className="w-4 h-4" />
                  <span>Download Archive (.ZIP)</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
