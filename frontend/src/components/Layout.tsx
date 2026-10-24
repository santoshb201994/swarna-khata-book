import React, { useState } from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Sparkles,
  ShoppingBag,
  Receipt,
  BookOpen,
  LogOut,
  Building2,
  Users,
} from 'lucide-react';
import { StaffManagementModal } from '../features/users/StaffManagementModal';

export const Layout: React.FC = () => {
  const { user, logout } = useAuth();
  const [isStaffModalOpen, setIsStaffModalOpen] = useState(false);

  const isOwnerOrManager = user?.role === 'owner' || user?.role === 'manager' || user?.role === 'superadmin';

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

          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1 bg-amber-50 border border-amber-200/80 rounded-xl text-xs font-semibold text-amber-900">
              <Building2 className="w-3.5 h-3.5 text-amber-700" />
              <span>Main Showroom</span>
            </div>

            {isOwnerOrManager && (
              <button
                onClick={() => setIsStaffModalOpen(true)}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-amber-100/70 hover:bg-amber-200/80 text-amber-900 border border-amber-300 rounded-xl text-xs font-bold transition"
                title="Manage Showroom Staff & Salesmen"
              >
                <Users className="w-3.5 h-3.5 text-amber-700" />
                <span className="hidden md:inline">Staff & Salesmen</span>
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
          </div>
        </div>
      </header>

      {/* Main Content View */}
      <main className="flex-1">
        <Outlet />
      </main>

      {/* Staff Management Modal for Store Owners */}
      {isOwnerOrManager && (
        <StaffManagementModal
          isOpen={isStaffModalOpen}
          onClose={() => setIsStaffModalOpen(false)}
          currentUserRole={user?.role}
        />
      )}
    </div>
  );
};
