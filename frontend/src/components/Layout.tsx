import React, { useState } from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Sparkles,
  ShoppingBag,
  Receipt,
  BookOpen,
  LogOut,
  Users,
  Settings2,
  UserCheck,
  Download,
} from 'lucide-react';
import { StaffManagementModal } from '../features/users/StaffManagementModal';
import { InvoiceSettingsModal } from '../features/billing/InvoiceSettingsModal';
import { CustomerDirectoryModal } from '../features/customers/CustomerDirectoryModal';
import { ExportDataModal } from '../features/export/ExportDataModal';
import { canAccessFeature } from '../utils/rbac';

export const Layout: React.FC = () => {
  const { user, logout } = useAuth();
  const [isStaffModalOpen, setIsStaffModalOpen] = useState(false);
  const [isInvoiceSettingsOpen, setIsInvoiceSettingsOpen] = useState(false);
  const [isCustomerModalOpen, setIsCustomerModalOpen] = useState(false);
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);

  // RBAC Hierarchy Controls
  const canManageStaff = canAccessFeature(user?.role, 'manage_staff');
  const canAccessInvoiceStudio = canAccessFeature(user?.role, 'invoice_studio');
  const canExportShopData = canAccessFeature(user?.role, 'export_shop_data');
  const canAccessAccounting = canAccessFeature(user?.role, 'view_accounting');
  const canAccessCustomers = canAccessFeature(user?.role, 'customer_directory');

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Top Header Navbar */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-tr from-amber-600 to-amber-400 rounded-xl flex items-center justify-center shadow-md shadow-amber-500/20 text-white font-black text-lg">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <div className="font-black text-base tracking-tight text-slate-900 leading-none">
                Swarna Khata Book
              </div>
              <div className="text-[11px] text-amber-700 font-semibold tracking-wide uppercase mt-0.5">
                Jewellery ERP • Multi-Tenant SaaS
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 sm:gap-3">
            {canAccessCustomers && (
              <button
                onClick={() => setIsCustomerModalOpen(true)}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-200/90 rounded-xl text-xs font-bold transition shadow-2xs"
                title="Customer Directory & Khata Records"
              >
                <UserCheck className="w-3.5 h-3.5 text-amber-700" />
                <span className="hidden sm:inline">Customers</span>
              </button>
            )}

            {canManageStaff && (
              <button
                onClick={() => setIsStaffModalOpen(true)}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-amber-100/70 hover:bg-amber-200/80 text-amber-900 border border-amber-300 rounded-xl text-xs font-bold transition"
                title="Manage Showroom Staff & Salesmen (Hierarchy Level 60+)"
              >
                <Users className="w-3.5 h-3.5 text-amber-700" />
                <span className="hidden md:inline">Staff</span>
              </button>
            )}

            {canAccessInvoiceStudio && (
              <button
                onClick={() => setIsInvoiceSettingsOpen(true)}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-amber-500 hover:bg-amber-400 text-slate-950 font-black rounded-xl text-xs transition shadow-sm"
                title="Customize Jewellery Invoice Template, Kannada/English Headers & Branding (Store Owner Level 80+)"
              >
                <Settings2 className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Bill & Invoice Studio</span>
              </button>
            )}

            {canExportShopData && (
              <button
                onClick={() => setIsExportModalOpen(true)}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-amber-300 border border-slate-700 rounded-xl text-xs font-bold transition shadow-xs"
                title="Export Store Data Archive (CSV & Manifest ZIP - Store Owner Level 80+)"
              >
                <Download className="w-3.5 h-3.5 text-amber-400" />
                <span className="hidden sm:inline">Export Data</span>
              </button>
            )}

            <div className="flex items-center gap-3 pl-2 border-l border-slate-200">
              <div className="text-right hidden sm:block">
                <div className="text-xs font-bold text-slate-800">{user?.username}</div>
                <div className="text-[10px] uppercase font-semibold text-amber-600">
                  {user?.role === 'staff' ? 'Salesman' : user?.role || 'owner'}
                </div>
              </div>
              <button
                onClick={logout}
                className="p-2 text-slate-400 hover:text-rose-600 hover:bg-slate-100 rounded-xl transition"
                title="Logout"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Tab Navigation Menu */}
        <div className="border-t border-slate-100 bg-slate-50/50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 flex gap-1 sm:gap-2 overflow-x-auto">
            <NavLink
              to="/"
              end
              className={({ isActive }) =>
                `flex items-center gap-2 py-3 px-4 text-xs font-bold border-b-2 transition ${
                  isActive
                    ? 'border-amber-600 text-amber-800 bg-white'
                    : 'border-transparent text-slate-600 hover:text-slate-900 hover:border-slate-300'
                }`
              }
            >
              <Receipt className="w-4 h-4" />
              <span>POS Billing & Invoice</span>
            </NavLink>

            <NavLink
              to="/products"
              className={({ isActive }) =>
                `flex items-center gap-2 py-3 px-4 text-xs font-bold border-b-2 transition ${
                  isActive
                    ? 'border-amber-600 text-amber-800 bg-white'
                    : 'border-transparent text-slate-600 hover:text-slate-900 hover:border-slate-300'
                }`
              }
            >
              <ShoppingBag className="w-4 h-4" />
              <span>Items & QR Tags</span>
            </NavLink>

            {canAccessAccounting && (
              <NavLink
                to="/accounting"
                className={({ isActive }) =>
                  `flex items-center gap-2 py-3 px-4 text-xs font-bold border-b-2 transition ${
                    isActive
                      ? 'border-amber-600 text-amber-800 bg-white'
                      : 'border-transparent text-slate-600 hover:text-slate-900 hover:border-slate-300'
                  }`
                }
              >
                <BookOpen className="w-4 h-4" />
                <span>Accounting & Day Book</span>
              </NavLink>
            )}
          </div>
        </div>
      </header>

      {/* Main Content View */}
      <main className="flex-1">
        <Outlet />
      </main>

      {/* Customer Directory Modal (Available to all store users) */}
      <CustomerDirectoryModal
        isOpen={isCustomerModalOpen}
        onClose={() => setIsCustomerModalOpen(false)}
      />

      {/* Staff Management (Owner & Manager Hierarchy: Level 60+) */}
      {canManageStaff && (
        <StaffManagementModal
          isOpen={isStaffModalOpen}
          onClose={() => setIsStaffModalOpen(false)}
          currentUserRole={user?.role}
        />
      )}

      {/* Bill & Invoice Studio (Store Owner / Superadmin Hierarchy: Level 80+) */}
      {canAccessInvoiceStudio && (
        <InvoiceSettingsModal
          isOpen={isInvoiceSettingsOpen}
          onClose={() => setIsInvoiceSettingsOpen(false)}
        />
      )}

      {/* Store Data Export Modal (Store Owner / Superadmin Hierarchy: Level 80+) */}
      {canExportShopData && (
        <ExportDataModal
          isOpen={isExportModalOpen}
          onClose={() => setIsExportModalOpen(false)}
        />
      )}
    </div>
  );
};
