import React, { useState, useEffect } from 'react';
import api from '../../api/client';
import type { Customer } from '../../types';
import { X, UserPlus, Phone, CreditCard, MapPin, Mail, Hash, Check } from 'lucide-react';
import toast from 'react-hot-toast';

interface CustomerFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCustomerSaved: (customer: Customer) => void;
  initialCustomer?: Customer | null;
  initialSearchQuery?: string;
}

export const CustomerFormModal: React.FC<CustomerFormModalProps> = ({
  isOpen,
  onClose,
  onCustomerSaved,
  initialCustomer,
  initialSearchQuery = '',
}) => {
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [panNumber, setPanNumber] = useState('');
  const [address, setAddress] = useState('');
  const [email, setEmail] = useState('');
  const [aadharLast4, setAadharLast4] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [existingMatch, setExistingMatch] = useState<Customer | null>(null);

  useEffect(() => {
    if (initialCustomer) {
      setName(initialCustomer.name || '');
      setPhone(initialCustomer.phone || '');
      setPanNumber(initialCustomer.pan_number || '');
      setAddress(initialCustomer.address || '');
      setEmail(initialCustomer.email || '');
      setAadharLast4(initialCustomer.aadhar_last4 || '');
      setExistingMatch(null);
    } else {
      // If initialSearchQuery looks like a phone number, prefill phone, else prefill name
      const isDigits = /^\d+$/.test(initialSearchQuery.trim());
      if (isDigits) {
        setPhone(initialSearchQuery.trim());
        setName('');
      } else {
        setName(initialSearchQuery.trim());
        setPhone('');
      }
      setPanNumber('');
      setAddress('');
      setEmail('');
      setAadharLast4('');
      setExistingMatch(null);
    }
  }, [initialCustomer, initialSearchQuery, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanName = name.trim();
    const cleanPhone = phone.trim().replace(/\D/g, ''); // strip non-digits

    if (!cleanName) {
      toast.error('Customer name is required');
      return;
    }

    if (!cleanPhone || cleanPhone.length < 10) {
      toast.error('Please enter a valid 10-digit mobile number');
      return;
    }

    const cleanPan = panNumber.trim().toUpperCase();
    if (cleanPan && !/^[A-Z]{5}[0-9]{4}[A-Z]{1}$/.test(cleanPan)) {
      toast.error('Invalid PAN format (e.g. ABCDE1234F)');
      return;
    }

    const cleanAadhar = aadharLast4.trim();
    if (cleanAadhar && !/^\d{4}$/.test(cleanAadhar)) {
      toast.error('Aadhar must be exactly the last 4 digits');
      return;
    }

    try {
      setIsSubmitting(true);
      const payload = {
        name: cleanName,
        phone: cleanPhone,
        pan_number: cleanPan,
        address: address.trim(),
        email: email.trim(),
        aadhar_last4: cleanAadhar,
      };

      if (initialCustomer?.id) {
        // Edit existing customer
        const res = await api.put(`/customers/${initialCustomer.id}/`, payload);
        toast.success(`Customer "${cleanName}" updated successfully!`);
        onCustomerSaved(res.data);
        onClose();
      } else {
        // Create new customer
        const res = await api.post('/customers/', payload);
        toast.success(`Customer "${cleanName}" registered & selected!`);
        onCustomerSaved(res.data);
        onClose();
      }
    } catch (err: any) {
      const errData = err.response?.data;
      if (errData?.existing_customer_id) {
        toast.error(errData.error || 'Customer already exists with this phone number.');
        // Offer to load existing customer
        try {
          const fetchRes = await api.get(`/customers/${errData.existing_customer_id}/`);
          setExistingMatch(fetchRes.data);
        } catch {
          // ignore
        }
      } else {
        toast.error(errData?.error || 'Failed to save customer. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-xs p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden border border-slate-200 animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="flex justify-between items-center px-6 py-4 border-b border-slate-100 bg-gradient-to-r from-amber-500/10 via-amber-500/5 to-transparent">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-amber-500 text-white flex items-center justify-center shadow-sm">
              <UserPlus className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-slate-900 text-base">
                {initialCustomer ? 'Edit Customer Details' : 'Add New Customer'}
              </h3>
              <p className="text-xs text-slate-500">
                {initialCustomer ? 'Update customer profile and tax identifiers' : 'Register customer for jewellery billing & khata records'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-xl text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Existing match banner (if phone already exists) */}
        {existingMatch && (
          <div className="mx-6 mt-4 p-3 bg-amber-50 border border-amber-300 rounded-xl flex items-center justify-between text-xs">
            <div>
              <span className="font-bold text-amber-900">Existing Customer Found: </span>
              <span className="text-slate-800 font-semibold">{existingMatch.name}</span> ({existingMatch.phone})
            </div>
            <button
              type="button"
              onClick={() => {
                onCustomerSaved(existingMatch);
                toast.success(`Selected existing customer: ${existingMatch.name}`);
                onClose();
              }}
              className="px-3 py-1 bg-amber-600 hover:bg-amber-700 text-white font-bold rounded-lg transition"
            >
              Select Existing
            </button>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Customer Name */}
            <div className="sm:col-span-2">
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Full Name <span className="text-rose-500">*</span>
              </label>
              <input
                type="text"
                required
                placeholder="e.g. Ramesh Patil"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-3.5 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-amber-500/20"
                autoFocus
              />
            </div>

            {/* Phone Number */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1 flex items-center gap-1">
                <Phone className="w-3.5 h-3.5 text-slate-400" />
                <span>Mobile Number</span> <span className="text-rose-500">*</span>
              </label>
              <input
                type="tel"
                required
                maxLength={10}
                placeholder="10-digit mobile (e.g. 9876543210)"
                value={phone}
                onChange={(e) => setPhone(e.target.value.replace(/\D/g, ''))}
                className="w-full px-3.5 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl font-mono focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-amber-500/20"
              />
            </div>

            {/* PAN Number */}
            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="text-xs font-semibold text-slate-700 flex items-center gap-1">
                  <CreditCard className="w-3.5 h-3.5 text-slate-400" />
                  <span>PAN Number</span>
                </label>
                <span className="text-[10px] text-amber-700 font-medium">Recom. ≥ ₹2 Lakh</span>
              </div>
              <input
                type="text"
                maxLength={10}
                placeholder="ABCDE1234F"
                value={panNumber}
                onChange={(e) => setPanNumber(e.target.value.toUpperCase())}
                className="w-full px-3.5 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl font-mono uppercase focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-amber-500/20"
              />
            </div>

            {/* Address */}
            <div className="sm:col-span-2">
              <label className="block text-xs font-semibold text-slate-700 mb-1 flex items-center gap-1">
                <MapPin className="w-3.5 h-3.5 text-slate-400" />
                <span>Showroom / Residential Address</span>
              </label>
              <input
                type="text"
                placeholder="e.g. Old Shroff Bazar, Gadag - 582101"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                className="w-full px-3.5 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-amber-500/20"
              />
            </div>

            {/* Email */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1 flex items-center gap-1">
                <Mail className="w-3.5 h-3.5 text-slate-400" />
                <span>Email (Optional)</span>
              </label>
              <input
                type="email"
                placeholder="customer@gmail.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3.5 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-amber-500/20"
              />
            </div>

            {/* Aadhar Last 4 */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1 flex items-center gap-1">
                <Hash className="w-3.5 h-3.5 text-slate-400" />
                <span>Aadhar Last 4 Digits</span>
              </label>
              <input
                type="text"
                maxLength={4}
                placeholder="e.g. 5432"
                value={aadharLast4}
                onChange={(e) => setAadharLast4(e.target.value.replace(/\D/g, ''))}
                className="w-full px-3.5 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl font-mono focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-amber-500/20"
              />
            </div>
          </div>

          {/* Action buttons */}
          <div className="pt-4 border-t border-slate-100 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2.5 text-xs font-bold text-slate-600 hover:text-slate-800 hover:bg-slate-100 rounded-xl transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex items-center gap-2 px-5 py-2.5 bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs rounded-xl shadow-md transition disabled:opacity-50"
            >
              <Check className="w-4 h-4" />
              <span>{isSubmitting ? 'Saving...' : initialCustomer ? 'Update Customer' : 'Save & Select Customer'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
