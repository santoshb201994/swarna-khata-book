import React, { useState, useEffect, useRef, useMemo } from 'react';
import QRCode from 'qrcode';
import api from '../../api/client';
import { downloadInvoicePdf } from '../../utils/invoiceDownload';
import type { Sale, InvoiceSetting } from '../../types';
import {
  Printer,
  Download,
  X,
  Sparkles,
  QrCode as QrIcon,
  ShieldCheck,
} from 'lucide-react';

interface InvoiceModalProps {
  isOpen: boolean;
  onClose: () => void;
  sale: Sale | null;
  customSettings?: InvoiceSetting | null;
}

export const InvoiceModal: React.FC<InvoiceModalProps> = ({
  isOpen,
  onClose,
  sale,
  customSettings,
}) => {
  const [storeSettings, setStoreSettings] = useState<InvoiceSetting | null>(null);

  useEffect(() => {
    if (isOpen && !customSettings && !sale?.invoice_setting) {
      api.get('/billing/invoice-settings/')
        .then((res) => {
          if (res.data) setStoreSettings(res.data);
        })
        .catch(() => {});
    }
  }, [isOpen, customSettings, sale?.invoice_setting]);

  // Determine effective invoice settings (from prop, sale snapshot, live store settings, or defaults)
  const settings: InvoiceSetting = useMemo(() => {
    return customSettings || sale?.invoice_setting || storeSettings || {
      id: 1,
      branch_id: 1,
      header_invocation: '|| ಶ್ರೀ ಶಾಂತೇರಿ ಪ್ರಸನ್ನ ||',
      shop_name_primary: 'Shree Balaji Abharan Angadi',
      shop_name_secondary: 'ಶ್ರೀ ಬಾಲಾಜಿ ಆಭರಣ ಅಂಗಡಿ',
      tagline: 'Gold & Silver Merchants',
      address_primary: 'Beside Mukkal Basaveshwar Temple, Old Shroff Bazar, GADAG-582101',
      address_secondary: 'ಮುಕ್ಕಾಲ ಬಸವೇಶ್ವರ ದೇವಸ್ಥಾನದ ಹತ್ತಿರ, ಹಳೇ ಸರಾಫ ಬಜಾರ, ಗದಗ-582101',
      phone_landline: '(08372) 238391',
      phone_mobile_1: '9449642640',
      phone_mobile_2: '7760755515',
      email: 'Ranjanbalaji93@gmail.com',
      website: '',
      gstin: '29ADNPP6515B1ZF',
      pan_number: 'ADNPP6515B',
      state_name: 'Karnataka',
      state_code: '29',
      bis_hallmark_licence: 'HM/C-7891234',
      logo_url: '',
      template_style: 'traditional_bilingual',
      default_paper_size: 'A4',
      show_invocation: true,
      show_bilingual_header: true,
      show_huid: true,
      show_purity: true,
      show_gross_net_weight: true,
      show_wastage: true,
      show_making_charge: true,
      show_stone_details: true,
      show_rate_per_gram: true,
      show_old_gold_section: true,
      show_upi_qr: true,
      show_bank_details: true,
      show_customer_address: true,
      show_hallmark_badge: true,
      bank_name: 'State Bank of India',
      account_name: 'Shree Balaji Abharan Angadi',
      account_number: '38291048591',
      ifsc_code: 'SBIN0000837',
      upi_id: '9449642640@sbi',
      terms_and_conditions:
        '1. Exchange with in 3 days, No Guarantee For Stone Falling & Brekage.\n2. Weight variation subject to +/- 10mg tolerance.\n3. Certified 916/750 Hallmark Jewellery conforms to Bureau of Indian Standards (BIS).\n4. Old Gold purchase/exchange value is calculated after melting assay & karat verification.\n5. Subject to Gadag jurisdiction only.',
      declaration:
        'Certified that the particulars given above are true and correct and price charged is legal.',
      signatory_title: 'For, Shree Balaji Abharan Angadi',
    };
  }, [customSettings, sale?.invoice_setting, storeSettings]);

  const [activeTemplate, setActiveTemplate] = useState<
    'traditional_bilingual' | 'modern_luxury' | 'royal_gold' | 'compact_thermal'
  >(() => settings.template_style || 'traditional_bilingual');
  const [paperSize, setPaperSize] = useState<'A4' | 'A5' | '80mm'>(
    () => settings.default_paper_size || 'A4'
  );
  const [upiQrDataUrl, setUpiQrDataUrl] = useState<string>('');
  const printAreaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (settings.template_style) {
      setActiveTemplate(settings.template_style);
    }
    if (settings.default_paper_size) {
      setPaperSize(settings.default_paper_size);
    }
  }, [settings.template_style, settings.default_paper_size]);

  // Generate UPI payment QR code string
  useEffect(() => {
    if (!sale || !settings.upi_id) return;
    const upiUri = `upi://pay?pa=${encodeURIComponent(settings.upi_id)}&pn=${encodeURIComponent(
      settings.shop_name_primary
    )}&am=${sale.total_amount}&cu=INR&tn=Invoice%20${encodeURIComponent(sale.invoice_number)}`;

    QRCode.toDataURL(upiUri, { width: 140, margin: 1, color: { dark: '#0f172a', light: '#ffffff' } })
      .then((url) => setUpiQrDataUrl(url))
      .catch((err) => console.error('QR generation error:', err));
  }, [sale, settings.upi_id, settings.shop_name_primary]);

  if (!isOpen || !sale) return null;

  const handlePrint = () => {
    window.print();
  };

  const handleDownloadPdf = async () => {
    if (!sale) return;
    await downloadInvoicePdf(sale.id, sale.invoice_number);
  };

  // Format currency
  const fmt = (val: string | number | undefined) => {
    const num = typeof val === 'string' ? parseFloat(val) : val || 0;
    return `₹${num.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  const parseNum = (val: string | number | undefined) => {
    return typeof val === 'string' ? parseFloat(val) || 0 : val || 0;
  };

  const saleDateFormatted = new Date(sale.sale_date).toLocaleDateString('en-IN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });

  // Calculate paper container dimensions
  const getPaperClasses = () => {
    if (paperSize === '80mm') return 'max-w-[340px] text-xs font-mono p-4 bg-white shadow-lg mx-auto';
    if (paperSize === 'A5') return 'max-w-[620px] text-xs p-6 bg-white shadow-xl mx-auto rounded-lg';
    return 'max-w-[820px] text-sm p-8 bg-white shadow-2xl mx-auto rounded-xl'; // A4
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/80 backdrop-blur-sm flex flex-col items-center justify-start py-6 px-3 print:p-0 print:bg-white print:static">
      {/* Top Action Toolbar (Hidden during Print) */}
      <div className="w-full max-w-4xl bg-slate-900 border border-slate-800 rounded-2xl p-4 mb-4 flex flex-wrap items-center justify-between gap-4 text-white shadow-2xl print:hidden">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-amber-500/20 text-amber-400 rounded-xl flex items-center justify-center font-black">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-black tracking-tight text-white flex items-center gap-2">
              <span>GST Tax Invoice #{sale.invoice_number}</span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/30">
                BIS 916
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              High-Precision Jewellery Bill • Direct Browser Print & PDF
            </p>
          </div>
        </div>

        {/* Template Selector Pills */}
        <div className="flex items-center gap-1.5 bg-slate-800/80 p-1 rounded-xl border border-slate-700 text-xs">
          <button
            onClick={() => setActiveTemplate('traditional_bilingual')}
            className={`px-3 py-1.5 rounded-lg font-bold transition ${
              activeTemplate === 'traditional_bilingual'
                ? 'bg-amber-600 text-white shadow'
                : 'text-slate-300 hover:text-white hover:bg-slate-700/50'
            }`}
            title="Traditional South Indian / Kannada Bilingual Layout"
          >
            Traditional Heritage
          </button>
          <button
            onClick={() => setActiveTemplate('modern_luxury')}
            className={`px-3 py-1.5 rounded-lg font-bold transition ${
              activeTemplate === 'modern_luxury'
                ? 'bg-amber-600 text-white shadow'
                : 'text-slate-300 hover:text-white hover:bg-slate-700/50'
            }`}
            title="Tanishq & BlueStone Style Minimalist High Contrast"
          >
            Modern Luxury
          </button>
          <button
            onClick={() => setActiveTemplate('royal_gold')}
            className={`px-3 py-1.5 rounded-lg font-bold transition ${
              activeTemplate === 'royal_gold'
                ? 'bg-amber-600 text-white shadow'
                : 'text-slate-300 hover:text-white hover:bg-slate-700/50'
            }`}
            title="Kalyan & Joyalukkas Gold-Bordered Layout"
          >
            Royal Heritage
          </button>
          <button
            onClick={() => {
              setActiveTemplate('compact_thermal');
              setPaperSize('80mm');
            }}
            className={`px-3 py-1.5 rounded-lg font-bold transition ${
              activeTemplate === 'compact_thermal'
                ? 'bg-amber-600 text-white shadow'
                : 'text-slate-300 hover:text-white hover:bg-slate-700/50'
            }`}
            title="80mm Thermal Receipt Printer Format"
          >
            80mm Thermal
          </button>
        </div>

        {/* Paper Size Selector */}
        <div className="flex items-center gap-1 bg-slate-800/80 p-1 rounded-xl border border-slate-700 text-xs font-bold">
          {(['A4', 'A5', '80mm'] as const).map((sz) => (
            <button
              key={sz}
              onClick={() => {
                setPaperSize(sz);
                if (sz === '80mm') setActiveTemplate('compact_thermal');
              }}
              className={`px-2.5 py-1 rounded-lg transition ${
                paperSize === sz ? 'bg-slate-600 text-white shadow' : 'text-slate-400 hover:text-white'
              }`}
            >
              {sz}
            </button>
          ))}
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={handlePrint}
            className="flex items-center gap-1.5 px-3.5 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 font-black rounded-xl text-xs transition shadow-md shadow-amber-500/20"
          >
            <Printer className="w-4 h-4" />
            <span>Print Bill</span>
          </button>
          <button
            onClick={handleDownloadPdf}
            className="flex items-center gap-1.5 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold rounded-xl text-xs transition border border-slate-700"
          >
            <Download className="w-4 h-4" />
            <span>PDF</span>
          </button>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-xl transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* =========================================================================
          PRINTABLE INVOICE DOCUMENT
          Surrounded with print CSS styling to isolate from surrounding browser
         ========================================================================= */}
      <div
        ref={printAreaRef}
        id="printable-invoice"
        className={`${getPaperClasses()} text-slate-900 border border-slate-200 print:border-none print:shadow-none print:p-0 print:w-full`}
      >
        {/* ===================================================================
            TEMPLATE 1: TRADITIONAL BILINGUAL (HERITAGE / SHREE BALAJI GADAG)
           =================================================================== */}
        {activeTemplate === 'traditional_bilingual' && (
          <div className="space-y-4">
            {/* Top Religious Invocation */}
            {settings.show_invocation && settings.header_invocation && (
              <div className="text-center font-serif text-sm sm:text-base font-bold text-amber-900 tracking-wider pb-1 border-b border-amber-200/70">
                {settings.header_invocation}
              </div>
            )}

            {/* Bilingual Shop Header */}
            <div className="text-center space-y-1">
              {/* Secondary/Kannada Script */}
              {settings.show_bilingual_header && settings.shop_name_secondary && (
                <div className="text-xl sm:text-2xl font-black text-amber-950 tracking-wide font-sans">
                  {settings.shop_name_secondary}
                </div>
              )}
              {/* Primary/English Script */}
              <div className="text-lg sm:text-xl font-black text-slate-900 tracking-tight uppercase">
                {settings.shop_name_primary}
              </div>

              {/* Tagline */}
              {settings.tagline && (
                <div className="text-[11px] font-bold text-amber-800 uppercase tracking-widest">
                  {settings.tagline}
                </div>
              )}

              {/* Bilingual Addresses */}
              {settings.show_bilingual_header && settings.address_secondary && (
                <div className="text-xs text-slate-700 font-medium">
                  {settings.address_secondary}
                </div>
              )}
              {settings.address_primary && (
                <div className="text-xs text-slate-600">
                  {settings.address_primary}
                </div>
              )}

              {/* Contact Information & GSTIN */}
              <div className="flex flex-wrap items-center justify-center gap-x-4 gap-y-1 text-xs font-semibold text-slate-700 pt-1">
                {settings.phone_landline && (
                  <span>Shop: <b>{settings.phone_landline}</b></span>
                )}
                {(settings.phone_mobile_1 || settings.phone_mobile_2) && (
                  <span>
                    Cell: <b>{[settings.phone_mobile_1, settings.phone_mobile_2].filter(Boolean).join(', ')}</b>
                  </span>
                )}
                {settings.email && <span>Email: {settings.email}</span>}
              </div>

              <div className="flex flex-wrap items-center justify-center gap-4 text-xs font-bold text-slate-800 pt-1">
                <span className="px-2.5 py-0.5 bg-amber-100/70 border border-amber-300 rounded text-amber-950">
                  GSTIN: {settings.gstin}
                </span>
                {settings.state_name && (
                  <span>State: {settings.state_name} ({settings.state_code})</span>
                )}
                {settings.show_hallmark_badge && (
                  <span className="flex items-center gap-1 text-emerald-800">
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                    <span>BIS Hallmark 916 / 750</span>
                  </span>
                )}
              </div>
            </div>

            {/* Bill Title & Metadata Bar */}
            <div className="border-y-2 border-slate-900 py-1.5 flex justify-between items-center text-xs font-bold bg-slate-50 px-2">
              <span className="uppercase tracking-wider text-slate-900 text-sm">
                TAX INVOICE / SALE BILL
              </span>
              <div className="flex items-center gap-4">
                <span>Bill No: <b className="text-slate-950 font-mono text-sm">{sale.invoice_number}</b></span>
                <span>Date: <b className="text-slate-950">{saleDateFormatted}</b></span>
              </div>
            </div>

            {/* Customer Details Box */}
            <div className="bg-slate-50/70 p-2.5 rounded border border-slate-200 text-xs flex justify-between items-start">
              <div>
                <span className="text-slate-500 uppercase text-[10px] font-bold block">Billed To</span>
                <span className="font-bold text-slate-900 text-sm">
                  {sale.customer_name || 'Walk-in Cash Customer'}
                </span>
                {settings.show_customer_address && sale.customer_address && (
                  <div className="text-slate-600 mt-0.5">{sale.customer_address}</div>
                )}
              </div>
              <div className="text-right">
                {sale.customer_phone && (
                  <div>Phone: <b>{sale.customer_phone}</b></div>
                )}
                {sale.customer_pan && (
                  <div>PAN: <b>{sale.customer_pan}</b></div>
                )}
                <div className="text-[11px] text-slate-500 mt-0.5">Place of Supply: {settings.state_name}</div>
              </div>
            </div>

            {/* Traditional Line Items Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse border border-slate-900 text-xs">
                <thead>
                  <tr className="bg-amber-950 text-white font-bold text-center">
                    <th className="border border-slate-700 py-1.5 px-2 w-10">Sl. No.</th>
                    <th className="border border-slate-700 py-1.5 px-2 text-left">Description</th>
                    {settings.show_purity && <th className="border border-slate-700 py-1.5 px-2">Purity</th>}
                    {settings.show_gross_net_weight && (
                      <th className="border border-slate-700 py-1.5 px-2">Sale Weight</th>
                    )}
                    {settings.show_wastage && <th className="border border-slate-700 py-1.5 px-2">Wastage</th>}
                    {settings.show_rate_per_gram && (
                      <th className="border border-slate-700 py-1.5 px-2">Rate / g</th>
                    )}
                    {settings.show_making_charge && (
                      <th className="border border-slate-700 py-1.5 px-2">Making / Stones</th>
                    )}
                    <th className="border border-slate-700 py-1.5 px-2 text-right">Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {sale.items && sale.items.length > 0 ? (
                    sale.items.map((item, idx) => (
                      <tr key={idx} className="border-b border-slate-300 font-medium hover:bg-slate-50">
                        <td className="border border-slate-400 py-1.5 px-2 text-center font-mono">{idx + 1}</td>
                        <td className="border border-slate-400 py-1.5 px-2">
                          <div className="font-bold text-slate-900">{item.product_name}</div>
                          <div className="text-[10px] text-slate-500 font-mono flex gap-2">
                            <span>SKU: {item.sku}</span>
                            {settings.show_huid && item.huid && (
                              <span className="font-bold text-amber-900">HUID: {item.huid}</span>
                            )}
                            {item.hsn_code && <span>HSN: {item.hsn_code}</span>}
                          </div>
                        </td>
                        {settings.show_purity && (
                          <td className="border border-slate-400 py-1.5 px-2 text-center font-bold text-amber-900">
                            {item.purity}
                          </td>
                        )}
                        {settings.show_gross_net_weight && (
                          <td className="border border-slate-400 py-1.5 px-2 text-center font-mono font-bold">
                            {item.net_weight}g
                            {parseNum(item.gross_weight) !== parseNum(item.net_weight) && (
                              <div className="text-[10px] text-slate-500 font-normal">
                                Gr: {item.gross_weight}g
                              </div>
                            )}
                          </td>
                        )}
                        {settings.show_wastage && (
                          <td className="border border-slate-400 py-1.5 px-2 text-center font-mono">
                            {parseNum(item.wastage_percent) > 0 ? `${item.wastage_percent}%` : '-'}
                          </td>
                        )}
                        {settings.show_rate_per_gram && (
                          <td className="border border-slate-400 py-1.5 px-2 text-center font-mono">
                            {fmt(item.gold_rate_per_gram)}
                          </td>
                        )}
                        {settings.show_making_charge && (
                          <td className="border border-slate-400 py-1.5 px-2 text-center font-mono">
                            {fmt(parseNum(item.making_charge) + parseNum(item.stone_charge))}
                          </td>
                        )}
                        <td className="border border-slate-400 py-1.5 px-2 text-right font-mono font-bold">
                          {fmt(item.total_price)}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={8} className="py-4 text-center text-slate-400 italic">
                        No line items billed.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {/* Old Gold / Exchange Deduction (If applicable) */}
            {settings.show_old_gold_section && parseNum(sale.old_gold_value) > 0 && (
              <div className="p-2 bg-amber-50/70 border border-amber-300 rounded text-xs flex justify-between items-center">
                <div>
                  <span className="font-bold text-amber-950">Old Gold Exchange Voucher Credited:</span>
                  <span className="text-[11px] text-slate-600 ml-2">Melting assay verified</span>
                </div>
                <div className="font-mono font-bold text-rose-700">
                  - {fmt(sale.old_gold_value)}
                </div>
              </div>
            )}

            {/* Calculations & GST Breakup Box */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 items-start pt-1">
              {/* Left Column: Bank Details & UPI QR Code */}
              <div className="space-y-3">
                {settings.show_upi_qr && upiQrDataUrl && (
                  <div className="flex items-center gap-3 p-2 bg-slate-50 border border-slate-200 rounded">
                    <img src={upiQrDataUrl} alt="UPI QR" className="w-20 h-20 border border-slate-300 rounded" />
                    <div className="text-[11px] text-slate-700 leading-tight">
                      <div className="font-bold text-slate-900 flex items-center gap-1">
                        <QrIcon className="w-3.5 h-3.5 text-amber-700" />
                        <span>Scan & Pay via UPI</span>
                      </div>
                      <div className="text-[10px] text-slate-500 font-mono mt-0.5">{settings.upi_id}</div>
                      <div className="text-[10px] text-amber-800 font-semibold mt-1">
                        Accepts GPay, PhonePe, Paytm, BHIM
                      </div>
                    </div>
                  </div>
                )}

                {settings.show_bank_details && settings.bank_name && (
                  <div className="text-[11px] text-slate-600 bg-slate-50/50 p-2 border border-slate-200 rounded">
                    <div className="font-bold text-slate-800">Bank Details for RTGS/NEFT:</div>
                    <div>Bank: <b>{settings.bank_name}</b></div>
                    <div>A/C Name: {settings.account_name}</div>
                    <div>A/C No: <b className="font-mono">{settings.account_number}</b> | IFSC: <b className="font-mono">{settings.ifsc_code}</b></div>
                  </div>
                )}
              </div>

              {/* Right Column: Financial Totals */}
              <div className="border border-slate-900 rounded overflow-hidden text-xs">
                <table className="w-full">
                  <tbody>
                    <tr className="border-b border-slate-200">
                      <td className="py-1 px-3 text-slate-700">Total Taxable Value</td>
                      <td className="py-1 px-3 text-right font-mono font-semibold">{fmt(sale.subtotal)}</td>
                    </tr>
                    {parseNum(sale.discount) > 0 && (
                      <tr className="border-b border-slate-200 text-rose-600">
                        <td className="py-1 px-3">Discount</td>
                        <td className="py-1 px-3 text-right font-mono">- {fmt(sale.discount)}</td>
                      </tr>
                    )}
                    <tr className="border-b border-slate-200">
                      <td className="py-1 px-3 text-slate-700">CGST (1.5%)</td>
                      <td className="py-1 px-3 text-right font-mono">{fmt(sale.cgst_amount)}</td>
                    </tr>
                    <tr className="border-b border-slate-200">
                      <td className="py-1 px-3 text-slate-700">SGST (1.5%)</td>
                      <td className="py-1 px-3 text-right font-mono">{fmt(sale.sgst_amount)}</td>
                    </tr>
                    {parseNum(sale.old_gold_value) > 0 && (
                      <tr className="border-b border-slate-200 text-rose-700">
                        <td className="py-1 px-3">Old Gold Exchange</td>
                        <td className="py-1 px-3 text-right font-mono">- {fmt(sale.old_gold_value)}</td>
                      </tr>
                    )}
                    <tr className="bg-amber-100/80 font-black text-slate-950 text-sm border-t-2 border-slate-900">
                      <td className="py-2 px-3 uppercase tracking-wider">GRAND TOTAL</td>
                      <td className="py-2 px-3 text-right font-mono text-base">{fmt(sale.total_amount)}</td>
                    </tr>
                    <tr className="border-t border-slate-200 bg-slate-50 text-[11px]">
                      <td className="py-1 px-3 text-slate-600">Amount Paid ({sale.payments?.[0]?.method || 'Cash'})</td>
                      <td className="py-1 px-3 text-right font-mono font-bold text-emerald-700">
                        {fmt(sale.amount_paid)}
                      </td>
                    </tr>
                    {parseNum(sale.balance_due) > 0 && (
                      <tr className="bg-rose-50 text-[11px] text-rose-800 font-bold">
                        <td className="py-1 px-3">Balance Due</td>
                        <td className="py-1 px-3 text-right font-mono">{fmt(sale.balance_due)}</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Terms & Conditions & Signatures */}
            <div className="pt-2 border-t border-slate-300 text-xs">
              <div className="font-bold text-slate-800 mb-1">Terms & Conditions:</div>
              <div className="text-[10px] text-slate-600 whitespace-pre-line leading-relaxed">
                {settings.terms_and_conditions}
              </div>

              {/* Signatures */}
              <div className="flex justify-between items-end pt-8 pb-2">
                <div className="text-center w-48 border-t border-slate-400 pt-1 text-[11px] font-semibold text-slate-700">
                  Customer Signature
                </div>
                <div className="text-center w-56 border-t border-slate-400 pt-1 text-[11px] font-bold text-slate-900">
                  <div>{settings.signatory_title || `For, ${settings.shop_name_primary}`}</div>
                  <div className="text-[9px] text-slate-500 font-normal uppercase tracking-wider mt-0.5">
                    Authorized Signatory
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ===================================================================
            TEMPLATE 2: MODERN LUXURY (TANISHQ & BLUESTONE STYLE)
           =================================================================== */}
        {activeTemplate === 'modern_luxury' && (
          <div className="space-y-5 font-sans">
            {/* Top Bar: Rule 46 CGST & Brand Header */}
            <div className="flex justify-between items-start border-b-2 border-slate-950 pb-4">
              <div>
                <div className="text-2xl font-black tracking-tight text-slate-950 uppercase">
                  {settings.shop_name_primary}
                </div>
                <div className="text-xs text-amber-700 font-bold uppercase tracking-widest mt-0.5">
                  Fine Jewellery • Haute Horlogerie
                </div>
                <div className="text-xs text-slate-600 mt-1 max-w-sm">
                  {settings.address_primary}
                </div>
                <div className="text-xs text-slate-600">
                  GSTIN: <b>{settings.gstin}</b> | CIN/PAN: <b>{settings.pan_number}</b>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm font-black text-slate-950 tracking-wider">TAX INVOICE</div>
                <div className="text-[10px] text-slate-500 font-medium">(See Rule 46 of CGST Rules, 2017)</div>
                <div className="mt-2 text-xs">
                  <div>Invoice #: <b className="font-mono text-slate-900">{sale.invoice_number}</b></div>
                  <div>Date: <b>{saleDateFormatted}</b></div>
                  <div className="text-emerald-700 font-bold mt-1">Place of Supply: {settings.state_name} (29)</div>
                </div>
              </div>
            </div>

            {/* Customer & Bullion Benchmark Info */}
            <div className="grid grid-cols-2 gap-4 text-xs bg-slate-50 p-3 rounded-lg border border-slate-200">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">Customer Info</span>
                <div className="font-bold text-slate-900 text-sm">{sale.customer_name || 'Counter Retail Buyer'}</div>
                {sale.customer_phone && <div>Phone: {sale.customer_phone}</div>}
                {sale.customer_address && <div className="text-slate-600">{sale.customer_address}</div>}
              </div>
              <div className="text-right border-l border-slate-200 pl-4">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">Today's Bullion Benchmark</span>
                <div className="font-bold text-slate-900">Gold 22KT: {fmt(sale.gold_rate_per_gram)} / gram</div>
                <div className="text-emerald-700 font-semibold flex items-center justify-end gap-1 mt-1">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                  <span>100% BIS Hallmarked with Laser HUID</span>
                </div>
              </div>
            </div>

            {/* Table */}
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b-2 border-slate-900 text-slate-900 font-black">
                  <th className="py-2 px-1">#</th>
                  <th className="py-2 px-2">Item Description & HUID</th>
                  <th className="py-2 px-2 text-center">HSN</th>
                  <th className="py-2 px-2 text-center">Purity</th>
                  <th className="py-2 px-2 text-right">Gross Wt</th>
                  <th className="py-2 px-2 text-right">Net Wt</th>
                  <th className="py-2 px-2 text-right">Rate / g</th>
                  <th className="py-2 px-2 text-right">Making</th>
                  <th className="py-2 px-2 text-right">Taxable Total</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 font-medium">
                {sale.items?.map((it, idx) => (
                  <tr key={idx}>
                    <td className="py-2 px-1 font-mono text-slate-500">{idx + 1}</td>
                    <td className="py-2 px-2">
                      <div className="font-bold text-slate-900">{it.product_name}</div>
                      <div className="text-[10px] text-amber-800 font-mono font-bold flex gap-2">
                        <span>HUID: {it.huid || 'HD916B29'}</span>
                        <span className="text-slate-500">SKU: {it.sku}</span>
                      </div>
                    </td>
                    <td className="py-2 px-2 text-center font-mono">{it.hsn_code || '7113'}</td>
                    <td className="py-2 px-2 text-center font-bold text-slate-800">{it.purity}</td>
                    <td className="py-2 px-2 text-right font-mono">{it.gross_weight}g</td>
                    <td className="py-2 px-2 text-right font-mono font-bold">{it.net_weight}g</td>
                    <td className="py-2 px-2 text-right font-mono">{fmt(it.gold_rate_per_gram)}</td>
                    <td className="py-2 px-2 text-right font-mono">{fmt(it.making_charge)}</td>
                    <td className="py-2 px-2 text-right font-mono font-bold">{fmt(it.total_price)}</td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Totals & Tax Box */}
            <div className="grid grid-cols-2 gap-4 border-t-2 border-slate-900 pt-3 text-xs">
              <div>
                <div className="font-bold text-slate-800 mb-1">GST Tax Summary (HSN 7113):</div>
                <table className="w-full text-[11px] border border-slate-200">
                  <thead className="bg-slate-100 font-bold">
                    <tr>
                      <th className="p-1 border-r">Tax</th>
                      <th className="p-1 border-r">Rate</th>
                      <th className="p-1 text-right">Amount</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-t">
                      <td className="p-1 border-r">CGST</td>
                      <td className="p-1 border-r">1.5%</td>
                      <td className="p-1 text-right font-mono">{fmt(sale.cgst_amount)}</td>
                    </tr>
                    <tr className="border-t">
                      <td className="p-1 border-r">SGST</td>
                      <td className="p-1 border-r">1.5%</td>
                      <td className="p-1 text-right font-mono">{fmt(sale.sgst_amount)}</td>
                    </tr>
                  </tbody>
                </table>

                {settings.show_upi_qr && upiQrDataUrl && (
                  <div className="mt-3 flex items-center gap-3">
                    <img src={upiQrDataUrl} alt="UPI QR" className="w-16 h-16 border rounded" />
                    <div className="text-[10px] text-slate-600">
                      <div className="font-bold text-slate-900">Tata Pay / UPI Instant Checkout</div>
                      <div>Scan to pay {fmt(sale.total_amount)}</div>
                    </div>
                  </div>
                )}
              </div>

              <div className="space-y-1 text-right font-mono">
                <div className="flex justify-between py-1 border-b text-slate-600">
                  <span>Subtotal Value:</span>
                  <span>{fmt(sale.subtotal)}</span>
                </div>
                {parseNum(sale.discount) > 0 && (
                  <div className="flex justify-between py-1 border-b text-rose-600">
                    <span>Discount:</span>
                    <span>- {fmt(sale.discount)}</span>
                  </div>
                )}
                <div className="flex justify-between py-1 border-b text-slate-600">
                  <span>Total GST (3.0%):</span>
                  <span>{fmt(parseNum(sale.cgst_amount) + parseNum(sale.sgst_amount))}</span>
                </div>
                {parseNum(sale.old_gold_value) > 0 && (
                  <div className="flex justify-between py-1 border-b text-rose-600">
                    <span>Old Gold Exchange:</span>
                    <span>- {fmt(sale.old_gold_value)}</span>
                  </div>
                )}
                <div className="flex justify-between py-2 border-b-2 border-slate-900 text-slate-950 font-black text-sm">
                  <span>FINAL NET AMOUNT:</span>
                  <span className="text-base">{fmt(sale.total_amount)}</span>
                </div>
                <div className="text-[11px] text-slate-500 pt-1">
                  Payment Mode: <b>{sale.payments?.[0]?.method?.toUpperCase() || 'CASH'}</b>
                </div>
              </div>
            </div>

            {/* Declaration & Signatures */}
            <div className="pt-4 border-t border-slate-200 text-xs">
              <div className="text-[10px] text-slate-500 leading-normal">
                {settings.declaration} Hallmark verified via BIS Care App.
              </div>
              <div className="flex justify-between items-end pt-8">
                <div className="text-center w-40 border-t border-slate-300 pt-1 text-[11px]">
                  Customer Signature
                </div>
                <div className="text-center w-52 border-t border-slate-300 pt-1 text-[11px] font-bold">
                  <div>{settings.signatory_title}</div>
                  <div className="text-[9px] text-slate-400 font-normal">Authorized Signatory</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ===================================================================
            TEMPLATE 3: ROYAL HERITAGE (KALYAN & JOYALUKKAS STYLE)
           =================================================================== */}
        {activeTemplate === 'royal_gold' && (
          <div className="border-4 border-amber-800 p-4 rounded-lg space-y-4 font-serif">
            <div className="border-2 border-amber-600 p-4 rounded space-y-3">
              {/* Royal Seal & Name */}
              <div className="text-center space-y-1">
                {settings.header_invocation && (
                  <div className="text-xs font-bold text-amber-900 tracking-widest uppercase">
                    {settings.header_invocation}
                  </div>
                )}
                <div className="text-2xl font-black text-amber-950 tracking-wide uppercase">
                  {settings.shop_name_primary}
                </div>
                {settings.shop_name_secondary && (
                  <div className="text-lg font-bold text-amber-900 font-sans">
                    {settings.shop_name_secondary}
                  </div>
                )}
                <div className="text-xs text-amber-900 italic">
                  {settings.address_primary}
                </div>
                <div className="text-xs font-sans text-slate-700">
                  GSTIN: <b>{settings.gstin}</b> | Phone: <b>{settings.phone_landline || settings.phone_mobile_1}</b>
                </div>
              </div>

              {/* Gold Ribbon Banner */}
              <div className="bg-gradient-to-r from-amber-800 via-amber-600 to-amber-800 text-white text-center py-1 font-sans font-bold text-xs uppercase tracking-widest rounded">
                Royal Jewellery Tax Invoice • BIS 916 Hallmark Guaranteed
              </div>

              {/* Bill & Customer Metadata */}
              <div className="flex justify-between items-center text-xs font-sans border-b border-amber-300 pb-2">
                <div>
                  <div>Customer: <b>{sale.customer_name || 'Valued Patron'}</b></div>
                  {sale.customer_phone && <div>Contact: {sale.customer_phone}</div>}
                </div>
                <div className="text-right">
                  <div>Invoice No: <b className="font-mono text-amber-950">{sale.invoice_number}</b></div>
                  <div>Date: <b>{saleDateFormatted}</b></div>
                </div>
              </div>

              {/* Royal Table */}
              <table className="w-full text-left font-sans text-xs border border-amber-300">
                <thead className="bg-amber-100 text-amber-950 font-bold">
                  <tr>
                    <th className="p-2 border border-amber-300">#</th>
                    <th className="p-2 border border-amber-300">Ornaments</th>
                    <th className="p-2 border border-amber-300 text-center">Purity</th>
                    <th className="p-2 border border-amber-300 text-right">Gross Wt</th>
                    <th className="p-2 border border-amber-300 text-right">Net Wt</th>
                    <th className="p-2 border border-amber-300 text-right">Rate/g</th>
                    <th className="p-2 border border-amber-300 text-right">VA / Making</th>
                    <th className="p-2 border border-amber-300 text-right">Total</th>
                  </tr>
                </thead>
                <tbody>
                  {sale.items?.map((it, idx) => (
                    <tr key={idx} className="border-b border-amber-200">
                      <td className="p-2 border border-amber-200 text-center">{idx + 1}</td>
                      <td className="p-2 border border-amber-200">
                        <div className="font-bold text-slate-900">{it.product_name}</div>
                        <div className="text-[10px] text-amber-800 font-mono">HUID: {it.huid || 'HD916B29'}</div>
                      </td>
                      <td className="p-2 border border-amber-200 text-center font-bold text-amber-900">{it.purity}</td>
                      <td className="p-2 border border-amber-200 text-right font-mono">{it.gross_weight}g</td>
                      <td className="p-2 border border-amber-200 text-right font-mono font-bold">{it.net_weight}g</td>
                      <td className="p-2 border border-amber-200 text-right font-mono">{fmt(it.gold_rate_per_gram)}</td>
                      <td className="p-2 border border-amber-200 text-right font-mono">{fmt(it.making_charge)}</td>
                      <td className="p-2 border border-amber-200 text-right font-mono font-bold">{fmt(it.total_price)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {/* Old Gold Voucher Block */}
              {parseNum(sale.old_gold_value) > 0 && (
                <div className="bg-amber-50 border border-amber-300 p-2 rounded text-xs font-sans flex justify-between items-center">
                  <div>
                    <span className="font-bold text-amber-950">Old Gold Exchange Voucher Credited:</span>
                    <span className="text-slate-600 text-[11px] ml-2">Lifetime Exchange Guarantee</span>
                  </div>
                  <div className="font-mono font-bold text-rose-700">- {fmt(sale.old_gold_value)}</div>
                </div>
              )}

              {/* Total Calculation */}
              <div className="flex justify-between items-start font-sans text-xs pt-2">
                <div className="max-w-xs space-y-2">
                  <div className="text-[10px] text-slate-600 whitespace-pre-line leading-relaxed">
                    {settings.terms_and_conditions}
                  </div>
                  {settings.show_upi_qr && upiQrDataUrl && (
                    <div className="flex items-center gap-2 pt-1">
                      <img src={upiQrDataUrl} alt="UPI" className="w-16 h-16 border rounded" />
                      <div className="text-[10px] text-slate-700">
                        <span className="font-bold">Scan to Pay:</span> {settings.upi_id}
                      </div>
                    </div>
                  )}
                </div>

                <div className="w-64 border border-amber-300 rounded font-mono text-xs">
                  <div className="flex justify-between p-1.5 border-b border-amber-200">
                    <span>Taxable Metal Value:</span>
                    <span>{fmt(sale.subtotal)}</span>
                  </div>
                  <div className="flex justify-between p-1.5 border-b border-amber-200">
                    <span>CGST (1.5%):</span>
                    <span>{fmt(sale.cgst_amount)}</span>
                  </div>
                  <div className="flex justify-between p-1.5 border-b border-amber-200">
                    <span>SGST (1.5%):</span>
                    <span>{fmt(sale.sgst_amount)}</span>
                  </div>
                  <div className="flex justify-between p-2 bg-amber-100 font-bold text-sm text-amber-950">
                    <span>GRAND PAYABLE:</span>
                    <span>{fmt(sale.total_amount)}</span>
                  </div>
                </div>
              </div>

              {/* Signatures */}
              <div className="flex justify-between items-end pt-6 font-sans text-xs">
                <div className="text-center w-40 border-t border-amber-400 pt-1 text-[11px]">
                  Customer Signature
                </div>
                <div className="text-center w-52 border-t border-amber-400 pt-1 text-[11px] font-bold text-amber-950">
                  <div>{settings.signatory_title}</div>
                  <div className="text-[9px] text-slate-500 font-normal">Authorized Signatory</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ===================================================================
            TEMPLATE 4: COMPACT THERMAL RECEIPT (80MM POS ROLL)
           =================================================================== */}
        {activeTemplate === 'compact_thermal' && (
          <div className="space-y-3 font-mono text-slate-950">
            <div className="text-center space-y-0.5">
              {settings.header_invocation && (
                <div className="text-[11px] font-bold">{settings.header_invocation}</div>
              )}
              <div className="text-sm font-black uppercase">{settings.shop_name_primary}</div>
              {settings.shop_name_secondary && (
                <div className="text-xs font-bold font-sans">{settings.shop_name_secondary}</div>
              )}
              <div className="text-[10px] text-slate-600">{settings.address_primary}</div>
              <div className="text-[10px]">Ph: {settings.phone_landline || settings.phone_mobile_1}</div>
              <div className="text-[10px] font-bold">GSTIN: {settings.gstin}</div>
            </div>

            <div className="border-t border-dashed border-slate-400 my-2"></div>

            <div className="text-[11px] flex justify-between">
              <span>Bill: #{sale.invoice_number}</span>
              <span>{new Date(sale.sale_date).toLocaleDateString()}</span>
            </div>
            <div className="text-[11px]">
              Customer: <b>{sale.customer_name || 'Cash Customer'}</b>
            </div>

            <div className="border-t border-dashed border-slate-400 my-2"></div>

            {/* Thermal Line Items */}
            <div className="space-y-2 text-[11px]">
              {sale.items?.map((it, idx) => (
                <div key={idx} className="border-b border-dotted border-slate-300 pb-1">
                  <div className="flex justify-between font-bold">
                    <span>{idx + 1}. {it.product_name}</span>
                    <span>{fmt(it.total_price)}</span>
                  </div>
                  <div className="flex justify-between text-[10px] text-slate-600">
                    <span>{it.purity} | Net: {it.net_weight}g</span>
                    <span>Rate: {fmt(it.gold_rate_per_gram)}/g</span>
                  </div>
                  {it.huid && (
                    <div className="text-[9px] text-amber-900 font-bold">HUID: {it.huid}</div>
                  )}
                </div>
              ))}
            </div>

            <div className="border-t border-dashed border-slate-400 my-2"></div>

            {/* Thermal Totals */}
            <div className="space-y-1 text-[11px]">
              <div className="flex justify-between">
                <span>Subtotal:</span>
                <span>{fmt(sale.subtotal)}</span>
              </div>
              {parseNum(sale.discount) > 0 && (
                <div className="flex justify-between">
                  <span>Discount:</span>
                  <span>- {fmt(sale.discount)}</span>
                </div>
              )}
              <div className="flex justify-between">
                <span>CGST (1.5%):</span>
                <span>{fmt(sale.cgst_amount)}</span>
              </div>
              <div className="flex justify-between">
                <span>SGST (1.5%):</span>
                <span>{fmt(sale.sgst_amount)}</span>
              </div>
              {parseNum(sale.old_gold_value) > 0 && (
                <div className="flex justify-between font-bold">
                  <span>Old Gold Exchange:</span>
                  <span>- {fmt(sale.old_gold_value)}</span>
                </div>
              )}
              <div className="border-t-2 border-slate-900 pt-1 flex justify-between font-black text-sm">
                <span>TOTAL PAYABLE:</span>
                <span>{fmt(sale.total_amount)}</span>
              </div>
              <div className="flex justify-between text-[10px] text-slate-600">
                <span>Paid ({sale.payments?.[0]?.method || 'Cash'}):</span>
                <span>{fmt(sale.amount_paid)}</span>
              </div>
            </div>

            {settings.show_upi_qr && upiQrDataUrl && (
              <div className="text-center pt-2 flex flex-col items-center">
                <img src={upiQrDataUrl} alt="UPI QR" className="w-24 h-24 border mx-auto" />
                <div className="text-[9px] mt-1 font-bold">Scan to Pay via UPI</div>
              </div>
            )}

            <div className="border-t border-dashed border-slate-400 my-2"></div>

            <div className="text-center text-[9px] space-y-1 text-slate-600">
              <div>Exchange within 3 days with bill.</div>
              <div>No guarantee for stone falling & breakage.</div>
              <div className="font-bold text-slate-900">Thank you! Visit again.</div>
            </div>
          </div>
        )}
      </div>

      {/* Dynamic @page sizing for selected paper format */}
      <style>{`
        @media print {
          @page {
            size: ${paperSize === 'A5' ? 'A5 landscape' : paperSize === '80mm' ? '80mm auto' : 'A4 portrait'};
            margin: ${paperSize === '80mm' ? '2mm' : '6mm'};
          }
        }
      `}</style>
    </div>
  );
};
