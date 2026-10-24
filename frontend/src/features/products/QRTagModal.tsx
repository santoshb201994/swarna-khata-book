import React, { useRef } from 'react';
import { X, Printer, Download } from 'lucide-react';
import type { Product } from '../../types';

interface QRTagModalProps {
  isOpen: boolean;
  onClose: () => void;
  product: Product | null;
}

export const QRTagModal: React.FC<QRTagModalProps> = ({ isOpen, onClose, product }) => {
  const printAreaRef = useRef<HTMLDivElement>(null);

  if (!isOpen || !product) return null;

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-xs p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden border border-slate-200">
        <div className="flex justify-between items-center px-6 py-4 border-b border-slate-100 bg-slate-50">
          <h3 className="text-base font-semibold text-slate-800">Jewelry QR Barcode Tag</h3>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 p-1 rounded-full hover:bg-slate-200 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 flex flex-col items-center">
          {/* Tag Container - styled like real jewelry tags */}
          <div
            ref={printAreaRef}
            className="w-72 bg-white border-2 border-dashed border-amber-500 rounded-xl p-4 shadow-sm text-center flex flex-col items-center print:border-solid print:shadow-none"
          >
            <div className="text-xs font-black tracking-widest text-amber-800 uppercase mb-1">
              SWARNA KHATA
            </div>
            <div className="text-[10px] text-slate-500 mb-2">JEWELLERS & BULLION</div>

            {product.qr_code_url ? (
              <div className="p-2 bg-white rounded-lg border border-slate-100 shadow-inner mb-3">
                <img
                  src={product.qr_code_url}
                  alt={`QR for ${product.sku}`}
                  className="w-36 h-36 object-contain"
                />
              </div>
            ) : (
              <div className="w-36 h-36 bg-slate-100 rounded-lg flex items-center justify-center text-xs text-slate-400 mb-3">
                No QR generated
              </div>
            )}

            <div className="w-full text-left bg-amber-50/70 p-2.5 rounded-lg border border-amber-200 text-xs space-y-1">
              <div className="flex justify-between">
                <span className="font-semibold text-slate-600">SKU:</span>
                <span className="font-mono font-bold text-slate-900">{product.sku}</span>
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

            <div className="mt-2 text-[9px] text-slate-400 tracking-wider">
              SCAN AT POS TO BILL
            </div>
          </div>

          <div className="mt-6 flex items-center gap-3 w-full">
            <button
              onClick={handlePrint}
              className="flex-1 flex items-center justify-center gap-2 py-2.5 bg-amber-600 hover:bg-amber-700 text-white font-medium rounded-xl shadow-sm transition"
            >
              <Printer className="w-4 h-4" />
              <span>Print Tag</span>
            </button>
            {product.qr_code_url && (
              <a
                href={product.qr_code_url}
                download={`tag_${product.sku}.png`}
                target="_blank"
                rel="noreferrer"
                className="flex items-center justify-center gap-2 px-4 py-2.5 border border-slate-300 text-slate-700 font-medium rounded-xl hover:bg-slate-50 transition"
              >
                <Download className="w-4 h-4" />
                <span>Save</span>
              </a>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
