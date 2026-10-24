import React, { useState, useEffect } from 'react';
import {
  Wallet,
  ArrowUpRight,
  ArrowDownLeft,
  Calendar,
  Lock,
  Coins,
  FileText,
  Printer,
  Globe,
  RefreshCw,
} from 'lucide-react';
import api from '../../api/client';
import type { DayBook, Sale, GoldRate } from '../../types';
import toast from 'react-hot-toast';

interface RateSource {
  id: string;
  name: string;
  url: string;
  description: string;
  is_default: boolean;
}

export const AccountingDashboard: React.FC = () => {
  const [dayBook, setDayBook] = useState<DayBook | null>(null);
  const [sales, setSales] = useState<Sale[]>([]);
  const [goldRates, setGoldRates] = useState<GoldRate[]>([]);

  // Rate Scraper Dropdown & Web Sync
  const [rateSources, setRateSources] = useState<RateSource[]>([]);
  const [selectedSource, setSelectedSource] = useState<string>('ksjf');
  const [isSyncingRates, setIsSyncingRates] = useState<boolean>(false);

  // New gold rate entry
  const [selectedPurityId, setSelectedPurityId] = useState<number>(1);
  const [newRateValue, setNewRateValue] = useState<string>('');

  // Cash In / Cash Out entry
  const [cashDeltaType, setCashDeltaType] = useState<'in' | 'out'>('in');
  const [cashDeltaAmount, setCashDeltaAmount] = useState<string>('');
  const [cashDeltaNotes, setCashDeltaNotes] = useState<string>('');

  useEffect(() => {
    fetchAccountingData();
  }, []);

  const fetchAccountingData = async () => {
    try {
      const [dayRes, salesRes, ratesRes, sourcesRes] = await Promise.all([
        api.get('/day-book/today/'),
        api.get('/sales/'),
        api.get('/gold-rates/current/'),
        api.get('/gold-rates/sources/').catch(() => ({ data: [] })),
      ]);
      setDayBook(dayRes.data);
      setSales(salesRes.data.results || salesRes.data);
      setGoldRates(ratesRes.data.results || ratesRes.data);

      if (sourcesRes.data && sourcesRes.data.length > 0) {
        setRateSources(sourcesRes.data);
        const defaultSource = sourcesRes.data.find((s: RateSource) => s.is_default);
        if (defaultSource) {
          setSelectedSource(defaultSource.id);
        }
      }
    } catch {
      toast.error('Failed to load accounting data');
    }
  };

  const handleSyncRatesFromWeb = async () => {
    if (!selectedSource) return;
    setIsSyncingRates(true);
    try {
      const res = await api.post('/gold-rates/sync/', { source: selectedSource });
      toast.success(res.data.message || 'Rates updated from website successfully!');
      fetchAccountingData();
    } catch (err: any) {
      const errText = err.response?.data?.error || 'Failed to scrape rates from selected website';
      toast.error(errText);
    } finally {
      setIsSyncingRates(false);
    }
  };

  const handleCloseDay = async () => {
    if (!dayBook) return;
    if (dayBook.is_closed) {
      toast.error('Day is already closed');
      return;
    }
    if (!confirm('Are you sure you want to close the business day? This finalizes the closing cash balance.')) return;

    try {
      const res = await api.post(`/day-book/${dayBook.id}/close_day/`);
      setDayBook(res.data);
      toast.success('Business day successfully closed and audited!');
    } catch {
      toast.error('Failed to close business day');
    }
  };

  const handleUpdateGoldRate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newRateValue) return;

    try {
      const today = new Date().toISOString().split('T')[0];
      await api.post('/gold-rates/', {
        purity: selectedPurityId,
        rate_per_gram: newRateValue,
        effective_date: today,
        is_current: true,
      });
      toast.success('Live metal rate updated across shop!');
      setNewRateValue('');
      fetchAccountingData();
    } catch {
      toast.error('Failed to update gold rate');
    }
  };

  const handleAddDayBookCash = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!dayBook || !cashDeltaAmount) return;

    try {
      const amt = parseFloat(cashDeltaAmount);
      const currentIn = parseFloat(dayBook.cash_in);
      const currentOut = parseFloat(dayBook.cash_out);

      const updateData =
        cashDeltaType === 'in'
          ? { cash_in: (currentIn + amt).toFixed(2) }
          : { cash_out: (currentOut + amt).toFixed(2) };

      const res = await api.patch(`/day-book/${dayBook.id}/`, updateData);
      setDayBook(res.data);
      toast.success(`Recorded ₹${amt} ${cashDeltaType === 'in' ? 'Cash In' : 'Cash Out'}`);
      setCashDeltaAmount('');
      setCashDeltaNotes('');
    } catch {
      toast.error('Failed to update Day Book');
    }
  };

  const currentRates = goldRates.filter((r) => r.is_current);

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
            <span>Accounting & Day Book</span>
            <span
              className={`px-2.5 py-0.5 text-xs font-semibold rounded-full ${
                dayBook?.is_closed
                  ? 'bg-rose-100 text-rose-800'
                  : 'bg-emerald-100 text-emerald-800'
              }`}
            >
              {dayBook?.is_closed ? 'Day Closed' : 'Day Open'}
            </span>
          </h1>
          <p className="text-sm text-slate-500">
            Cash register audit, live bullion rates, day-close summary, and invoice ledgers
          </p>
        </div>

        {dayBook && !dayBook.is_closed && (
          <button
            onClick={handleCloseDay}
            className="flex items-center gap-2 px-5 py-2.5 bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs rounded-xl shadow-md transition"
          >
            <Lock className="w-4 h-4" />
            <span>Close Business Day</span>
          </button>
        )}
      </div>

      {/* Day Book Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
          <div className="flex justify-between items-center text-slate-400 mb-2">
            <span className="text-xs font-bold uppercase tracking-wider">Opening Balance</span>
            <Calendar className="w-4 h-4 text-slate-400" />
          </div>
          <div className="text-2xl font-black font-mono text-slate-800">
            ₹{parseFloat(dayBook?.opening_balance || '0').toLocaleString('en-IN')}
          </div>
          <div className="text-[11px] text-slate-400 mt-1">Starting cash today</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
          <div className="flex justify-between items-center text-emerald-600 mb-2">
            <span className="text-xs font-bold uppercase tracking-wider">Cash In (Sales)</span>
            <ArrowDownLeft className="w-4 h-4" />
          </div>
          <div className="text-2xl font-black font-mono text-emerald-600">
            +₹{parseFloat(dayBook?.cash_in || '0').toLocaleString('en-IN')}
          </div>
          <div className="text-[11px] text-slate-400 mt-1">Cash receipts & sales</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
          <div className="flex justify-between items-center text-rose-600 mb-2">
            <span className="text-xs font-bold uppercase tracking-wider">Cash Out (Expense)</span>
            <ArrowUpRight className="w-4 h-4" />
          </div>
          <div className="text-2xl font-black font-mono text-rose-600">
            -₹{parseFloat(dayBook?.cash_out || '0').toLocaleString('en-IN')}
          </div>
          <div className="text-[11px] text-slate-400 mt-1">Old gold buyback & payouts</div>
        </div>

        <div className="bg-gradient-to-br from-amber-600 to-amber-700 text-white p-5 rounded-2xl shadow-md">
          <div className="flex justify-between items-center text-amber-200 mb-2">
            <span className="text-xs font-bold uppercase tracking-wider">Current Drawer Cash</span>
            <Wallet className="w-4 h-4" />
          </div>
          <div className="text-2xl font-black font-mono">
            ₹
            {(
              (parseFloat(dayBook?.opening_balance || '0') +
                parseFloat(dayBook?.cash_in || '0') -
                parseFloat(dayBook?.cash_out || '0'))
            ).toLocaleString('en-IN')}
          </div>
          <div className="text-[11px] text-amber-200 mt-1">Net physical cash on hand</div>
        </div>
      </div>

      {/* Middle Row: Gold Rates Manager & Record Cash Entry */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Live Metal Rates Card */}
        <div className="lg:col-span-6 bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs space-y-4">
          <div className="flex flex-wrap justify-between items-center pb-3 border-b border-slate-100 gap-2">
            <h3 className="font-bold text-base text-slate-800 flex items-center gap-2">
              <Coins className="w-5 h-5 text-amber-500" />
              <span>Today's Metal Rates (₹/gram)</span>
            </h3>

            {/* Bullion Rate Source Web Scraper Dropdown & Sync Button */}
            <div className="flex items-center gap-2">
              <div className="relative flex items-center">
                <Globe className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 pointer-events-none" />
                <select
                  value={selectedSource}
                  onChange={(e) => setSelectedSource(e.target.value)}
                  className="text-xs bg-slate-50 border border-slate-200 rounded-lg pl-7 pr-3 py-1.5 font-medium text-slate-700 hover:bg-slate-100 focus:bg-white focus:outline-hidden transition-all cursor-pointer"
                  title="Select trade association or benchmark website to scrape live rates"
                >
                  {rateSources.map((src) => (
                    <option key={src.id} value={src.id}>
                      {src.name}
                    </option>
                  ))}
                </select>
              </div>

              <button
                type="button"
                onClick={handleSyncRatesFromWeb}
                disabled={isSyncingRates}
                className="text-xs px-3 py-1.5 bg-amber-500 hover:bg-amber-600 text-white font-bold rounded-lg flex items-center gap-1.5 transition-all shadow-xs cursor-pointer disabled:opacity-50"
                title="Scrape and automatically update live metal rates from this website"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${isSyncingRates ? 'animate-spin' : ''}`} />
                <span>{isSyncingRates ? 'Syncing...' : 'Auto-Sync'}</span>
              </button>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {currentRates.map((r) => (
              <div
                key={r.id}
                className="p-3 bg-amber-50/60 border border-amber-200 rounded-xl flex flex-col justify-between"
              >
                <span className="text-xs font-bold text-amber-900">{r.purity_name}</span>
                <span className="text-lg font-black font-mono text-slate-900 mt-1">
                  ₹{parseFloat(r.rate_per_gram).toLocaleString('en-IN')}
                </span>
                <span className="text-[10px] text-slate-400 mt-0.5">per gram</span>
              </div>
            ))}
          </div>

          {/* Quick Rate Updater Form */}
          <form
            onSubmit={handleUpdateGoldRate}
            className="pt-2 border-t border-slate-100 flex items-center gap-2"
          >
            <select
              value={selectedPurityId}
              onChange={(e) => setSelectedPurityId(Number(e.target.value))}
              className="text-xs px-2.5 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:bg-white focus:outline-hidden"
            >
              {currentRates.map((r) => (
                <option key={r.purity} value={r.purity}>
                  {r.purity_name}
                </option>
              ))}
            </select>

            <input
              type="number"
              step="1"
              required
              placeholder="New rate (₹/g)..."
              value={newRateValue}
              onChange={(e) => setNewRateValue(e.target.value)}
              className="flex-1 text-xs px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg font-mono focus:bg-white focus:outline-hidden"
            />

            <button
              type="submit"
              className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold rounded-lg transition"
            >
              Update Rate
            </button>
          </form>
        </div>

        {/* Quick Cash Entry Form */}
        <div className="lg:col-span-6 bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs space-y-4">
          <div className="flex justify-between items-center pb-3 border-b border-slate-100">
            <h3 className="font-bold text-base text-slate-800 flex items-center gap-2">
              <Wallet className="w-5 h-5 text-emerald-600" />
              <span>Record Cash Drawer In / Out</span>
            </h3>
          </div>

          <form onSubmit={handleAddDayBookCash} className="space-y-3">
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setCashDeltaType('in')}
                className={`py-2 text-xs font-bold rounded-xl border transition ${
                  cashDeltaType === 'in'
                    ? 'bg-emerald-600 text-white border-emerald-600'
                    : 'bg-slate-50 text-slate-600 border-slate-200'
                }`}
              >
                + Cash In (Receipt)
              </button>
              <button
                type="button"
                onClick={() => setCashDeltaType('out')}
                className={`py-2 text-xs font-bold rounded-xl border transition ${
                  cashDeltaType === 'out'
                    ? 'bg-rose-600 text-white border-rose-600'
                    : 'bg-slate-50 text-slate-600 border-slate-200'
                }`}
              >
                - Cash Out (Expense)
              </button>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <input
                type="number"
                step="1"
                required
                placeholder="Amount (₹)..."
                value={cashDeltaAmount}
                onChange={(e) => setCashDeltaAmount(e.target.value)}
                className="px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg font-mono focus:bg-white"
              />
              <input
                type="text"
                placeholder="Reason / Notes..."
                value={cashDeltaNotes}
                onChange={(e) => setCashDeltaNotes(e.target.value)}
                className="px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:bg-white"
              />
            </div>

            <button
              type="submit"
              className="w-full py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold rounded-xl transition"
            >
              Record in Day Book
            </button>
          </form>
        </div>
      </div>

      {/* Recent Sales Ledger Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100 flex justify-between items-center">
          <h3 className="font-bold text-base text-slate-800 flex items-center gap-2">
            <FileText className="w-4 h-4 text-amber-600" />
            <span>Sales & Tax Invoice Ledger</span>
          </h3>
          <span className="text-xs text-slate-400 font-mono">{sales.length} transactions</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 uppercase font-semibold">
              <tr>
                <th className="px-5 py-3">Invoice #</th>
                <th className="px-5 py-3">Date</th>
                <th className="px-5 py-3">Customer</th>
                <th className="px-5 py-3">Amount</th>
                <th className="px-5 py-3">Status</th>
                <th className="px-5 py-3 text-right">PDF Invoice</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {sales.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-8 text-slate-400">
                    No sales recorded yet. Use the POS Billing screen to bill items.
                  </td>
                </tr>
              ) : (
                sales.map((sale) => (
                  <tr key={sale.id} className="hover:bg-slate-50/60 transition">
                    <td className="px-5 py-3 font-mono font-bold text-slate-900">
                      {sale.invoice_number}
                    </td>
                    <td className="px-5 py-3 text-slate-500 font-mono">
                      {new Date(sale.sale_date).toLocaleDateString('en-IN', {
                        day: '2-digit',
                        month: 'short',
                        year: 'numeric',
                      })}
                    </td>
                    <td className="px-5 py-3 font-medium text-slate-800">
                      {sale.customer_name || 'Walk-in'}
                    </td>
                    <td className="px-5 py-3 font-mono font-bold text-slate-900">
                      ₹{parseFloat(sale.total_amount).toLocaleString('en-IN')}
                    </td>
                    <td className="px-5 py-3">
                      <span
                        className={`px-2 py-0.5 rounded-full font-semibold uppercase text-[10px] ${
                          sale.payment_status === 'paid'
                            ? 'bg-emerald-100 text-emerald-800'
                            : 'bg-amber-100 text-amber-800'
                        }`}
                      >
                        {sale.payment_status}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-right">
                      <a
                        href={`/api/sales/${sale.id}/invoice_pdf/`}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 px-2.5 py-1 bg-amber-50 hover:bg-amber-100 text-amber-800 font-bold rounded-lg border border-amber-200 transition"
                      >
                        <Printer className="w-3 h-3 text-amber-600" />
                        <span>PDF</span>
                      </a>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
