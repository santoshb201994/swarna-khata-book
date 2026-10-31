import React, { useState, useMemo } from 'react';
import { X, Layers, Plus, Trash2, Search, QrCode } from 'lucide-react';
import api from '../../api/client';
import type { Product, Tray } from '../../types';
import toast from 'react-hot-toast';

interface ClubTrayModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedProducts: Product[];
  allProducts: Product[];
  editingTray?: Tray | null;
  onTraySaved: (tray: Tray) => void;
}

export const ClubTrayModal: React.FC<ClubTrayModalProps> = ({
  isOpen,
  onClose,
  selectedProducts,
  allProducts,
  editingTray,
  onTraySaved,
}) => {
  const [trayName, setTrayName] = useState('');
  const [trayCode, setTrayCode] = useState('');
  const [description, setDescription] = useState('');
  const [items, setItems] = useState<Product[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Initialize form when modal opens or props change
  React.useEffect(() => {
    if (isOpen) {
      if (editingTray) {
        setTrayName(editingTray.name || '');
        setTrayCode(editingTray.code || '');
        setDescription(editingTray.description || '');
        // Map tray.items to Product list
        const mappedItems: Product[] = editingTray.items.map((it) => {
          const match = allProducts.find((p) => p.id === it.id);
          if (match) return match;
          return {
            id: it.id,
            sku: it.sku,
            name: it.name,
            category: 0,
            category_name: it.category_name,
            purity: 0,
            purity_name: it.purity,
            gross_weight: String(it.gross_weight),
            net_weight: String(it.net_weight),
            stone_weight: String(it.stone_weight),
            other_weight: '0.000',
            making_charge_type: 'per_gram',
            making_charge_value: '0.00',
            description: '',
            hsn_code: '7113',
            huid: it.huid || '',
            is_active: true,
            created_at: '',
          };
        });
        setItems(mappedItems);
      } else {
        const currentYear = new Date().getFullYear();
        const randId = Math.floor(100 + Math.random() * 900);
        setTrayName(`Display Tray ${randId}`);
        setTrayCode(`TRAY-${currentYear}-${randId}`);
        setDescription('');
        setItems(selectedProducts);
      }
      setSearchQuery('');
    }
  }, [isOpen, editingTray, selectedProducts, allProducts]);

  // Aggregate totals
  const totals = useMemo(() => {
    let gross = 0;
    let net = 0;
    let stone = 0;
    items.forEach((p) => {
      gross += parseFloat(p.gross_weight) || 0;
      net += parseFloat(p.net_weight) || 0;
      stone += parseFloat(p.stone_weight) || 0;
    });
    return {
      count: items.length,
      gross: gross.toFixed(3),
      net: net.toFixed(3),
      stone: stone.toFixed(3),
    };
  }, [items]);

  // Search unselected products to add
  const availableToAdd = useMemo(() => {
    if (!searchQuery.trim()) return [];
    const q = searchQuery.toLowerCase().trim();
    const existingIds = new Set(items.map((i) => i.id));
    return allProducts
      .filter(
        (p) =>
          !existingIds.has(p.id) &&
          (p.sku.toLowerCase().includes(q) ||
            p.name.toLowerCase().includes(q) ||
            (p.huid && p.huid.toLowerCase().includes(q)))
      )
      .slice(0, 8);
  }, [allProducts, items, searchQuery]);

  const handleAddItem = (prod: Product) => {
    setItems((prev) => [...prev, prod]);
    setSearchQuery('');
  };

  const handleRemoveItem = (prodId: number) => {
    setItems((prev) => prev.filter((p) => p.id !== prodId));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!trayName.trim()) {
      toast.error('Please enter a tray name');
      return;
    }
    if (items.length === 0) {
      toast.error('Please select at least 1 jewelry item to club into the tray');
      return;
    }

    try {
      setIsSubmitting(true);
      const payload = {
        name: trayName.trim(),
        code: trayCode.trim() || undefined,
        description: description.trim(),
        product_ids: items.map((i) => i.id),
      };

      let res;
      if (editingTray) {
        res = await api.put(`/trays/${editingTray.id}/`, payload);
        toast.success(`Tray "${res.data.name}" updated successfully!`);
      } else {
        res = await api.post('/trays/', payload);
        toast.success(`Group QR Code generated for "${res.data.name}"!`);
      }

      onTraySaved(res.data);
      onClose();
    } catch (err: any) {
      const msg = err.response?.data?.error || err.response?.data?.message || 'Failed to save tray';
      toast.error(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-xs p-4 overflow-y-auto">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-3xl overflow-hidden border border-slate-200 my-8">
        {/* Header */}
        <div className="flex justify-between items-center px-6 py-4 border-b border-slate-100 bg-gradient-to-r from-amber-50 to-orange-50">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-amber-500 text-white flex items-center justify-center shadow-sm">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-black text-slate-800">
                {editingTray ? 'Edit Tray & Group QR Tag' : 'Club QR Codes into Tray Group'}
              </h3>
              <p className="text-xs text-amber-900/70">
                Group jewelry pieces together to create a unified tray QR barcode label
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

        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          {/* Form Fields: Name, Code, Description */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Tray Display Name <span className="text-rose-500">*</span>
              </label>
              <input
                type="text"
                value={trayName}
                onChange={(e) => setTrayName(e.target.value)}
                placeholder="e.g. Tray 1 - 22KT Antique Bangles"
                className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-hidden focus:ring-1 focus:ring-amber-500 font-medium"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Tray Identifier Code <span className="text-slate-400 font-normal">(Auto or Custom)</span>
              </label>
              <input
                type="text"
                value={trayCode}
                onChange={(e) => setTrayCode(e.target.value)}
                placeholder="e.g. TRAY-2026-001"
                className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-hidden focus:ring-1 focus:ring-amber-500 font-mono font-bold text-amber-900"
              />
            </div>

            <div className="sm:col-span-2">
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Counter / Showroom Location Note <span className="text-slate-400 font-normal">(Optional)</span>
              </label>
              <input
                type="text"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="e.g. Main showcase counter #2, front display"
                className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-hidden focus:ring-1 focus:ring-amber-500 font-medium"
              />
            </div>
          </div>

          {/* Quick Metrics Bar */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-amber-50/70 p-3.5 rounded-xl border border-amber-200">
            <div>
              <div className="text-[11px] font-semibold text-amber-800">Total Pieces</div>
              <div className="text-lg font-black text-amber-950 font-mono">{totals.count} pcs</div>
            </div>
            <div>
              <div className="text-[11px] font-semibold text-amber-800">Total Gross Wt</div>
              <div className="text-lg font-black text-amber-950 font-mono">{totals.gross} g</div>
            </div>
            <div>
              <div className="text-[11px] font-semibold text-amber-800">Total Net Wt</div>
              <div className="text-lg font-black text-emerald-800 font-mono">{totals.net} g</div>
            </div>
            <div>
              <div className="text-[11px] font-semibold text-amber-800">Total Stone Wt</div>
              <div className="text-lg font-black text-slate-700 font-mono">{totals.stone} g</div>
            </div>
          </div>

          {/* Add more items picker */}
          <div className="relative">
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Add More Items to this Tray
            </label>
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search SKU, name, or HUID to add..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-hidden focus:ring-1 focus:ring-amber-500 font-medium"
              />
            </div>

            {availableToAdd.length > 0 && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-slate-200 rounded-xl shadow-lg z-20 max-h-48 overflow-y-auto divide-y divide-slate-100">
                {availableToAdd.map((prod) => (
                  <button
                    key={prod.id}
                    type="button"
                    onClick={() => handleAddItem(prod)}
                    className="w-full px-3 py-2 text-left hover:bg-amber-50/80 flex items-center justify-between text-xs transition"
                  >
                    <div>
                      <span className="font-bold font-mono text-slate-800 mr-2">{prod.sku}</span>
                      <span className="text-slate-600">{prod.name}</span>
                      <span className="text-slate-400 text-[10px] ml-2">({prod.purity_name || '22KT'})</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-slate-500">{prod.gross_weight}g</span>
                      <span className="px-2 py-0.5 bg-amber-100 text-amber-800 rounded font-bold text-[10px] flex items-center gap-1">
                        <Plus className="w-3 h-3" /> Add
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Clubbed Products Table */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-700">
                Items Clubbed in this Tray ({items.length})
              </span>
              {items.length > 0 && (
                <button
                  type="button"
                  onClick={() => setItems([])}
                  className="text-[11px] text-rose-600 hover:text-rose-700 font-semibold"
                >
                  Clear All
                </button>
              )}
            </div>

            <div className="max-h-56 overflow-y-auto border border-slate-200 rounded-xl">
              {items.length === 0 ? (
                <div className="py-8 text-center text-xs text-slate-400">
                  No items in this tray yet. Search and add products above.
                </div>
              ) : (
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-bold sticky top-0">
                    <tr>
                      <th className="py-2 px-3">SKU</th>
                      <th className="py-2 px-3">Item Name</th>
                      <th className="py-2 px-3">Purity</th>
                      <th className="py-2 px-3 text-right">Gross Wt</th>
                      <th className="py-2 px-3 text-right">Net Wt</th>
                      <th className="py-2 px-3 text-center">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 font-medium">
                    {items.map((prod) => (
                      <tr key={prod.id} className="hover:bg-slate-50/70">
                        <td className="py-2 px-3 font-mono font-bold text-slate-900">{prod.sku}</td>
                        <td className="py-2 px-3 text-slate-700">{prod.name}</td>
                        <td className="py-2 px-3 text-amber-900">{prod.purity_name || '22KT'}</td>
                        <td className="py-2 px-3 text-right font-mono text-slate-700">{prod.gross_weight}g</td>
                        <td className="py-2 px-3 text-right font-mono font-bold text-emerald-700">{prod.net_weight}g</td>
                        <td className="py-2 px-3 text-center">
                          <button
                            type="button"
                            onClick={() => handleRemoveItem(prod.id)}
                            className="p-1 text-slate-400 hover:text-rose-600 rounded hover:bg-rose-50 transition"
                            title="Remove from tray"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>

          {/* Footer Actions */}
          <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-4 py-2 text-xs font-bold text-slate-600 hover:bg-slate-100 rounded-xl transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || items.length === 0}
              className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-700 hover:to-amber-600 text-white text-xs font-bold rounded-xl shadow-md transition disabled:opacity-50"
            >
              <QrCode className="w-4 h-4" />
              <span>{isSubmitting ? 'Generating QR...' : editingTray ? 'Update & Refresh QR' : 'Generate Group QR Code'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
