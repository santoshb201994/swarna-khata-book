import React, { useState, useEffect } from 'react';
import { Camera, X, Check, Sparkles } from 'lucide-react';
import type { Category, Purity } from '../../types';
import api from '../../api/client';
import toast from 'react-hot-toast';
import { CameraCaptureModal } from '../camera/CameraCaptureModal';

interface ProductFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  categories: Category[];
  purities: Purity[];
}

export const ProductFormModal: React.FC<ProductFormModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  categories,
  purities,
}) => {
  const [name, setName] = useState('');
  const [sku, setSku] = useState('');
  const [categoryId, setCategoryId] = useState<number>(categories[0]?.id || 1);
  const [purityId, setPurityId] = useState<number>(purities[0]?.id || 1);
  const [grossWeight, setGrossWeight] = useState('');
  const [stoneWeight, setStoneWeight] = useState('0.000');
  const [otherWeight, setOtherWeight] = useState('0.000');
  const [makingType, setMakingType] = useState<'per_gram' | 'percent' | 'fixed'>('per_gram');
  const [makingCharge, setMakingCharge] = useState('450.00');
  const hsnCode = '7113';
  const [huid, setHuid] = useState('');
  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
  const [isCameraOpen, setIsCameraOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleCategoryChange = (newCatId: number) => {
    setCategoryId(newCatId);
    const cat = categories.find((c) => c.id === newCatId);
    if (cat) {
      const catName = cat.name.toLowerCase();
      if (/silver|chandi/i.test(catName)) {
        const silverPurity = purities.find((p) => /silver|925|chandi/i.test(p.name));
        if (silverPurity) {
          setPurityId(silverPurity.id);
          if (makingCharge === '450.00') setMakingCharge('15.00');
        }
      } else if (/platinum|\bpt\b/i.test(catName)) {
        const platPurity = purities.find((p) => /platinum|950/i.test(p.name));
        if (platPurity) setPurityId(platPurity.id);
      } else if (/gold/i.test(catName)) {
        const goldPurity = purities.find((p) => /22kt|916/i.test(p.name)) || purities[0];
        if (goldPurity) setPurityId(goldPurity.id);
      }
    }
  };

  const handleNameChange = (newName: string) => {
    setName(newName);
    if (/silver|payal|anklet/i.test(newName)) {
      const silverCat = categories.find((c) => /silver/i.test(c.name));
      const silverPurity = purities.find((p) => /silver|925|chandi/i.test(p.name));
      const curPurity = purities.find((p) => p.id === purityId);
      if (curPurity && !/silver|925|chandi/i.test(curPurity.name) && silverPurity) {
        setPurityId(silverPurity.id);
        if (silverCat) setCategoryId(silverCat.id);
        if (makingCharge === '450.00') setMakingCharge('15.00');
      }
    }
  };

  const selectedPurity = purities.find((p) => p.id === purityId);
  const selectedCat = categories.find((c) => c.id === categoryId);
  const isSilverItem = /silver|925|chandi|payal|anklet/i.test(`${selectedPurity?.name || ''} ${selectedCat?.name || ''} ${name}`);
  const isPlatItem = /platinum|950|\bpt\b/i.test(`${selectedPurity?.name || ''} ${selectedCat?.name || ''} ${name}`);
  const detectedMetalName = isSilverItem ? 'Silver' : isPlatItem ? 'Platinum' : 'Gold';

  useEffect(() => {
    if (categories.length > 0 && (!categoryId || !categories.some((c) => c.id === categoryId))) {
      setCategoryId(categories[0].id);
    }
    if (purities.length > 0 && (!purityId || !purities.some((p) => p.id === purityId))) {
      setPurityId(purities[0].id);
    }
  }, [categories, purities]);

  useEffect(() => {
    if (isOpen) {
      setName('');
      setSku('');
      setGrossWeight('');
      setStoneWeight('0.000');
      setOtherWeight('0.000');
      setMakingType('per_gram');
      setMakingCharge('450.00');
      setHuid('');
      setPhotoFile(null);
      setPhotoPreview(null);
      if (categories.length > 0) setCategoryId(categories[0].id);
      if (purities.length > 0) setPurityId(purities[0].id);
    }
  }, [isOpen]);

  const netWeight = (
    Math.max(
      0,
      (parseFloat(grossWeight) || 0) -
        (parseFloat(stoneWeight) || 0) -
        (parseFloat(otherWeight) || 0)
    )
  ).toFixed(3);

  const generateRandomSku = () => {
    const prefix = 'JW';
    const rand = Math.floor(100000 + Math.random() * 900000);
    setSku(`${prefix}-${rand}`);
  };

  const handlePhotoCapture = (file: File) => {
    setPhotoFile(file);
    setPhotoPreview(URL.createObjectURL(file));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !sku || !grossWeight) {
      toast.error('Please fill all mandatory fields (Name, SKU, Gross Weight)');
      return;
    }

    try {
      setIsSubmitting(true);
      const payload = {
        name: name.trim(),
        sku: sku.trim().toUpperCase(),
        category_id: Number(categoryId),
        purity_id: Number(purityId),
        gross_weight: grossWeight,
        stone_weight: stoneWeight || '0.000',
        other_weight: otherWeight || '0.000',
        making_charge_type: makingType,
        making_charge_value: makingCharge || '0.00',
        description: '',
        hsn_code: hsnCode,
        huid: huid.trim().toUpperCase(),
        initial_stock: 1,
      };

      const res = await api.post('/products/', payload);
      const createdProd = res.data;

      // If photo was captured or uploaded, attach it via photo upload endpoint
      if (photoFile && createdProd?.id) {
        try {
          const photoData = new FormData();
          photoData.append('photo', photoFile);
          await api.post(`/products/${createdProd.id}/upload-photo/`, photoData, {
            headers: { 'Content-Type': 'multipart/form-data' },
          });
        } catch {
          console.warn('Product created, but photo upload failed.');
        }
      }

      toast.success('Product created, QR Code generated & added to Item inventory!');
      onSuccess();
      onClose();
    } catch (err: any) {
      const serverErr = err.response?.data?.error || err.response?.data?.sku;
      const msg = serverErr
        ? String(serverErr)
        : 'Failed to create product. Please verify inputs.';
      toast.error(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <>
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 overflow-y-auto">
        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl my-8 overflow-hidden border border-slate-200">
          <div className="flex justify-between items-center px-6 py-4 border-b border-slate-100 bg-amber-500/10">
            <div>
              <h3 className="text-lg font-bold text-slate-800">Add Jewelry Product & Tag</h3>
              <p className="text-xs text-slate-500">
                Snap photo with camera, enter details → auto generates QR barcode tag
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-slate-600 p-1 rounded-full hover:bg-slate-200"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="p-6 space-y-5">
            {/* Camera / Photo Section */}
            <div className="flex items-center gap-4 p-4 rounded-xl bg-slate-50 border border-slate-200">
              <div className="w-24 h-24 rounded-xl bg-slate-200 border-2 border-dashed border-slate-300 flex items-center justify-center overflow-hidden shrink-0">
                {photoPreview ? (
                  <img
                    src={photoPreview}
                    alt="Preview"
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <Camera className="w-8 h-8 text-slate-400" />
                )}
              </div>
              <div className="flex-1">
                <h4 className="text-sm font-semibold text-slate-800">Product Photo</h4>
                <p className="text-xs text-slate-500 mb-3">
                  Capture from webcam / camera or upload an image for the tag
                </p>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => setIsCameraOpen(true)}
                    className="flex items-center gap-2 px-3.5 py-1.5 bg-amber-600 hover:bg-amber-700 text-white text-xs font-semibold rounded-lg shadow-sm transition"
                  >
                    <Camera className="w-3.5 h-3.5" />
                    <span>Open Camera</span>
                  </button>
                  {photoPreview && (
                    <button
                      type="button"
                      onClick={() => {
                        setPhotoFile(null);
                        setPhotoPreview(null);
                      }}
                      className="px-3 py-1.5 border border-slate-300 text-slate-600 hover:text-red-600 text-xs font-medium rounded-lg hover:bg-white transition"
                    >
                      Clear
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* Basic Info */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Product Name *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. 22KT Antique Bridal Choker or Silver Payal"
                  value={name}
                  onChange={(e) => handleNameChange(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                />
              </div>

              <div>
                <div className="flex justify-between items-center mb-1">
                  <label className="text-xs font-semibold text-slate-700">SKU / Item Code *</label>
                  <button
                    type="button"
                    onClick={generateRandomSku}
                    className="flex items-center gap-1 text-[11px] text-amber-700 hover:text-amber-800 font-medium"
                  >
                    <Sparkles className="w-3 h-3" /> Auto
                  </button>
                </div>
                <input
                  type="text"
                  required
                  placeholder="e.g. JW-982314"
                  value={sku}
                  onChange={(e) => setSku(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm font-mono focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                />
              </div>
            </div>

            {/* Category & Purity */}
            <div className="space-y-2">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Category *</label>
                  <select
                    value={categoryId}
                    onChange={(e) => handleCategoryChange(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                  >
                    {categories.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Purity *</label>
                  <select
                    value={purityId}
                    onChange={(e) => setPurityId(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                  >
                    {purities.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Dynamic Metal Classification Badge */}
              <div
                className={`px-3 py-1.5 rounded-lg text-xs font-medium flex items-center justify-between transition-colors ${
                  isSilverItem
                    ? 'bg-slate-100 text-slate-800 border border-slate-200'
                    : isPlatItem
                    ? 'bg-sky-50 text-sky-800 border border-sky-200'
                    : 'bg-amber-50 text-amber-900 border border-amber-200'
                }`}
              >
                <span>
                  Metal Classification: <b className="uppercase">{detectedMetalName}</b> ({selectedPurity?.name || 'Standard'})
                </span>
                <span className="text-[11px] opacity-80 font-mono">
                  Billed at {detectedMetalName} rate in POS
                </span>
              </div>
            </div>

            {/* Weights Breakdown (NUMERIC 3 decimals) */}
            <div className="p-4 bg-amber-50/50 rounded-xl border border-amber-200">
              <h4 className="text-xs font-bold text-amber-900 uppercase tracking-wider mb-3">
                Weights Breakdown (Grams)
              </h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div>
                  <label className="block text-[11px] font-semibold text-slate-600 mb-1">
                    Gross Wt (g) *
                  </label>
                  <input
                    type="number"
                    step="0.001"
                    min="0.001"
                    required
                    placeholder="0.000"
                    value={grossWeight}
                    onChange={(e) => setGrossWeight(e.target.value)}
                    className="w-full px-2.5 py-1.5 border border-slate-300 rounded-lg text-sm font-mono focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-slate-600 mb-1">
                    Stone Wt (g)
                  </label>
                  <input
                    type="number"
                    step="0.001"
                    min="0"
                    value={stoneWeight}
                    onChange={(e) => setStoneWeight(e.target.value)}
                    className="w-full px-2.5 py-1.5 border border-slate-300 rounded-lg text-sm font-mono focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-slate-600 mb-1">
                    Other Wt (g)
                  </label>
                  <input
                    type="number"
                    step="0.001"
                    min="0"
                    value={otherWeight}
                    onChange={(e) => setOtherWeight(e.target.value)}
                    className="w-full px-2.5 py-1.5 border border-slate-300 rounded-lg text-sm font-mono focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-bold text-emerald-800 mb-1">
                    Net Pure Wt (g)
                  </label>
                  <div className="px-2.5 py-1.5 bg-emerald-50 border border-emerald-300 rounded-lg text-sm font-mono font-bold text-emerald-700">
                    {netWeight} g
                  </div>
                </div>
              </div>
            </div>

            {/* Making Charges & Compliance */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Making Charge Type
                </label>
                <select
                  value={makingType}
                  onChange={(e: any) => setMakingType(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-amber-500"
                >
                  <option value="per_gram">Per Gram (₹)</option>
                  <option value="fixed">Fixed Lump-Sum (₹)</option>
                  <option value="percent">% of Gold Value</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Making Charge Value
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  value={makingCharge}
                  onChange={(e) => setMakingCharge(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm font-mono focus:ring-2 focus:ring-amber-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  HUID (Hallmark ID)
                </label>
                <input
                  type="text"
                  placeholder="e.g. 6-digit alphanum"
                  value={huid}
                  onChange={(e) => setHuid(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm uppercase font-mono focus:ring-2 focus:ring-amber-500"
                />
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-3 border-t border-slate-100">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 border border-slate-300 text-slate-700 rounded-xl text-sm font-medium hover:bg-slate-50 transition"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="flex items-center gap-2 px-6 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-xl text-sm font-bold shadow-md transition disabled:opacity-50"
              >
                <Check className="w-4 h-4" />
                <span>{isSubmitting ? 'Saving & Generating QR...' : 'Save & Generate QR'}</span>
              </button>
            </div>
          </form>
        </div>
      </div>

      <CameraCaptureModal
        isOpen={isCameraOpen}
        onClose={() => setIsCameraOpen(false)}
        onCapture={handlePhotoCapture}
      />
    </>
  );
};
