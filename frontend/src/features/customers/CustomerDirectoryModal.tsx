import React, { useState, useEffect } from 'react';
import type { Customer } from '../../types';
import api from '../../api/client';
import {
  Users,
  Search,
  Plus,
  X,
  Phone,
  CreditCard,
  MapPin,
  Edit2,
  Calendar,
  Receipt,
  Mail,
} from 'lucide-react';
import { CustomerFormModal } from './CustomerFormModal';
import toast from 'react-hot-toast';

interface CustomerDirectoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectCustomerForBill?: (customer: Customer) => void;
}

export const CustomerDirectoryModal: React.FC<CustomerDirectoryModalProps> = ({
  isOpen,
  onClose,
  onSelectCustomerForBill,
}) => {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState<Customer | null>(null);

  const fetchCustomers = async (search?: string) => {
    try {
      setIsLoading(true);
      const url = search ? `/customers/?search=${encodeURIComponent(search)}` : '/customers/';
      const res = await api.get(url);
      setCustomers(res.data.results || res.data);
    } catch {
      toast.error('Failed to load customers');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchCustomers();
    }
  }, [isOpen]);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setSearchQuery(val);
    fetchCustomers(val);
  };

  const handleOpenAdd = () => {
    setEditingCustomer(null);
    setIsFormModalOpen(true);
  };

  const handleOpenEdit = (customer: Customer) => {
    setEditingCustomer(customer);
    setIsFormModalOpen(true);
  };

  const handleCustomerSaved = (savedCust: Customer) => {
    setCustomers((prev) => {
      const idx = prev.findIndex((c) => c.id === savedCust.id);
      if (idx >= 0) {
        const copy = [...prev];
        copy[idx] = savedCust;
        return copy;
      }
      return [savedCust, ...prev];
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-xs p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden border border-slate-200">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-200 flex justify-between items-center bg-slate-50/70 shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-500 text-white flex items-center justify-center shadow-sm">
              <Users className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-black text-slate-900 tracking-tight flex items-center gap-2">
                <span>Customer Khata Directory</span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 font-bold">
                  {customers.length} registered
                </span>
              </h2>
              <p className="text-xs text-slate-500">
                Search, add and manage jewellery showroom customer profiles & tax details
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleOpenAdd}
              className="flex items-center gap-1.5 px-3.5 py-2 bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs rounded-xl shadow-xs transition"
            >
              <Plus className="w-4 h-4" />
              <span>Add New Customer</span>
            </button>
            <button
              onClick={onClose}
              className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-200/60 rounded-xl transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Search Bar */}
        <div className="p-4 border-b border-slate-100 bg-white shrink-0">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by customer name, phone number, PAN, address..."
              value={searchQuery}
              onChange={handleSearchChange}
              className="w-full pl-10 pr-4 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-amber-500/20"
              autoFocus
            />
          </div>
        </div>

        {/* Customer List */}
        <div className="flex-1 overflow-y-auto p-4 divide-y divide-slate-100">
          {isLoading ? (
            <div className="p-12 text-center text-sm text-slate-400">Loading customer directory...</div>
          ) : customers.length === 0 ? (
            <div className="p-12 text-center space-y-3">
              <Users className="w-10 h-10 text-slate-300 mx-auto" />
              <div className="text-sm font-semibold text-slate-700">No customers found</div>
              <p className="text-xs text-slate-400 max-w-sm mx-auto">
                {searchQuery
                  ? `No customer matches "${searchQuery}". Click below to add them as a new customer.`
                  : 'Start registering customers to track purchase history, KYC and khata ledgers.'}
              </p>
              <button
                onClick={handleOpenAdd}
                className="inline-flex items-center gap-1.5 px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs rounded-xl transition shadow-xs"
              >
                <Plus className="w-4 h-4" />
                <span>Add Customer Now</span>
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {customers.map((cust) => (
                <div
                  key={cust.id}
                  className="p-4 bg-white rounded-xl border border-slate-200 hover:border-amber-300 hover:shadow-xs transition flex flex-col justify-between space-y-3"
                >
                  <div>
                    <div className="flex justify-between items-start gap-2">
                      <div className="font-bold text-slate-900 text-sm flex items-center gap-1.5">
                        <span>{cust.name}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => handleOpenEdit(cust)}
                          className="p-1.5 text-slate-400 hover:text-amber-700 hover:bg-amber-50 rounded-lg transition"
                          title="Edit Customer Details"
                        >
                          <Edit2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>

                    <div className="space-y-1 mt-2 text-xs text-slate-600">
                      <div className="flex items-center gap-2 font-mono">
                        <Phone className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                        <span className="font-semibold text-slate-800">{cust.phone}</span>
                      </div>
                      {cust.pan_number && (
                        <div className="flex items-center gap-2 font-mono">
                          <CreditCard className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                          <span className="text-amber-900 font-bold">PAN: {cust.pan_number}</span>
                        </div>
                      )}
                      {cust.address && (
                        <div className="flex items-center gap-2">
                          <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                          <span className="text-slate-500 line-clamp-1">{cust.address}</span>
                        </div>
                      )}
                      {cust.email && (
                        <div className="flex items-center gap-2">
                          <Mail className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                          <span className="text-slate-500 truncate">{cust.email}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="pt-2 border-t border-slate-100 flex justify-between items-center text-[11px]">
                    <span className="text-slate-400 flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      <span>{cust.created_at ? new Date(cust.created_at).toLocaleDateString() : 'Customer'}</span>
                    </span>
                    {onSelectCustomerForBill && (
                      <button
                        onClick={() => {
                          onSelectCustomerForBill(cust);
                          onClose();
                          toast.success(`Selected ${cust.name} for POS bill!`);
                        }}
                        className="flex items-center gap-1 px-3 py-1 bg-amber-500 hover:bg-amber-600 text-slate-950 font-black rounded-lg transition"
                      >
                        <Receipt className="w-3 h-3" />
                        <span>Bill Customer</span>
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-200 bg-slate-50 flex justify-between items-center text-xs text-slate-500 shrink-0">
          <span>Showing {customers.length} customer records</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 text-slate-600 hover:text-slate-800 font-bold hover:bg-slate-200/60 rounded-lg transition"
          >
            Close
          </button>
        </div>
      </div>

      {/* Customer Form Modal */}
      <CustomerFormModal
        isOpen={isFormModalOpen}
        onClose={() => setIsFormModalOpen(false)}
        initialCustomer={editingCustomer}
        onCustomerSaved={handleCustomerSaved}
      />
    </div>
  );
};
