import React, { useRef, useState } from 'react';
import { X, Printer, Download, Copy, Check, Layers } from 'lucide-react';
import type { Tray } from '../../types';
import api from '../../api/client';
import toast from 'react-hot-toast';

interface TrayQRTagModalProps {
  isOpen: boolean;
  onClose: () => void;
  tray: Tray | null;
  onRefresh?: () => void;
}

export const TrayQRTagModal: React.FC<TrayQRTagModalProps> = ({
  isOpen,
  onClose,
  tray,
  onRefresh,
}) => {
  const printAreaRef = useRef<HTMLDivElement>(null);
  const [copied, setCopied] = useState(false);

  if (!isOpen || !tray) return null;

  const handlePrint = async () => {
    try {
      // Increment printed count on backend
      await api.post(`/trays/${tray.id}/mark-printed/`);
      if (onRefresh) onRefresh();
    } catch {
      // Non-blocking
    }
    window.print();
  };

  const handleCopyPayload = () => {
    if (!tray.qr_data) return;
    navigator.clipboard.writeText(tray.qr_data);
    setCopied(true);
    toast.success('Group QR payload copied to clipboard');
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-xs p-4 overflow-y-auto">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl overflow-hidden border border-slate-200 my-8">
        {/* Modal Top Header (Hidden on Print) */}
        <div className="flex justify-between items-center px-6 py-4 border-b border-slate-100 bg-slate-50 print:hidden">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-amber-500 text-white flex items-center justify-center">
              <Layers className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-800">Jewellery Tray Group QR Tag</h3>
              <p className="text-xs text-slate-500">
                Clubbed QR barcode containing full inventory breakdown for this tray
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 p-1.5 rounded-full hover:bg-slate-200 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Printable Tray Tag Sheet */}
        <div ref={printAreaRef} className="p-6 space-y-6">
          {/* Main Card */}
          <div className="bg-gradient-to-br from-amber-50/50 via-white to-amber-50/30 border-2 border-dashed border-amber-400 rounded-2xl p-6 shadow-xs print:border-solid print:border-amber-600 print:shadow-none">
            {/* Tag Header */}
            <div className="text-center border-b border-amber-200 pb-4">
              <div className="text-sm font-black tracking-widest text-amber-900 uppercase">
                SWARNA KHATA JEWELLERS
              </div>
              <div className="text-[11px] text-amber-700/80 font-bold uppercase tracking-wider">
                Showroom Display Tray &bull; Group Barcode Tag
              </div>
              <div className="mt-2 flex items-center justify-center gap-2 flex-wrap">
                <span className="px-3 py-1 bg-amber-600 text-white text-xs font-mono font-bold rounded-full">
                  {tray.code}
                </span>
                <span className="text-base font-black text-slate-900">{tray.name}</span>
                {tray.description && (
                  <span className="text-xs text-slate-500 font-medium">({tray.description})</span>
                )}
              </div>
            </div>

            {/* Middle Section: QR Code & Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center py-5 border-b border-amber-200">
              {/* QR Image */}
              <div className="flex flex-col items-center justify-center">
                <div className="p-3 bg-white rounded-xl border border-amber-200 shadow-sm">
                  {tray.qr_image_url ? (
                    <img
                      src={tray.qr_image_url}
                      alt={`Group QR for ${tray.code}`}
                      className="w-44 h-44 object-contain"
                    />
                  ) : (
                    <div className="w-44 h-44 bg-slate-100 rounded flex items-center justify-center text-xs text-slate-400">
                      Generating QR...
                    </div>
                  )}
                </div>
                <div className="mt-2 text-[10px] text-slate-500 font-semibold uppercase tracking-wider text-center">
                  SCAN AT POS TO BILL ALL TRAY ITEMS
                </div>
              </div>

              {/* Aggregated Totals Grid */}
              <div className="md:col-span-2 grid grid-cols-2 gap-3">
                <div className="bg-white p-3.5 rounded-xl border border-amber-200 shadow-2xs">
                  <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wide">
                    Total Clubbed Pieces
                  </div>
                  <div className="text-2xl font-black text-amber-950 font-mono mt-0.5">
                    {tray.total_items} <span className="text-xs font-semibold text-slate-500">items</span>
                  </div>
                </div>

                <div className="bg-white p-3.5 rounded-xl border border-amber-200 shadow-2xs">
                  <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wide">
                    Total Gross Weight
                  </div>
                  <div className="text-2xl font-black text-amber-950 font-mono mt-0.5">
                    {Number(tray.total_gross_weight).toFixed(3)}{' '}
                    <span className="text-xs font-semibold text-slate-500">g</span>
                  </div>
                </div>

                <div className="bg-white p-3.5 rounded-xl border border-amber-200 shadow-2xs">
                  <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wide">
                    Total Net Weight
                  </div>
                  <div className="text-2xl font-black text-emerald-700 font-mono mt-0.5">
                    {Number(tray.total_net_weight).toFixed(3)}{' '}
                    <span className="text-xs font-semibold text-slate-500">g</span>
                  </div>
                </div>

                <div className="bg-white p-3.5 rounded-xl border border-amber-200 shadow-2xs">
                  <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wide">
                    Total Stone Weight
                  </div>
                  <div className="text-2xl font-black text-slate-700 font-mono mt-0.5">
                    {Number(tray.total_stone_weight).toFixed(3)}{' '}
                    <span className="text-xs font-semibold text-slate-500">g</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Details Table: All Items in that Tray */}
            <div className="mt-5 space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                  Itemized Tray Breakdown ({tray.items?.length || 0} Products)
                </h4>
                <span className="text-[11px] text-slate-500">
                  Printed {tray.printed_count || 0} times
                </span>
              </div>

              <div className="overflow-x-auto rounded-xl border border-amber-200 bg-white">
                <table className="w-full text-left text-xs">
                  <thead className="bg-amber-100/70 border-b border-amber-200 text-amber-950 font-bold">
                    <tr>
                      <th className="py-2 px-3 w-8">#</th>
                      <th className="py-2 px-3">SKU</th>
                      <th className="py-2 px-3">Item Name</th>
                      <th className="py-2 px-3">Purity</th>
                      <th className="py-2 px-3 text-right">Gross Wt</th>
                      <th className="py-2 px-3 text-right">Net Wt</th>
                      <th className="py-2 px-3 text-right">Stone Wt</th>
                      <th className="py-2 px-3">HUID</th>
                      <th className="py-2 px-3 text-center">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 font-medium">
                    {tray.items && tray.items.length > 0 ? (
                      tray.items.map((item, idx) => (
                        <tr key={item.id} className="hover:bg-amber-50/50">
                          <td className="py-2 px-3 text-slate-400 font-mono">{idx + 1}</td>
                          <td className="py-2 px-3 font-mono font-bold text-slate-900">{item.sku}</td>
                          <td className="py-2 px-3 text-slate-700">{item.name}</td>
                          <td className="py-2 px-3 font-semibold text-amber-900">
                            {item.purity || '22KT'}
                          </td>
                          <td className="py-2 px-3 text-right font-mono text-slate-700">
                            {Number(item.gross_weight).toFixed(3)}g
                          </td>
                          <td className="py-2 px-3 text-right font-mono font-bold text-emerald-700">
                            {Number(item.net_weight).toFixed(3)}g
                          </td>
                          <td className="py-2 px-3 text-right font-mono text-slate-500">
                            {Number(item.stone_weight).toFixed(3)}g
                          </td>
                          <td className="py-2 px-3 font-mono text-[11px] text-indigo-700 font-bold">
                            {item.huid || '—'}
                          </td>
                          <td className="py-2 px-3 text-center">
                            <span
                              className={`px-2 py-0.5 text-[10px] font-bold rounded-full ${
                                item.item_status === 'SOLD'
                                  ? 'bg-rose-100 text-rose-800'
                                  : item.item_status === 'IN_CART'
                                  ? 'bg-blue-100 text-blue-800'
                                  : 'bg-emerald-100 text-emerald-800'
                              }`}
                            >
                              {item.item_status || 'AVAILABLE'}
                            </span>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={9} className="py-4 text-center text-slate-400">
                          No items in this tray
                        </td>
                      </tr>
                    )}
                  </tbody>
                  {tray.items && tray.items.length > 0 && (
                    <tfoot className="bg-amber-50/80 font-bold border-t border-amber-200 text-slate-800">
                      <tr>
                        <td colSpan={4} className="py-2 px-3 text-right uppercase text-[11px]">
                          Tray Totals:
                        </td>
                        <td className="py-2 px-3 text-right font-mono text-slate-900">
                          {Number(tray.total_gross_weight).toFixed(3)}g
                        </td>
                        <td className="py-2 px-3 text-right font-mono text-emerald-800">
                          {Number(tray.total_net_weight).toFixed(3)}g
                        </td>
                        <td className="py-2 px-3 text-right font-mono text-slate-700">
                          {Number(tray.total_stone_weight).toFixed(3)}g
                        </td>
                        <td colSpan={2}></td>
                      </tr>
                    </tfoot>
                  )}
                </table>
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons (Hidden on Print) */}
        <div className="px-6 py-4 bg-slate-50 border-t border-slate-100 flex items-center justify-between flex-wrap gap-3 print:hidden">
          <div className="flex items-center gap-2">
            <button
              onClick={handleCopyPayload}
              className="flex items-center gap-1.5 px-3 py-2 text-xs font-bold text-slate-700 bg-white border border-slate-300 rounded-xl hover:bg-slate-50 transition"
              title="Copy JSON QR code payload"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied' : 'Copy QR Data'}</span>
            </button>

            {tray.qr_image_url && (
              <a
                href={tray.qr_image_url}
                download={`group_qr_${tray.code}.png`}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1.5 px-3 py-2 text-xs font-bold text-slate-700 bg-white border border-slate-300 rounded-xl hover:bg-slate-50 transition"
                title="Download QR image PNG"
              >
                <Download className="w-3.5 h-3.5 text-slate-600" />
                <span>Save QR PNG</span>
              </a>
            )}
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="px-4 py-2 text-xs font-bold text-slate-600 hover:bg-slate-200 rounded-xl transition"
            >
              Close
            </button>
            <button
              onClick={handlePrint}
              className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-700 hover:to-amber-600 text-white text-xs font-bold rounded-xl shadow-sm transition"
            >
              <Printer className="w-4 h-4" />
              <span>Print Tray Group Tag</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
