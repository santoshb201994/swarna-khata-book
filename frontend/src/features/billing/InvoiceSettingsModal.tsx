import React, { useState, useEffect } from 'react';
import api from '../../api/client';
import type { InvoiceSetting } from '../../types';
import {
  X,
  Sparkles,
  Save,
  RotateCcw,
  Building2,
  Sliders,
  CreditCard,
  FileText,
  Check,
  QrCode,
} from 'lucide-react';
import toast from 'react-hot-toast';

interface InvoiceSettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSettingsUpdated?: (newSettings: InvoiceSetting) => void;
}

export const InvoiceSettingsModal: React.FC<InvoiceSettingsModalProps> = ({
  isOpen,
  onClose,
  onSettingsUpdated,
}) => {
  const [activeTab, setActiveTab] = useState<'identity' | 'layout' | 'bank' | 'terms'>('identity');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [formData, setFormData] = useState<InvoiceSetting>({
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
  });

  const fetchSettings = async () => {
    try {
      setIsLoading(true);
      const res = await api.get('/billing/invoice-settings/');
      if (res.data) {
        setFormData(res.data);
      }
    } catch (err: any) {
      console.warn('Could not fetch remote invoice settings, using defaults.', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchSettings();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleChange = (field: keyof InvoiceSetting, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSave = async () => {
    try {
      setIsSaving(true);
      const res = await api.put('/billing/invoice-settings/', formData);
      toast.success('Invoice settings & branding saved successfully!');
      if (onSettingsUpdated) {
        onSettingsUpdated(res.data);
      }
      onClose();
    } catch (err: any) {
      toast.error('Failed to save invoice settings. Check permissions.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleResetDemo = async () => {
    if (!window.confirm('Reset all invoice settings to Shree Balaji Abharan Angadi (Gadag) default?')) {
      return;
    }
    try {
      setIsSaving(true);
      const res = await api.post('/billing/invoice-settings/reset-demo/');
      setFormData(res.data);
      toast.success('Reset to Shree Balaji Abharan Angadi (Gadag) profile!');
      if (onSettingsUpdated) {
        onSettingsUpdated(res.data);
      }
    } catch (err: any) {
      toast.error('Failed to reset demo invoice settings.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-xs p-4 overflow-y-auto">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-5xl my-8 overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-slate-900 text-white">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-amber-500/20 text-amber-400 rounded-xl flex items-center justify-center font-black">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-black tracking-tight text-white flex items-center gap-2">
                <span>Invoice Customization & Branding Studio</span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-400 font-bold border border-amber-500/30">
                  Owner Control
                </span>
              </h2>
              <p className="text-xs text-slate-400">
                Configure your store header, Kannada/English scripts, GSTIN, columns, terms, and print formats
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-xl transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-slate-200 bg-slate-50 px-6 overflow-x-auto">
          <button
            onClick={() => setActiveTab('identity')}
            className={`flex items-center gap-2 py-3 px-4 text-xs font-bold border-b-2 transition ${
              activeTab === 'identity'
                ? 'border-amber-600 text-amber-900 bg-white'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <Building2 className="w-4 h-4 text-amber-700" />
            <span>Store Identity & Header</span>
          </button>
          <button
            onClick={() => setActiveTab('layout')}
            className={`flex items-center gap-2 py-3 px-4 text-xs font-bold border-b-2 transition ${
              activeTab === 'layout'
                ? 'border-amber-600 text-amber-900 bg-white'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <Sliders className="w-4 h-4 text-amber-700" />
            <span>Styles & Column Toggles</span>
          </button>
          <button
            onClick={() => setActiveTab('bank')}
            className={`flex items-center gap-2 py-3 px-4 text-xs font-bold border-b-2 transition ${
              activeTab === 'bank'
                ? 'border-amber-600 text-amber-900 bg-white'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <CreditCard className="w-4 h-4 text-amber-700" />
            <span>Bank & Dynamic UPI QR</span>
          </button>
          <button
            onClick={() => setActiveTab('terms')}
            className={`flex items-center gap-2 py-3 px-4 text-xs font-bold border-b-2 transition ${
              activeTab === 'terms'
                ? 'border-amber-600 text-amber-900 bg-white'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <FileText className="w-4 h-4 text-amber-700" />
            <span>Terms, Policies & Signature</span>
          </button>
        </div>

        {/* Content Area */}
        <div className="p-6 overflow-y-auto flex-1 space-y-6">
          {isLoading ? (
            <div className="text-center py-12 text-slate-400">Loading shop profile...</div>
          ) : (
            <>
              {/* TAB 1: STORE IDENTITY & HEADER */}
              {activeTab === 'identity' && (
                <div className="space-y-4">
                  <div className="p-3 bg-amber-50/60 border border-amber-200 rounded-xl text-xs text-amber-900">
                    <b>Traditional Bilingual Identity:</b> Supports religious invocations, primary (English) and secondary regional script (e.g. Kannada: ಶ್ರೀ ಬಾಲಾಜಿ ಆಭರಣ ಅಂಗಡಿ), landlines, and dual cell phone lines.
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">
                        Top Religious Invocation
                      </label>
                      <input
                        type="text"
                        value={formData.header_invocation}
                        onChange={(e) => handleChange('header_invocation', e.target.value)}
                        placeholder="e.g. || ಶ್ರೀ ಶಾಂತೇರಿ ಪ್ರಸನ್ನ ||"
                        className="w-full px-3 py-2 border border-slate-300 rounded-xl text-xs focus:ring-2 focus:ring-amber-500 focus:outline-hidden font-serif"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">
                        Store Tagline / Subtitle
                      </label>
                      <input
                        type="text"
                        value={formData.tagline}
                        onChange={(e) => handleChange('tagline', e.target.value)}
                        placeholder="e.g. Gold & Silver Merchants"
                        className="w-full px-3 py-2 border border-slate-300 rounded-xl text-xs focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">
                        Shop Name (Primary / English) *
                      </label>
                      <input
                        type="text"
                        value={formData.shop_name_primary}
                        onChange={(e) => handleChange('shop_name_primary', e.target.value)}
                        placeholder="e.g. Shree Balaji Abharan Angadi"
                        className="w-full px-3 py-2 border border-slate-300 rounded-xl text-xs font-bold focus:ring-2 focus:ring-amber-500 focus:outline-hidden uppercase"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">
                        Shop Name (Secondary / Kannada Script)
                      </label>
                      <input
                        type="text"
                        value={formData.shop_name_secondary}
                        onChange={(e) => handleChange('shop_name_secondary', e.target.value)}
                        placeholder="e.g. ಶ್ರೀ ಬಾಲಾಜಿ ಆಭರಣ ಅಂಗಡಿ"
                        className="w-full px-3 py-2 border border-slate-300 rounded-xl text-xs font-bold focus:ring-2 focus:ring-amber-500 focus:outline-hidden text-amber-950"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">
                        Address (Primary / English) *
                      </label>
                      <textarea
                        rows={2}
                        value={formData.address_primary}
                        onChange={(e) => handleChange('address_primary', e.target.value)}
                        placeholder="Beside Mukkal Basaveshwar Temple, Old Shroff Bazar, GADAG-582101"
                        className="w-full px-3 py-2 border border-slate-300 rounded-xl text-xs focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">
                        Address (Secondary / Kannada Script)
                      </label>
                      <textarea
                        rows={2}
                        value={formData.address_secondary}
                        onChange={(e) => handleChange('address_secondary', e.target.value)}
                        placeholder="ಮುಕ್ಕಾಲ ಬಸವೇಶ್ವರ ದೇವಸ್ಥಾನದ ಹತ್ತಿರ, ಹಳೇ ಸರಾಫ ಬಜಾರ, ಗದಗ-582101"
                        className="w-full px-3 py-2 border border-slate-300 rounded-xl text-xs focus:ring-2 focus:ring-amber-500 focus:outline-hidden text-amber-950"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">
                        Landline Shop Phone
                      </label>
                      <input
                        type="text"
                        value={formData.phone_landline}
                        onChange={(e) => handleChange('phone_landline', e.target.value)}
                        placeholder="e.g. (08372) 238391"
                        className="w-full px-3 py-2 border border-slate-300 rounded-xl text-xs focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">
                        Primary Cell Phone
                      </label>
                      <input
                        type="text"
                        value={formData.phone_mobile_1}
                        onChange={(e) => handleChange('phone_mobile_1', e.target.value)}
                        placeholder="e.g. 9449642640"
                        className="w-full px-3 py-2 border border-slate-300 rounded-xl text-xs focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">
                        Secondary Cell Phone
                      </label>
                      <input
                        type="text"
                        value={formData.phone_mobile_2}
                        onChange={(e) => handleChange('phone_mobile_2', e.target.value)}
                        placeholder="e.g. 7760755515"
                        className="w-full px-3 py-2 border border-slate-300 rounded-xl text-xs focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">
                        GSTIN Number *
                      </label>
                      <input
                        type="text"
                        value={formData.gstin}
                        onChange={(e) => handleChange('gstin', e.target.value)}
                        placeholder="e.g. 29ADNPP6515B1ZF"
                        className="w-full px-3 py-2 border border-slate-300 rounded-xl text-xs font-mono font-bold focus:ring-2 focus:ring-amber-500 focus:outline-hidden uppercase"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">
                        Store Email
                      </label>
                      <input
                        type="email"
                        value={formData.email}
                        onChange={(e) => handleChange('email', e.target.value)}
                        placeholder="e.g. Ranjanbalaji93@gmail.com"
                        className="w-full px-3 py-2 border border-slate-300 rounded-xl text-xs focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">
                        State & State Code
                      </label>
                      <div className="flex gap-2">
                        <input
                          type="text"
                          value={formData.state_name}
                          onChange={(e) => handleChange('state_name', e.target.value)}
                          placeholder="Karnataka"
                          className="w-2/3 px-3 py-2 border border-slate-300 rounded-xl text-xs focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                        />
                        <input
                          type="text"
                          value={formData.state_code}
                          onChange={(e) => handleChange('state_code', e.target.value)}
                          placeholder="29"
                          className="w-1/3 px-3 py-2 border border-slate-300 rounded-xl text-xs font-mono focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 2: STYLES & COLUMN TOGGLES */}
              {activeTab === 'layout' && (
                <div className="space-y-6">
                  {/* Template Style Selector */}
                  <div>
                    <label className="block text-xs font-bold text-slate-800 mb-2">
                      Default Template Style
                    </label>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                      {[
                        {
                          id: 'traditional_bilingual',
                          title: 'Traditional Heritage',
                          desc: 'Shree Balaji (Gadag) style with Kannada invocation, bilingual headers, and merchant grid.',
                        },
                        {
                          id: 'modern_luxury',
                          title: 'Modern Luxury',
                          desc: 'Tanishq & BlueStone style with corporate clean lines, HUID badges, and dynamic UPI QR.',
                        },
                        {
                          id: 'royal_gold',
                          title: 'Royal Heritage',
                          desc: 'Kalyan & Joyalukkas style with gold-embossed borders and dedicated Old Gold Exchange slip.',
                        },
                        {
                          id: 'compact_thermal',
                          title: '80mm POS Thermal',
                          desc: 'High-density narrow thermal roll receipt for fast counter slip printers.',
                        },
                      ].map((t) => (
                        <div
                          key={t.id}
                          onClick={() => handleChange('template_style', t.id)}
                          className={`cursor-pointer p-4 rounded-xl border-2 transition ${
                            formData.template_style === t.id
                              ? 'border-amber-600 bg-amber-50/70 shadow-sm'
                              : 'border-slate-200 hover:border-slate-300 bg-white'
                          }`}
                        >
                          <div className="flex items-center justify-between mb-1">
                            <span className="font-bold text-xs text-slate-900">{t.title}</span>
                            {formData.template_style === t.id && (
                              <Check className="w-4 h-4 text-amber-600" />
                            )}
                          </div>
                          <p className="text-[11px] text-slate-500 leading-tight">{t.desc}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Paper Format */}
                  <div>
                    <label className="block text-xs font-bold text-slate-800 mb-2">
                      Default Paper Format
                    </label>
                    <div className="flex gap-4">
                      {(['A4', 'A5', '80mm'] as const).map((sz) => (
                        <label key={sz} className="flex items-center gap-2 cursor-pointer text-xs font-bold text-slate-700">
                          <input
                            type="radio"
                            name="default_paper_size"
                            value={sz}
                            checked={formData.default_paper_size === sz}
                            onChange={() => handleChange('default_paper_size', sz)}
                            className="text-amber-600 focus:ring-amber-500"
                          />
                          <span>{sz === 'A4' ? 'A4 Full Page' : sz === 'A5' ? 'A5 Half Page' : '80mm Thermal Slip'}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Column Visibility Switches */}
                  <div>
                    <label className="block text-xs font-bold text-slate-800 mb-2">
                      Invoice Column & Section Visibility Toggles
                    </label>
                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 bg-slate-50 p-4 rounded-xl border border-slate-200">
                      {[
                        { key: 'show_invocation', label: 'Religious Invocation (ಶ್ರೀ ಶಾಂತೇರಿ ಪ್ರಸನ್ನ)' },
                        { key: 'show_bilingual_header', label: 'Bilingual Kannada Name & Address' },
                        { key: 'show_huid', label: 'Laser HUID Code Column' },
                        { key: 'show_purity', label: 'Purity Fineness (22KT 916)' },
                        { key: 'show_gross_net_weight', label: 'Gross & Net Weight Columns' },
                        { key: 'show_wastage', label: 'Wastage (VA %) Column' },
                        { key: 'show_rate_per_gram', label: 'Daily Rate per Gram Column' },
                        { key: 'show_making_charge', label: 'Making Charges Column' },
                        { key: 'show_old_gold_section', label: 'Old Gold Exchange Voucher Section' },
                        { key: 'show_upi_qr', label: 'Dynamic UPI Payment QR Code' },
                        { key: 'show_bank_details', label: 'Bank Account & IFSC Box' },
                        { key: 'show_hallmark_badge', label: 'BIS Hallmark 916 Emblem' },
                      ].map((toggle) => (
                        <label key={toggle.key} className="flex items-center gap-2.5 cursor-pointer text-xs text-slate-700 font-medium select-none">
                          <input
                            type="checkbox"
                            checked={!!formData[toggle.key as keyof InvoiceSetting]}
                            onChange={(e) => handleChange(toggle.key as keyof InvoiceSetting, e.target.checked)}
                            className="rounded border-slate-300 text-amber-600 focus:ring-amber-500 w-4 h-4"
                          />
                          <span>{toggle.label}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 3: BANK & DYNAMIC UPI QR */}
              {activeTab === 'bank' && (
                <div className="space-y-4">
                  <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-900 flex items-center gap-2">
                    <QrCode className="w-4 h-4 text-emerald-700" />
                    <span>
                      <b>Scan-to-Pay UPI Integration:</b> Entering your UPI VPA automatically prints a scannable payment QR code on the invoice with the exact bill amount.
                    </span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">
                        Merchant UPI ID (VPA) *
                      </label>
                      <input
                        type="text"
                        value={formData.upi_id}
                        onChange={(e) => handleChange('upi_id', e.target.value)}
                        placeholder="e.g. 9449642640@sbi"
                        className="w-full px-3 py-2 border border-slate-300 rounded-xl text-xs font-mono font-bold focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                      />
                      <span className="text-[10px] text-slate-400 mt-0.5 block">
                        Linked to Google Pay, PhonePe, Paytm, BHIM, and Banking UPI apps.
                      </span>
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">
                        Bank Name
                      </label>
                      <input
                        type="text"
                        value={formData.bank_name}
                        onChange={(e) => handleChange('bank_name', e.target.value)}
                        placeholder="e.g. State Bank of India"
                        className="w-full px-3 py-2 border border-slate-300 rounded-xl text-xs focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">
                        Account Holder Name
                      </label>
                      <input
                        type="text"
                        value={formData.account_name}
                        onChange={(e) => handleChange('account_name', e.target.value)}
                        placeholder="e.g. Shree Balaji Abharan Angadi"
                        className="w-full px-3 py-2 border border-slate-300 rounded-xl text-xs focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">
                        Bank Account Number
                      </label>
                      <input
                        type="text"
                        value={formData.account_number}
                        onChange={(e) => handleChange('account_number', e.target.value)}
                        placeholder="e.g. 38291048591"
                        className="w-full px-3 py-2 border border-slate-300 rounded-xl text-xs font-mono focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">
                        IFSC Code
                      </label>
                      <input
                        type="text"
                        value={formData.ifsc_code}
                        onChange={(e) => handleChange('ifsc_code', e.target.value)}
                        placeholder="e.g. SBIN0000837"
                        className="w-full px-3 py-2 border border-slate-300 rounded-xl text-xs font-mono uppercase focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 4: TERMS, POLICIES & SIGNATURE */}
              {activeTab === 'terms' && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      Terms & Conditions (Printed at Footer of Bill)
                    </label>
                    <textarea
                      rows={5}
                      value={formData.terms_and_conditions}
                      onChange={(e) => handleChange('terms_and_conditions', e.target.value)}
                      placeholder="1. Exchange with in 3 days, No Guarantee For Stone Falling & Brekage..."
                      className="w-full px-3 py-2 border border-slate-300 rounded-xl text-xs font-mono focus:ring-2 focus:ring-amber-500 focus:outline-hidden leading-relaxed"
                    />
                    <div className="flex gap-2 mt-1">
                      <button
                        type="button"
                        onClick={() =>
                          handleChange(
                            'terms_and_conditions',
                            '1. Exchange with in 3 days, No Guarantee For Stone Falling & Brekage.\n2. Weight variation subject to +/- 10mg tolerance.\n3. Certified 916/750 Hallmark Jewellery conforms to Bureau of Indian Standards (BIS).\n4. Old Gold purchase/exchange value is calculated after melting assay & karat verification.\n5. Subject to Gadag jurisdiction only.'
                          )
                        }
                        className="text-[11px] text-amber-700 font-bold hover:underline"
                      >
                        [Insert Gadag Reference Terms]
                      </button>
                      <button
                        type="button"
                        onClick={() =>
                          handleChange(
                            'terms_and_conditions',
                            '1. Exchange within 15 days on presentation of original tax invoice.\n2. 100% buyback guarantee on gold weight at prevailing market rate.\n3. Diamonds certified by IGI / SGL.\n4. Disputes subject to store local jurisdiction.'
                          )
                        }
                        className="text-[11px] text-amber-700 font-bold hover:underline"
                      >
                        [Insert Tanishq/BlueStone Modern Terms]
                      </button>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">
                        Statutory Declaration
                      </label>
                      <input
                        type="text"
                        value={formData.declaration}
                        onChange={(e) => handleChange('declaration', e.target.value)}
                        placeholder="Certified that the particulars given above are true and correct..."
                        className="w-full px-3 py-2 border border-slate-300 rounded-xl text-xs focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">
                        Authorized Signatory Title
                      </label>
                      <input
                        type="text"
                        value={formData.signatory_title}
                        onChange={(e) => handleChange('signatory_title', e.target.value)}
                        placeholder="e.g. For, Shree Balaji Abharan Angadi"
                        className="w-full px-3 py-2 border border-slate-300 rounded-xl text-xs font-bold focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                      />
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-slate-200 bg-slate-50">
          <button
            onClick={handleResetDemo}
            disabled={isSaving}
            className="flex items-center gap-1.5 px-3 py-2 bg-slate-200 hover:bg-slate-300 text-slate-700 font-bold rounded-xl text-xs transition"
            title="Reset to Shree Balaji Abharan Angadi (Gadag) reference profile"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset to Gadag Reference Profile</span>
          </button>

          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              disabled={isSaving}
              className="px-4 py-2 text-slate-600 hover:text-slate-900 font-bold text-xs"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="flex items-center gap-2 px-5 py-2.5 bg-amber-600 hover:bg-amber-500 text-white font-black rounded-xl text-xs transition shadow-md shadow-amber-600/20 disabled:opacity-50"
            >
              <Save className="w-4 h-4" />
              <span>{isSaving ? 'Saving...' : 'Save Invoice Settings'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
