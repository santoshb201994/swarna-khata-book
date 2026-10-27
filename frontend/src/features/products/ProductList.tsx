import React, { useState, useEffect, useMemo } from 'react';
import {
  Plus,
  Search,
  QrCode,
  Tag,
  Sparkles,
  Table as TableIcon,
  LayoutGrid,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Download,
  Filter,
  RotateCcw,
} from 'lucide-react';
import api from '../../api/client';
import type { Product, Category, Purity } from '../../types';
import { ProductFormModal } from './ProductFormModal';
import { QRTagModal } from './QRTagModal';
import { useAuth } from '../../context/AuthContext';
import { canAccessFeature } from '../../utils/rbac';
import toast from 'react-hot-toast';

type SortField =
  | 'sku'
  | 'name'
  | 'category_name'
  | 'purity_name'
  | 'gross_weight'
  | 'net_weight'
  | 'stone_weight'
  | 'making_charge_value'
  | 'item_status'
  | 'created_at';

export const ProductList: React.FC = () => {
  const { user } = useAuth();
  const canAddProduct = canAccessFeature(user?.role, 'add_edit_products');

  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [purities, setPurities] = useState<Purity[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // View mode: Excel spreadsheet vs Photo Cards Grid
  const [viewMode, setViewMode] = useState<'excel' | 'grid'>('excel');

  // Excel filter states
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedPurity, setSelectedPurity] = useState<string>('');
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [minWeight, setMinWeight] = useState<string>('');
  const [maxWeight, setMaxWeight] = useState<string>('');

  // Sorting
  const [sortField, setSortField] = useState<SortField>('sku');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  // Modals
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [selectedProductForQR, setSelectedProductForQR] = useState<Product | null>(null);

  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    try {
      setIsLoading(true);
      const [prodRes, catRes, purRes] = await Promise.all([
        api.get('/products/'),
        api.get('/categories/'),
        api.get('/purities/'),
      ]);
      setProducts(prodRes.data.results || prodRes.data);
      setCategories(catRes.data.results || catRes.data);
      setPurities(purRes.data.results || purRes.data);
    } catch {
      toast.error('Failed to load products');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortOrder('asc');
    }
  };

  const resetFilters = () => {
    setSearch('');
    setSelectedCategory('');
    setSelectedPurity('');
    setSelectedStatus('');
    setMinWeight('');
    setMaxWeight('');
  };

  const activeFiltersCount = [
    search,
    selectedCategory,
    selectedPurity,
    selectedStatus,
    minWeight,
    maxWeight,
  ].filter(Boolean).length;

  // Filtered & Sorted products (Excel engine)
  const filteredProducts = useMemo(() => {
    const term = search.trim().toLowerCase();
    const minW = parseFloat(minWeight) || 0;
    const maxW = parseFloat(maxWeight) || Infinity;

    const list = products.filter((p) => {
      // 1. Text Search across SKU, Name, HUID, Category
      const matchesSearch =
        !term ||
        p.name.toLowerCase().includes(term) ||
        p.sku.toLowerCase().includes(term) ||
        (p.huid && p.huid.toLowerCase().includes(term)) ||
        (p.category_name && p.category_name.toLowerCase().includes(term));

      // 2. Category filter
      const matchesCategory = selectedCategory
        ? String(p.category || (p as any).category_id) === String(selectedCategory)
        : true;

      // 3. Purity filter
      const matchesPurity = selectedPurity
        ? String(p.purity || (p as any).purity_id) === String(selectedPurity)
        : true;

      // 4. Item Status filter (AVAILABLE, IN_CART, SOLD)
      const currentStatus = p.item_status || 'AVAILABLE';
      const matchesStatus = selectedStatus ? currentStatus === selectedStatus : true;

      // 5. Weight range filter
      const gross = parseFloat(p.gross_weight) || 0;
      const matchesWeight = gross >= minW && gross <= maxW;

      return matchesSearch && matchesCategory && matchesPurity && matchesStatus && matchesWeight;
    });

    // Sort
    return list.sort((a, b) => {
      let aVal: any = a[sortField as keyof Product] ?? '';
      let bVal: any = b[sortField as keyof Product] ?? '';

      // Numeric comparisons
      if (['gross_weight', 'net_weight', 'stone_weight', 'making_charge_value'].includes(sortField)) {
        aVal = parseFloat(aVal) || 0;
        bVal = parseFloat(bVal) || 0;
      } else {
        aVal = String(aVal).toLowerCase();
        bVal = String(bVal).toLowerCase();
      }

      if (aVal < bVal) return sortOrder === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });
  }, [
    products,
    search,
    selectedCategory,
    selectedPurity,
    selectedStatus,
    minWeight,
    maxWeight,
    sortField,
    sortOrder,
  ]);

  // Aggregated Excel Summary Metrics
  const summary = useMemo(() => {
    let totalGross = 0;
    let totalNet = 0;
    let availableCount = 0;

    for (const p of filteredProducts) {
      totalGross += parseFloat(p.gross_weight) || 0;
      totalNet += parseFloat(p.net_weight) || 0;
      if ((p.item_status || 'AVAILABLE') === 'AVAILABLE') {
        availableCount++;
      }
    }

    return {
      count: filteredProducts.length,
      totalGross: totalGross.toFixed(3),
      totalNet: totalNet.toFixed(3),
      availableCount,
    };
  }, [filteredProducts]);

  // Export to CSV / Excel spreadsheet
  const handleExportCSV = () => {
    if (filteredProducts.length === 0) {
      toast.error('No items to export.');
      return;
    }

    const headers = [
      'SKU',
      'Name',
      'Category',
      'Purity',
      'Gross Wt (g)',
      'Stone Wt (g)',
      'Net Wt (g)',
      'Making Charge Type',
      'Making Charge Value',
      'HUID',
      'Item Status',
      'Created Date',
    ];

    const rows = filteredProducts.map((p) => [
      `"${p.sku}"`,
      `"${p.name.replace(/"/g, '""')}"`,
      `"${p.category_name || ''}"`,
      `"${p.purity_name || ''}"`,
      p.gross_weight,
      p.stone_weight,
      p.net_weight,
      `"${p.making_charge_type || 'per_gram'}"`,
      p.making_charge_value,
      `"${p.huid || ''}"`,
      `"${p.item_status || 'AVAILABLE'}"`,
      `"${p.created_at ? new Date(p.created_at).toLocaleDateString() : ''}"`,
    ]);

    const csvContent =
      'data:text/csv;charset=utf-8,' +
      [headers.join(','), ...rows.map((e) => e.join(','))].join('\n');

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `swarna_jewellery_inventory_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.success('Inventory exported to CSV successfully!');
  };

  const handleOpenQRTag = async (prod: Product) => {
    try {
      const res = await api.get(`/products/${prod.id}/`);
      setSelectedProductForQR(res.data);
    } catch {
      setSelectedProductForQR(prod);
    }
  };

  const renderSortIcon = (field: SortField) => {
    if (sortField !== field) {
      return <ArrowUpDown className="w-3.5 h-3.5 text-slate-400 opacity-50 group-hover:opacity-100" />;
    }
    return sortOrder === 'asc' ? (
      <ArrowUp className="w-3.5 h-3.5 text-amber-600 font-bold" />
    ) : (
      <ArrowDown className="w-3.5 h-3.5 text-amber-600 font-bold" />
    );
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-5">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-black tracking-tight text-slate-900 flex items-center gap-2">
              <span>Inventory, Items & QR Tags</span>
            </h1>
            <span className="px-2.5 py-0.5 text-xs font-bold bg-amber-100 text-amber-900 rounded-full border border-amber-200">
              {filteredProducts.length} items
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Excel-style inventory grid, real-time item status, QR barcode tagging & camera snapshot
          </p>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          {/* View Mode Toggle */}
          <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200">
            <button
              onClick={() => setViewMode('excel')}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-lg transition ${
                viewMode === 'excel'
                  ? 'bg-white text-emerald-800 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
              title="Excel Spreadsheet View with multi-column filters"
            >
              <TableIcon className="w-4 h-4 text-emerald-600" />
              <span>Excel View</span>
            </button>
            <button
              onClick={() => setViewMode('grid')}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-lg transition ${
                viewMode === 'grid'
                  ? 'bg-white text-amber-800 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
              title="Card Photo Grid View"
            >
              <LayoutGrid className="w-4 h-4 text-amber-600" />
              <span>Grid View</span>
            </button>
          </div>

          {/* Export to CSV */}
          <button
            onClick={handleExportCSV}
            className="flex items-center gap-1.5 px-3.5 py-2 bg-emerald-50 hover:bg-emerald-100 text-emerald-800 text-xs font-bold rounded-xl border border-emerald-200 transition"
            title="Download current filtered data as Excel CSV"
          >
            <Download className="w-4 h-4 text-emerald-600" />
            <span>Export Excel</span>
          </button>

          {/* Add Product Button (Hierarchy Level 60+: Manager, Owner, Superadmin) */}
          {canAddProduct && (
            <button
              onClick={() => setIsAddModalOpen(true)}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-700 hover:to-amber-600 text-white text-xs font-bold rounded-xl shadow-sm transition active:scale-95"
            >
              <Plus className="w-4 h-4" />
              <span>Add Jewelry Item</span>
            </button>
          )}
        </div>
      </div>

      {/* Excel-Style Multi-Column Filter Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs space-y-3">
        <div className="flex items-center justify-between gap-2 border-b border-slate-100 pb-2">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-700">
            <Filter className="w-3.5 h-3.5 text-amber-600" />
            <span>Excel Filter Controls</span>
            {activeFiltersCount > 0 && (
              <span className="px-2 py-0.5 text-[10px] font-bold bg-amber-500 text-white rounded-full">
                {activeFiltersCount} active
              </span>
            )}
          </div>
          {activeFiltersCount > 0 && (
            <button
              onClick={resetFilters}
              className="flex items-center gap-1 text-xs text-rose-600 hover:text-rose-700 font-semibold transition"
            >
              <RotateCcw className="w-3 h-3" />
              <span>Reset Filters</span>
            </button>
          )}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2.5">
          {/* Quick Search */}
          <div className="relative lg:col-span-2">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search SKU, name, HUID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:bg-white focus:outline-hidden focus:ring-1 focus:ring-amber-500 font-medium"
            />
          </div>

          {/* Category Filter */}
          <div>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full px-2.5 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:bg-white focus:outline-hidden font-medium text-slate-700"
            >
              <option value="">All Categories</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          {/* Purity Filter */}
          <div>
            <select
              value={selectedPurity}
              onChange={(e) => setSelectedPurity(e.target.value)}
              className="w-full px-2.5 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:bg-white focus:outline-hidden font-medium text-slate-700"
            >
              <option value="">All Purities</option>
              {purities.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </div>

          {/* Item Status Filter */}
          <div>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="w-full px-2.5 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:bg-white focus:outline-hidden font-medium text-slate-700"
            >
              <option value="">All Statuses</option>
              <option value="AVAILABLE">Available (In Stock)</option>
              <option value="IN_CART">In Cart (POS Billing)</option>
              <option value="SOLD">Sold</option>
            </select>
          </div>

          {/* Weight Range Filter */}
          <div className="flex items-center gap-1">
            <input
              type="number"
              step="0.001"
              placeholder="Min g"
              value={minWeight}
              onChange={(e) => setMinWeight(e.target.value)}
              className="w-1/2 px-2 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:bg-white focus:outline-hidden text-center font-mono"
            />
            <span className="text-slate-400 text-xs">-</span>
            <input
              type="number"
              step="0.001"
              placeholder="Max g"
              value={maxWeight}
              onChange={(e) => setMaxWeight(e.target.value)}
              className="w-1/2 px-2 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:bg-white focus:outline-hidden text-center font-mono"
            />
          </div>
        </div>
      </div>

      {/* Main View Display */}
      {isLoading ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-16 text-center text-slate-400">
          <Sparkles className="w-8 h-8 text-amber-500 animate-spin mx-auto mb-2" />
          <p className="text-sm font-semibold">Loading jewellery inventory...</p>
        </div>
      ) : filteredProducts.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-2xl border border-dashed border-slate-200">
          <Tag className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-slate-700">No items matched your filters</h3>
          <p className="text-xs text-slate-400 mb-4">Try clearing filters or add a new jewellery product</p>
          <button
            onClick={resetFilters}
            className="inline-flex items-center gap-1.5 px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl transition"
          >
            <RotateCcw className="w-3.5 h-3.5" /> Reset Filters
          </button>
        </div>
      ) : viewMode === 'excel' ? (
        /* ======================================================================== */
        /* EXCEL SPREADSHEET TABLE VIEW                                             */
        /* ======================================================================== */
        <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden flex flex-col">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-100 border-b border-slate-200 text-slate-700 font-bold select-none">
                  <th className="py-2.5 px-3 text-center w-12 border-r border-slate-200/60">#</th>
                  <th
                    onClick={() => handleSort('sku')}
                    className="py-2.5 px-3 cursor-pointer hover:bg-slate-200/70 border-r border-slate-200/60 transition group"
                  >
                    <div className="flex items-center justify-between gap-1">
                      <span>SKU / Barcode</span>
                      {renderSortIcon('sku')}
                    </div>
                  </th>
                  <th
                    onClick={() => handleSort('name')}
                    className="py-2.5 px-3 cursor-pointer hover:bg-slate-200/70 border-r border-slate-200/60 transition group"
                  >
                    <div className="flex items-center justify-between gap-1">
                      <span>Product Name</span>
                      {renderSortIcon('name')}
                    </div>
                  </th>
                  <th
                    onClick={() => handleSort('category_name')}
                    className="py-2.5 px-3 cursor-pointer hover:bg-slate-200/70 border-r border-slate-200/60 transition group"
                  >
                    <div className="flex items-center justify-between gap-1">
                      <span>Category</span>
                      {renderSortIcon('category_name')}
                    </div>
                  </th>
                  <th
                    onClick={() => handleSort('purity_name')}
                    className="py-2.5 px-3 cursor-pointer hover:bg-slate-200/70 border-r border-slate-200/60 transition group"
                  >
                    <div className="flex items-center justify-between gap-1">
                      <span>Purity</span>
                      {renderSortIcon('purity_name')}
                    </div>
                  </th>
                  <th
                    onClick={() => handleSort('gross_weight')}
                    className="py-2.5 px-3 text-right cursor-pointer hover:bg-slate-200/70 border-r border-slate-200/60 transition group"
                  >
                    <div className="flex items-center justify-end gap-1">
                      <span>Gross Wt (g)</span>
                      {renderSortIcon('gross_weight')}
                    </div>
                  </th>
                  <th
                    onClick={() => handleSort('stone_weight')}
                    className="py-2.5 px-3 text-right cursor-pointer hover:bg-slate-200/70 border-r border-slate-200/60 transition group"
                  >
                    <div className="flex items-center justify-end gap-1">
                      <span>Stone (g)</span>
                      {renderSortIcon('stone_weight')}
                    </div>
                  </th>
                  <th
                    onClick={() => handleSort('net_weight')}
                    className="py-2.5 px-3 text-right cursor-pointer hover:bg-slate-200/70 border-r border-slate-200/60 transition group bg-emerald-50/60"
                  >
                    <div className="flex items-center justify-end gap-1 text-emerald-900">
                      <span>Net Pure (g)</span>
                      {renderSortIcon('net_weight')}
                    </div>
                  </th>
                  <th
                    onClick={() => handleSort('making_charge_value')}
                    className="py-2.5 px-3 text-right cursor-pointer hover:bg-slate-200/70 border-r border-slate-200/60 transition group"
                  >
                    <div className="flex items-center justify-end gap-1">
                      <span>Making (₹)</span>
                      {renderSortIcon('making_charge_value')}
                    </div>
                  </th>
                  <th className="py-2.5 px-3 border-r border-slate-200/60">HUID</th>
                  <th
                    onClick={() => handleSort('item_status')}
                    className="py-2.5 px-3 text-center cursor-pointer hover:bg-slate-200/70 border-r border-slate-200/60 transition group"
                  >
                    <div className="flex items-center justify-center gap-1">
                      <span>Item Status</span>
                      {renderSortIcon('item_status')}
                    </div>
                  </th>
                  <th className="py-2.5 px-3 text-center w-28">QR Tag</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-normal text-slate-800">
                {filteredProducts.map((p, idx) => {
                  const status = p.item_status || 'AVAILABLE';
                  return (
                    <tr
                      key={p.id}
                      className="hover:bg-amber-50/50 transition font-mono text-[11.5px] group"
                    >
                      {/* Row Index */}
                      <td className="py-2 px-3 text-center text-slate-400 font-sans border-r border-slate-100">
                        {idx + 1}
                      </td>

                      {/* SKU */}
                      <td className="py-2 px-3 font-bold text-slate-900 border-r border-slate-100">
                        <span className="bg-slate-100 px-1.5 py-0.5 rounded text-[11px] text-slate-800">
                          {p.sku}
                        </span>
                      </td>

                      {/* Name */}
                      <td className="py-2 px-3 font-sans font-semibold text-slate-800 max-w-[200px] truncate border-r border-slate-100">
                        <div className="flex items-center gap-2">
                          {p.photo_url ? (
                            <img
                              src={p.photo_url}
                              alt={p.name}
                              className="w-6 h-6 rounded object-cover border border-slate-200 shrink-0"
                            />
                          ) : (
                            <div className="w-6 h-6 rounded bg-slate-100 border border-slate-200 flex items-center justify-center text-[9px] text-slate-400 shrink-0">
                              💍
                            </div>
                          )}
                          <span className="truncate">{p.name}</span>
                        </div>
                      </td>

                      {/* Category */}
                      <td className="py-2 px-3 font-sans text-slate-600 border-r border-slate-100">
                        {p.category_name || '-'}
                      </td>

                      {/* Purity */}
                      <td className="py-2 px-3 border-r border-slate-100">
                        <span className="px-1.5 py-0.5 bg-amber-100 text-amber-900 font-bold rounded text-[10.5px]">
                          {p.purity_name || '22KT'}
                        </span>
                      </td>

                      {/* Gross Wt */}
                      <td className="py-2 px-3 text-right font-semibold text-slate-800 border-r border-slate-100">
                        {Number(p.gross_weight).toFixed(3)}
                      </td>

                      {/* Stone Wt */}
                      <td className="py-2 px-3 text-right text-slate-500 border-r border-slate-100">
                        {Number(p.stone_weight || 0).toFixed(3)}
                      </td>

                      {/* Net Wt */}
                      <td className="py-2 px-3 text-right font-bold text-emerald-700 bg-emerald-50/30 border-r border-slate-100">
                        {Number(p.net_weight).toFixed(3)}
                      </td>

                      {/* Making Charge */}
                      <td className="py-2 px-3 text-right text-slate-600 border-r border-slate-100">
                        ₹{Number(p.making_charge_value || 0).toFixed(2)}
                      </td>

                      {/* HUID */}
                      <td className="py-2 px-3 text-slate-500 font-sans border-r border-slate-100">
                        {p.huid || '-'}
                      </td>

                      {/* Item Status */}
                      <td className="py-2 px-3 text-center border-r border-slate-100">
                        {status === 'AVAILABLE' ? (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded-full text-[10px] font-bold font-sans">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                            Available
                          </span>
                        ) : status === 'IN_CART' ? (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-amber-100 text-amber-800 rounded-full text-[10px] font-bold font-sans">
                            <span className="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
                            In Cart
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-slate-100 text-slate-600 rounded-full text-[10px] font-bold font-sans">
                            <span className="w-1.5 h-1.5 rounded-full bg-slate-400"></span>
                            Sold
                          </span>
                        )}
                      </td>

                      {/* QR Tag Action */}
                      <td className="py-2 px-3 text-center">
                        <button
                          onClick={() => handleOpenQRTag(p)}
                          className="inline-flex items-center gap-1 px-2.5 py-1 bg-amber-50 hover:bg-amber-100 text-amber-800 rounded-md border border-amber-200 transition text-[11px] font-sans font-bold shadow-2xs"
                          title="Preview & Print Jewellery QR Tag"
                        >
                          <QrCode className="w-3.5 h-3.5 text-amber-600" />
                          <span>QR Tag</span>
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Excel Status Bar (Bottom Sheet summary) */}
          <div className="bg-slate-50 border-t border-slate-200 px-4 py-2.5 flex flex-wrap items-center justify-between text-xs text-slate-600 font-mono">
            <div className="flex items-center gap-4 flex-wrap">
              <span className="font-semibold text-slate-800">
                COUNT: <span className="text-amber-800 font-bold">{summary.count}</span>
              </span>
              <span>•</span>
              <span>
                SUM Gross Wt:{' '}
                <span className="text-slate-900 font-bold">{summary.totalGross}g</span>
              </span>
              <span>•</span>
              <span>
                SUM Net Pure Wt:{' '}
                <span className="text-emerald-700 font-bold">{summary.totalNet}g</span>
              </span>
              <span>•</span>
              <span>
                IN STOCK:{' '}
                <span className="text-emerald-600 font-bold">{summary.availableCount}</span>
              </span>
            </div>

            <div className="text-[11px] text-slate-400 font-sans">
              Click any column header to sort • Filter rows using the controls above
            </div>
          </div>
        </div>
      ) : (
        /* ======================================================================== */
        /* GRID / CARDS VIEW                                                        */
        /* ======================================================================== */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
          {filteredProducts.map((p) => {
            const status = p.item_status || 'AVAILABLE';
            return (
              <div
                key={p.id}
                className="group bg-white rounded-2xl border border-slate-200 shadow-xs hover:shadow-md transition overflow-hidden flex flex-col justify-between"
              >
                <div>
                  {/* Photo preview or placeholder */}
                  <div className="relative aspect-4/3 bg-slate-100 overflow-hidden flex items-center justify-center">
                    {p.photo_url ? (
                      <img
                        src={p.photo_url}
                        alt={p.name}
                        className="w-full h-full object-cover group-hover:scale-105 transition duration-300"
                      />
                    ) : (
                      <div className="flex flex-col items-center justify-center text-slate-300">
                        <Sparkles className="w-8 h-8 mb-1" />
                        <span className="text-[11px] font-medium">No Photo</span>
                      </div>
                    )}

                    {/* Purity badge */}
                    <span className="absolute top-2.5 right-2.5 px-2.5 py-1 bg-amber-950/80 backdrop-blur-xs text-amber-300 font-bold text-[11px] rounded-lg shadow-sm">
                      {p.purity_name || '22KT'}
                    </span>

                    {/* Status badge */}
                    <span
                      className={`absolute top-2.5 left-2.5 px-2 py-0.5 text-[10px] font-bold rounded-md shadow-xs ${
                        status === 'AVAILABLE'
                          ? 'bg-emerald-600 text-white'
                          : status === 'IN_CART'
                          ? 'bg-amber-500 text-white'
                          : 'bg-slate-700 text-white'
                      }`}
                    >
                      {status}
                    </span>
                  </div>

                  <div className="p-4 space-y-2">
                    <div className="flex justify-between items-start gap-2">
                      <h3 className="font-bold text-sm text-slate-900 line-clamp-1">{p.name}</h3>
                    </div>
                    <div className="flex items-center justify-between text-xs text-slate-500 font-mono">
                      <span className="bg-slate-100 px-2 py-0.5 rounded-md font-semibold text-slate-700">
                        {p.sku}
                      </span>
                      <span>{p.category_name}</span>
                    </div>

                    <div className="pt-2 grid grid-cols-2 gap-2 text-xs border-t border-slate-100">
                      <div>
                        <span className="text-[10px] text-slate-400 block uppercase font-medium">Gross Wt</span>
                        <span className="font-mono font-medium text-slate-700">
                          {Number(p.gross_weight).toFixed(3)}g
                        </span>
                      </div>
                      <div>
                        <span className="text-[10px] text-slate-400 block uppercase font-medium">Net Pure Wt</span>
                        <span className="font-mono font-bold text-emerald-700">
                          {Number(p.net_weight).toFixed(3)}g
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Action buttons */}
                <div className="p-4 pt-0">
                  <button
                    onClick={() => handleOpenQRTag(p)}
                    className="w-full flex items-center justify-center gap-2 py-2 bg-amber-50 hover:bg-amber-100 text-amber-800 text-xs font-bold rounded-xl border border-amber-200 transition"
                  >
                    <QrCode className="w-4 h-4 text-amber-600" />
                    <span>View / Print QR Tag</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Add Product Modal */}
      <ProductFormModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onSuccess={fetchInitialData}
        categories={categories}
        purities={purities}
      />

      {/* QR Tag Print Preview Modal */}
      <QRTagModal
        isOpen={!!selectedProductForQR}
        onClose={() => setSelectedProductForQR(null)}
        product={selectedProductForQR}
      />
    </div>
  );
};
