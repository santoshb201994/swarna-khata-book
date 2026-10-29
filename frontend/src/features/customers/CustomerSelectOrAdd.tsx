import React, { useState, useEffect, useRef } from 'react';
import type { Customer } from '../../types';
import api from '../../api/client';
import {
  UserCheck,
  Search,
  Plus,
  X,
  Phone,
  CreditCard,
  Edit2,
  MapPin,
  Check,
  User,
} from 'lucide-react';
import { CustomerFormModal } from './CustomerFormModal';

interface CustomerSelectOrAddProps {
  customers: Customer[];
  selectedCustomerId: string;
  onSelectCustomer: (customerId: string, customer?: Customer) => void;
  onCustomerAddedOrUpdated: (customer: Customer) => void;
}

export const CustomerSelectOrAdd: React.FC<CustomerSelectOrAddProps> = ({
  customers,
  selectedCustomerId,
  onSelectCustomer,
  onCustomerAddedOrUpdated,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isOpenDropdown, setIsOpenDropdown] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState<Customer | null>(null);
  const [searchResults, setSearchResults] = useState<Customer[]>(customers);
  const [isSearchingBackend, setIsSearchingBackend] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Selected customer object
  const selectedCustomer = customers.find((c) => String(c.id) === String(selectedCustomerId)) || null;

  // Filter local customers immediately, and debounce backend search
  useEffect(() => {
    const term = searchQuery.trim().toLowerCase();
    if (!term) {
      setSearchResults(customers.slice(0, 50));
      return;
    }

    // Local filter
    const localFiltered = customers.filter(
      (c) =>
        c.name.toLowerCase().includes(term) ||
        c.phone.toLowerCase().includes(term) ||
        (c.pan_number && c.pan_number.toLowerCase().includes(term)) ||
        (c.address && c.address.toLowerCase().includes(term))
    );
    setSearchResults(localFiltered);

    // If local results are few or user is typing actively, query backend
    const timeoutId = setTimeout(async () => {
      try {
        setIsSearchingBackend(true);
        const res = await api.get(`/customers/?search=${encodeURIComponent(term)}`);
        const serverCustomers: Customer[] = res.data.results || res.data;
        if (Array.isArray(serverCustomers) && serverCustomers.length > 0) {
          // Merge unique by ID
          const existingIds = new Set(localFiltered.map((c) => c.id));
          const combined = [...localFiltered];
          serverCustomers.forEach((sc) => {
            if (!existingIds.has(sc.id)) {
              combined.push(sc);
            }
          });
          setSearchResults(combined);
        }
      } catch {
        // ignore network error for search
      } finally {
        setIsSearchingBackend(false);
      }
    }, 250);

    return () => clearTimeout(timeoutId);
  }, [searchQuery, customers]);

  // Click outside listener to close dropdown
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpenDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (customer: Customer | null) => {
    if (customer) {
      onSelectCustomer(String(customer.id), customer);
      setSearchQuery('');
      setIsOpenDropdown(false);
    } else {
      // Walk-in
      onSelectCustomer('');
      setSearchQuery('');
      setIsOpenDropdown(false);
    }
  };

  const handleOpenAddModal = (initialQuery?: string) => {
    setEditingCustomer(null);
    setSearchQuery(initialQuery || searchQuery);
    setIsModalOpen(true);
    setIsOpenDropdown(false);
  };

  const handleOpenEditModal = (customer: Customer) => {
    setEditingCustomer(customer);
    setIsModalOpen(true);
  };

  return (
    <div className="space-y-2 relative" ref={dropdownRef}>
      <div className="flex justify-between items-center">
        <label className="text-xs font-semibold text-slate-700 flex items-center gap-1">
          <UserCheck className="w-3.5 h-3.5 text-amber-600" />
          <span>Billed Customer (Khata)</span>
        </label>
        <button
          type="button"
          onClick={() => handleOpenAddModal('')}
          className="text-xs font-bold text-amber-700 hover:text-amber-800 flex items-center gap-1 transition"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>New Customer</span>
        </button>
      </div>

      {/* When a customer IS selected: Display Rich Customer Card */}
      {selectedCustomer ? (
        <div className="p-3 bg-amber-50/70 border border-amber-200/90 rounded-xl flex items-center justify-between gap-3 shadow-2xs">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-9 h-9 rounded-xl bg-amber-500 text-white flex items-center justify-center shrink-0 font-bold text-sm shadow-2xs">
              {selectedCustomer.name.charAt(0).toUpperCase()}
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <span className="font-bold text-sm text-slate-900 truncate">
                  {selectedCustomer.name}
                </span>
                <span className="inline-flex items-center gap-0.5 px-1.5 py-0.2 text-[10px] font-bold bg-emerald-100 text-emerald-800 rounded">
                  <Check className="w-2.5 h-2.5" /> Verified
                </span>
              </div>
              <div className="flex flex-wrap items-center gap-x-2 gap-y-0.5 text-xs text-slate-600 mt-0.5 font-mono">
                <span className="flex items-center gap-1">
                  <Phone className="w-3 h-3 text-slate-400" />
                  <span>{selectedCustomer.phone}</span>
                </span>
                {selectedCustomer.pan_number && (
                  <span className="flex items-center gap-1 text-amber-900 font-semibold">
                    <CreditCard className="w-3 h-3 text-amber-600" />
                    <span>PAN: {selectedCustomer.pan_number}</span>
                  </span>
                )}
                {selectedCustomer.address && (
                  <span className="flex items-center gap-1 text-slate-500 truncate max-w-[200px]">
                    <MapPin className="w-3 h-3 text-slate-400 shrink-0" />
                    <span className="truncate">{selectedCustomer.address}</span>
                  </span>
                )}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-1.5 shrink-0">
            <button
              type="button"
              onClick={() => handleOpenEditModal(selectedCustomer)}
              className="p-1.5 text-slate-500 hover:text-amber-700 hover:bg-amber-100/60 rounded-lg transition"
              title="Edit Customer"
            >
              <Edit2 className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              onClick={() => handleSelect(null)}
              className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition"
              title="Switch to Walk-in or Change Customer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      ) : (
        /* When NO customer is selected: Search Bar + Walk-in Selector + New Button */
        <div className="space-y-2">
          <div className="relative flex items-center">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 pointer-events-none" />
            <input
              type="text"
              placeholder="Search customer by name, mobile, PAN..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setIsOpenDropdown(true);
              }}
              onFocus={() => setIsOpenDropdown(true)}
              className="w-full pl-9 pr-24 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-amber-500/20"
            />

            <button
              type="button"
              onClick={() => handleOpenAddModal(searchQuery)}
              className="absolute right-1.5 px-2.5 py-1.5 bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs rounded-lg transition shadow-2xs flex items-center gap-1"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>+ Add</span>
            </button>
          </div>

          {/* Quick Walk-in Indicator */}
          <div className="flex items-center justify-between px-1">
            <span className="text-[11px] text-slate-500 flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-slate-400" />
              <span>Current: <b>Walk-in Cash Customer</b></span>
            </span>
            {searchQuery && (
              <button
                type="button"
                onClick={() => setSearchQuery('')}
                className="text-[11px] text-slate-400 hover:text-slate-600"
              >
                Clear search
              </button>
            )}
          </div>

          {/* Autocomplete Dropdown */}
          {isOpenDropdown && (
            <div className="absolute left-0 right-0 top-full mt-1 bg-white border border-slate-200 rounded-xl shadow-xl z-50 max-h-64 overflow-y-auto divide-y divide-slate-100 animate-in fade-in zoom-in-95 duration-100">
              {/* Option for Walk-in */}
              <div
                onClick={() => handleSelect(null)}
                className="p-2.5 hover:bg-slate-50 transition cursor-pointer flex items-center justify-between text-xs"
              >
                <div className="flex items-center gap-2">
                  <User className="w-4 h-4 text-slate-400" />
                  <span className="font-semibold text-slate-700">Walk-in Customer (No Khata)</span>
                </div>
                <span className="text-[10px] text-slate-400">Default</span>
              </div>

              {/* Customer List Matches */}
              {searchResults.length > 0 ? (
                searchResults.map((cust) => (
                  <div
                    key={cust.id}
                    onClick={() => handleSelect(cust)}
                    className="p-2.5 hover:bg-amber-50/60 transition cursor-pointer flex items-center justify-between text-xs gap-2"
                  >
                    <div>
                      <div className="font-bold text-slate-900">{cust.name}</div>
                      <div className="text-[11px] text-slate-500 font-mono flex items-center gap-2 mt-0.5">
                        <span className="flex items-center gap-1">
                          <Phone className="w-3 h-3 text-slate-400" />
                          <span>{cust.phone}</span>
                        </span>
                        {cust.pan_number && (
                          <span className="text-amber-800 font-semibold">
                            PAN: {cust.pan_number}
                          </span>
                        )}
                        {cust.address && (
                          <span className="text-slate-400 truncate max-w-[160px]">
                            {cust.address}
                          </span>
                        )}
                      </div>
                    </div>
                    <button
                      type="button"
                      className="px-2.5 py-1 bg-amber-100 text-amber-900 font-bold text-[10px] rounded-md hover:bg-amber-200"
                    >
                      Select
                    </button>
                  </div>
                ))
              ) : (
                <div className="p-4 text-center space-y-2">
                  <p className="text-xs text-slate-500">
                    No customer found matching "<b>{searchQuery}</b>"
                  </p>
                  <button
                    type="button"
                    onClick={() => handleOpenAddModal(searchQuery)}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs rounded-xl shadow-xs transition"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>Add "{searchQuery}" as New Customer</span>
                  </button>
                </div>
              )}

              {isSearchingBackend && (
                <div className="p-2 text-center text-[10px] text-slate-400 font-medium">
                  Searching customer directory...
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Customer Form Modal */}
      <CustomerFormModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        initialCustomer={editingCustomer}
        initialSearchQuery={searchQuery}
        onCustomerSaved={(savedCust) => {
          onCustomerAddedOrUpdated(savedCust);
          onSelectCustomer(String(savedCust.id), savedCust);
        }}
      />
    </div>
  );
};
