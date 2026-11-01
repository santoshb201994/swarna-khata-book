import React, { useState, useEffect } from 'react';
import { X, Printer, RefreshCw, Tag } from 'lucide-react';
import type { Product } from '../../types';
import { generateQRDataUrl, getQRPayload } from '../../utils/qrPayload';

interface BulkQRPrintModalProps {
  isOpen: boolean;
  onClose: () => void;
  products: Product[];
}

interface TagItemWithQR {
  product: Product;
  qrUrl: string;
  payload: string;
}

export const BulkQRPrintModal: React.FC<BulkQRPrintModalProps> = ({
  isOpen,
  onClose,
  products,
}) => {
  const [tagItems, setTagItems] = useState<TagItemWithQR[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    let isSubscribed = true;
    if (isOpen && products.length > 0) {
      setIsLoading(true);
      Promise.all(
        products.map(async (p) => {
          const token = p.qr_token || p.sku;
          const qrUrl = await generateQRDataUrl(token, { width: 200, margin: 1 });
          const payload = getQRPayload(token);
          return {
            product: p,
            qrUrl,
            payload,
          };
        })
      )
        .then((items) => {
          if (isSubscribed) {
            setTagItems(items);
            setIsLoading(false);
          }
        })
        .catch((err) => {
          console.error('Failed to generate bulk QRs:', err);
          if (isSubscribed) {
            setIsLoading(false);
          }
        });
    } else {
      setTagItems([]);
    }

    return () => {
      isSubscribed = false;
    };
  }, [isOpen, products]);

  if (!isOpen) return null;

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-xs p-4">
      <div className="bg-white rounded-3xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col border border-slate-200">
        {/* Header */}
        <div className="flex justify-between items-center px-6 py-4 border-b border-slate-100 bg-slate-50 shrink-0 print:hidden">
          <div className="flex items-center gap-2.5">
            <Tag className="w-5 h-5 text-amber-600" />
            <div>
              <h3 className="text-base font-bold text-slate-900">
                Bulk Print Jewellery QR Tags ({products.length})
              </h3>
              <p className="text-xs text-slate-500">
                Dynamic high-contrast tags formatted for standard jewellery label rolls
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handlePrint}
              disabled={isLoading || tagItems.length === 0}
              className="flex items-center gap-2 px-4 py-2 bg-amber-600 hover:bg-amber-700 disabled:opacity-50 text-white font-medium rounded-xl text-xs shadow-sm transition"
            >
              <Printer className="w-4 h-4" />
              <span>Print Sheet</span>
            </button>
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-slate-600 p-1.5 rounded-full hover:bg-slate-200 transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto flex-1">
          {isLoading ? (
            <div className="py-20 flex flex-col items-center justify-center space-y-3 text-slate-400">
              <RefreshCw className="w-8 h-8 animate-spin text-amber-600" />
              <p className="text-xs">Generating dynamic vector QR codes for {products.length} items...</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 print:grid-cols-2 print:gap-3">
              {tagItems.map(({ product, qrUrl, payload }) => (
                <div
                  key={product.id}
                  className="bg-white border-2 border-dashed border-amber-400 rounded-2xl p-3 shadow-xs text-center flex flex-col items-center print:border-solid print:shadow-none print:break-inside-avoid"
                >
                  <div className="text-[10px] font-black tracking-widest text-amber-800 uppercase">
                    SWARNA KHATA
                  </div>
                  <div className="text-[8px] font-semibold text-slate-400 uppercase mb-1.5">
                    JEWELLERS & BULLION
                  </div>

                  {/* QR Image */}
                  <div className="p-1.5 bg-white rounded-lg border border-slate-100 shadow-inner mb-2">
                    <img
                      src={qrUrl}
                      alt={`QR for ${product.sku}`}
                      className="w-24 h-24 object-contain"
                    />
                  </div>

                  {/* Specs */}
                  <div className="w-full text-left bg-amber-50/60 p-2 rounded-lg border border-amber-200/80 text-[10px] space-y-0.5">
                    <div className="flex justify-between">
                      <span className="font-semibold text-slate-600">SKU:</span>
                      <span className="font-mono font-bold text-slate-900">{product.sku}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-semibold text-slate-600">Purity:</span>
                      <span className="font-bold text-amber-900">{product.purity_name || '22KT'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-semibold text-slate-600">Net Wt:</span>
                      <span className="font-mono font-bold text-emerald-700">
                        {Number(product.net_weight).toFixed(3)}g
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-semibold text-slate-600">Gross:</span>
                      <span className="font-mono text-slate-800">
                        {Number(product.gross_weight).toFixed(3)}g
                      </span>
                    </div>
                    {product.huid && (
                      <div className="flex justify-between">
                        <span className="font-semibold text-slate-600">HUID:</span>
                        <span className="font-mono text-indigo-700 font-bold text-[9px]">{product.huid}</span>
                      </div>
                    )}
                  </div>

                  <div className="mt-1 text-[8px] text-slate-400 font-mono truncate max-w-[190px]">
                    {payload}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
