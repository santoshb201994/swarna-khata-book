import React, { useState, useEffect } from 'react';
import {
  Terminal,
  Users,
  Store,
  KeyRound,
  ExternalLink,
  Search,
  CheckCircle2,
  ArrowRight,
  Lock,
  RefreshCw,
  LogOut,
  X,
  Eye,
  EyeOff,
  Download,
  Calendar,
  Loader2,
  HardDriveDownload,
} from 'lucide-react';
import api from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import { PasswordPolicyChecklist } from '../../components/PasswordPolicyChecklist';
import { validatePasswordPolicy } from '../../utils/passwordPolicy';
import toast from 'react-hot-toast';

interface StoreUser {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  phone: string;
  is_active: boolean;
  branch_name?: string;
}

interface TenantItem {
  id: number;
  name: string;
  schema_name: string;
  description: string;
  is_active: boolean;
  created_on: string;
  domains: string[];
  product_count: number;
  branch_count: number;
  users: StoreUser[];
}

interface OverviewData {
  total_tenants: number;
  active_tenants: number;
  total_users: number;
  tenants: TenantItem[];
}

export const DeveloperPortal: React.FC = () => {
  const { user, developerLogin, logout } = useAuth();

  // Developer Login State
  const [devUsername, setDevUsername] = useState('');
  const [devPassword, setDevPassword] = useState('');
  const [showDevPassword, setShowDevPassword] = useState(false);
  const [isLoggingIn, setIsLoggingIn] = useState(false);

  // Dashboard Data State
  const [overview, setOverview] = useState<OverviewData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Reset Password State
  const [resetModal, setResetModal] = useState<{
    schemaName: string;
    userId: number;
    username: string;
  } | null>(null);
  const [newPassword, setNewPassword] = useState('');
  const [showResetPassword, setShowResetPassword] = useState(false);
  const [isResetting, setIsResetting] = useState(false);

  // Global Multi-Store Export State
  const [globalStartDate, setGlobalStartDate] = useState('');
  const [globalEndDate, setGlobalEndDate] = useState('');
  const [isExportingAll, setIsExportingAll] = useState(false);

  const isSuperadmin = user?.role === 'superadmin';

  const handleExportAllShops = async () => {
    if (globalStartDate && globalEndDate && globalStartDate > globalEndDate) {
      toast.error('Start Date cannot be after End Date.');
      return;
    }

    try {
      setIsExportingAll(true);
      const loadingToast = toast.loading('Compiling multi-tenant archive across all stores...');

      const params: Record<string, string> = {};
      if (globalStartDate) params.start_date = globalStartDate;
      if (globalEndDate) params.end_date = globalEndDate;

      const response = await api.get('/export/all-shops/', {
        params,
        responseType: 'blob',
      });

      let filename = `swarna_khata_global_all_shops_${new Date().toISOString().slice(0, 10)}.zip`;
      const disposition = response.headers['content-disposition'];
      if (disposition && disposition.includes('filename=')) {
        const match = disposition.match(/filename="?([^";]+)"?/);
        if (match && match[1]) {
          filename = match[1];
        }
      }

      const blob = new Blob([response.data], { type: 'application/zip' });
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(downloadUrl);

      toast.dismiss(loadingToast);
      toast.success('All stores global archive downloaded successfully!');
    } catch (err: any) {
      console.error('Global export failed:', err);
      toast.error(
        err.response?.status === 403
          ? 'Permission denied: Superadmin developer role required.'
          : 'Failed to export all shops. Please try again.'
      );
    } finally {
      setIsExportingAll(false);
    }
  };

  const fetchOverview = async () => {
    try {
      setIsLoading(true);
      const res = await api.get('/developer/overview/');
      setOverview(res.data);
    } catch (err: any) {
      if (err.response?.status === 403) {
        toast.error('Developer access denied. Superadmin credentials required.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isSuperadmin) {
      fetchOverview();
    }
  }, [isSuperadmin]);

  const handleDeveloperLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsLoggingIn(true);
      await developerLogin(devUsername, devPassword);
      toast.success('Developer Root Session Authenticated');
    } catch (err: any) {
      toast.error(err.response?.data?.error || 'Invalid developer credentials');
    } finally {
      setIsLoggingIn(false);
    }
  };

  const handleToggleTenant = async (schema: string, currentStatus: boolean) => {
    const nextStatus = !currentStatus;
    if (!confirm(`Are you sure you want to ${nextStatus ? 'activate' : 'suspend'} store schema '${schema}'?`)) {
      return;
    }
    try {
      await api.post(`/developer/tenants/${schema}/toggle-status/`, { is_active: nextStatus });
      toast.success(`Store schema '${schema}' ${nextStatus ? 'activated' : 'suspended'}.`);
      fetchOverview();
    } catch (err: any) {
      toast.error(err.response?.data?.error || 'Failed to update tenant status');
    }
  };

  const handleToggleUser = async (schema: string, userId: number, username: string, currentStatus: boolean) => {
    const nextStatus = !currentStatus;
    try {
      await api.post(`/developer/tenants/${schema}/users/${userId}/toggle-status/`, { is_active: nextStatus });
      toast.success(`User '${username}' ${nextStatus ? 'activated' : 'deactivated'}.`);
      fetchOverview();
    } catch {
      toast.error('Failed to update user status');
    }
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resetModal) return;
    const policy = validatePasswordPolicy(newPassword);
    if (!policy.isValid) {
      toast.error(policy.errors[0] || 'Password does not meet Jewellery Shield policy');
      return;
    }

    try {
      setIsResetting(true);
      await api.post(
        `/developer/tenants/${resetModal.schemaName}/users/${resetModal.userId}/reset-password/`,
        { new_password: newPassword }
      );
      toast.success(`Password reset successfully for ${resetModal.username}`);
      setResetModal(null);
      setNewPassword('');
    } catch (err: any) {
      toast.error(err.response?.data?.error || 'Failed to reset password');
    } finally {
      setIsResetting(false);
    }
  };

  const handleEnterStore = async (schema: string) => {
    try {
      const res = await api.post('/developer/switch-store-token/', { schema_name: schema });
      const { access } = res.data;
      localStorage.setItem('access_token', access);
      localStorage.setItem('x_tenant_schema', schema);

      const meRes = await api.get('/auth/me');
      localStorage.setItem('user_info', JSON.stringify(meRes.data));

      toast.success(`Entered store schema '${schema}' with full superadmin privileges!`);
      window.location.href = '/';
    } catch {
      toast.error('Failed to switch store context');
    }
  };

  // If not logged in as superadmin, show the Developer Terminal Login window
  if (!isSuperadmin) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center p-4">
        <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl p-8 space-y-6 relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-emerald-500 via-cyan-500 to-indigo-500" />

          <div className="text-center space-y-2">
            <div className="w-14 h-14 bg-gradient-to-tr from-emerald-500/20 to-cyan-500/20 border border-cyan-500/30 rounded-2xl flex items-center justify-center mx-auto text-cyan-400">
              <Terminal className="w-7 h-7" />
            </div>
            <h1 className="text-2xl font-black tracking-tight text-white flex items-center justify-center gap-2">
              Developer Control Plane
            </h1>
            <p className="text-xs text-slate-400 font-mono">
              [ROOT ACCESS] Multi-Tenant Database & Owner Hierarchy
            </p>
          </div>

          <div className="p-3 bg-slate-800/80 rounded-xl border border-slate-700/80 text-xs text-cyan-300 flex items-center gap-2">
            <Lock className="w-4 h-4 text-cyan-400 shrink-0" />
            <span>Developer / Platform Superadmin credentials required.</span>
          </div>

          <form onSubmit={handleDeveloperLogin} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase mb-1 font-mono">
                Developer Username
              </label>
              <input
                type="text"
                required
                value={devUsername}
                onChange={(e) => setDevUsername(e.target.value)}
                className="w-full px-4 py-2.5 bg-slate-950 border border-slate-700 rounded-xl text-sm text-white focus:outline-hidden focus:ring-2 focus:ring-cyan-500/40 font-mono"
                placeholder="root / admin"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase mb-1 font-mono">
                Master Password
              </label>
              <div className="relative flex items-center">
                <input
                  type={showDevPassword ? 'text' : 'password'}
                  required
                  value={devPassword}
                  onChange={(e) => setDevPassword(e.target.value)}
                  className="w-full px-4 py-2.5 pr-11 bg-slate-950 border border-slate-700 rounded-xl text-sm text-white focus:outline-hidden focus:ring-2 focus:ring-cyan-500/40 font-mono"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowDevPassword(!showDevPassword)}
                  className="absolute right-3 text-slate-400 hover:text-cyan-400 focus:outline-hidden cursor-pointer p-1"
                  title={showDevPassword ? 'Hide password' : 'Show password'}
                  aria-label={showDevPassword ? 'Hide password' : 'Show password'}
                >
                  {showDevPassword ? (
                    <EyeOff className="w-4 h-4 text-cyan-400" />
                  ) : (
                    <Eye className="w-4 h-4 text-slate-400" />
                  )}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoggingIn}
              className="w-full py-3 bg-gradient-to-r from-emerald-600 to-cyan-600 hover:from-emerald-500 hover:to-cyan-500 text-white font-bold rounded-xl shadow-lg transition transform active:scale-98 flex items-center justify-center gap-2 disabled:opacity-50"
            >
              <span>{isLoggingIn ? 'Verifying Superadmin...' : 'Authenticate Terminal'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          <div className="text-center pt-2">
            <a
              href="/login"
              className="text-xs text-slate-500 hover:text-slate-300 transition flex items-center justify-center gap-1"
            >
              <Store className="w-3.5 h-3.5" />
              <span>Return to Standard Shop Login</span>
            </a>
          </div>
        </div>
      </div>
    );
  }

  // Developer Control Plane Dashboard
  const filteredTenants = overview?.tenants.filter((t) =>
    t.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    t.schema_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    t.users.some((u) => u.username.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Root Bar */}
      <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur-md sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-cyan-500/10 border border-cyan-500/30 rounded-xl flex items-center justify-center text-cyan-400">
              <Terminal className="w-5 h-5" />
            </div>
            <div>
              <div className="font-black text-sm text-white flex items-center gap-2 tracking-tight">
                Swarna Khata SaaS Developer Console
                <span className="px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 text-[10px] font-mono border border-cyan-500/30">
                  SUPERUSER ROOT
                </span>
              </div>
              <div className="text-[11px] text-slate-400 font-mono">
                Global Tenant Isolation • Cross-Store Owner & Staff Authority
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={fetchOverview}
              disabled={isLoading}
              className="p-2 text-slate-400 hover:text-white bg-slate-800 rounded-xl transition"
              title="Refresh Data"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            </button>
            <div className="text-right hidden sm:block">
              <div className="text-xs font-bold text-white">{user?.username}</div>
              <div className="text-[10px] font-mono text-cyan-400 uppercase">Superadmin</div>
            </div>
            <button
              onClick={logout}
              className="p-2 text-rose-400 hover:bg-rose-500/10 rounded-xl transition"
              title="Exit Developer Session"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Body */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8 flex-1 w-full space-y-6">
        {/* Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex items-center gap-4">
            <div className="w-12 h-12 bg-amber-500/10 border border-amber-500/20 rounded-xl flex items-center justify-center text-amber-400">
              <Store className="w-6 h-6" />
            </div>
            <div>
              <div className="text-2xl font-black text-white">{overview?.total_tenants ?? 0}</div>
              <div className="text-xs text-slate-400 font-medium">Total Registered Stores</div>
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex items-center gap-4">
            <div className="w-12 h-12 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-center justify-center text-emerald-400">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <div>
              <div className="text-2xl font-black text-white">{overview?.active_tenants ?? 0}</div>
              <div className="text-xs text-slate-400 font-medium">Active Production Schemas</div>
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex items-center gap-4">
            <div className="w-12 h-12 bg-indigo-500/10 border border-indigo-500/20 rounded-xl flex items-center justify-center text-indigo-400">
              <Users className="w-6 h-6" />
            </div>
            <div>
              <div className="text-2xl font-black text-white">{overview?.total_users ?? 0}</div>
              <div className="text-xs text-slate-400 font-medium">Total Owners & Showroom Staff</div>
            </div>
          </div>
        </div>

        {/* Global Multi-Tenant Export Engine */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none" />
          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 relative z-10">
            <div className="space-y-1.5 max-w-xl">
              <div className="flex items-center gap-2">
                <span className="w-8 h-8 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
                  <HardDriveDownload className="w-4 h-4" />
                </span>
                <h2 className="text-base font-black text-white tracking-tight">
                  Global Multi-Store Data Archive
                </h2>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                  PLATFORM LEVEL 100
                </span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Stream an aggregated multi-tenant ZIP containing isolated datasets for every active store schema in PostgreSQL, complete with cross-store summary and metadata manifest.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-3 w-full lg:w-auto">
              <div className="flex items-center gap-2 bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-800 text-xs">
                <Calendar className="w-3.5 h-3.5 text-cyan-400" />
                <span className="text-slate-400">From:</span>
                <input
                  type="date"
                  value={globalStartDate}
                  onChange={(e) => setGlobalStartDate(e.target.value)}
                  className="bg-transparent text-white text-xs focus:outline-hidden"
                />
              </div>

              <div className="flex items-center gap-2 bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-800 text-xs">
                <Calendar className="w-3.5 h-3.5 text-cyan-400" />
                <span className="text-slate-400">To:</span>
                <input
                  type="date"
                  value={globalEndDate}
                  onChange={(e) => setGlobalEndDate(e.target.value)}
                  className="bg-transparent text-white text-xs focus:outline-hidden"
                />
              </div>

              <button
                type="button"
                onClick={handleExportAllShops}
                disabled={isExportingAll}
                className="flex items-center gap-2 px-5 py-2 bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white font-black text-xs rounded-xl shadow-lg shadow-cyan-600/20 transition active:scale-95 disabled:opacity-50 cursor-pointer"
              >
                {isExportingAll ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Archiving All Stores...</span>
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4" />
                    <span>Export All Stores (.ZIP)</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Search & Filter Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="relative w-full sm:w-96">
            <Search className="w-4 h-4 absolute left-3.5 top-3 text-slate-500" />
            <input
              type="text"
              placeholder="Search stores, schemas, owners, staff..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white focus:outline-hidden focus:ring-2 focus:ring-cyan-500/30"
            />
          </div>
          <div className="text-xs text-slate-400 font-mono">
            PostgreSQL Physical Isolation (django-tenants)
          </div>
        </div>

        {/* Store Directory */}
        {isLoading && !overview ? (
          <div className="py-20 text-center text-xs text-slate-500 font-mono">
            Loading tenant schemas and staff matrices...
          </div>
        ) : (
          <div className="space-y-6">
            {filteredTenants?.map((tenant) => (
              <div
                key={tenant.id}
                className="bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden shadow-xl"
              >
                {/* Store Header Banner */}
                <div className="p-5 border-b border-slate-800 bg-slate-850/60 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-3">
                      <h2 className="text-lg font-black text-white tracking-tight">{tenant.name}</h2>
                      <span className="text-[11px] font-mono px-2.5 py-0.5 rounded-full bg-slate-800 text-cyan-300 border border-slate-700">
                        schema: {tenant.schema_name}
                      </span>
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                          tenant.is_active
                            ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                            : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                        }`}
                      >
                        {tenant.is_active ? 'ACTIVE' : 'SUSPENDED'}
                      </span>
                    </div>
                    <div className="text-xs text-slate-400 flex flex-wrap gap-x-4 font-mono">
                      <span>Domains: {tenant.domains.join(', ') || 'N/A'}</span>
                      <span>Products: {tenant.product_count}</span>
                      <span>Branches: {tenant.branch_count}</span>
                      <span>Created: {tenant.created_on}</span>
                    </div>
                  </div>

                  {/* Store Actions */}
                  <div className="flex items-center gap-2 self-end md:self-center">
                    <button
                      onClick={() => handleToggleTenant(tenant.schema_name, tenant.is_active)}
                      className={`px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 ${
                        tenant.is_active
                          ? 'bg-rose-500/10 text-rose-400 hover:bg-rose-500/20 border border-rose-500/30'
                          : 'bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 border border-emerald-500/30'
                      }`}
                    >
                      {tenant.is_active ? 'Suspend Store' : 'Activate Store'}
                    </button>

                    <button
                      onClick={() => handleEnterStore(tenant.schema_name)}
                      className="px-4 py-1.5 bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white rounded-xl text-xs font-bold shadow-md transition flex items-center gap-1.5"
                    >
                      <span>Enter Store as Superadmin</span>
                      <ExternalLink className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

                {/* Staff Matrix Table */}
                <div className="p-5">
                  <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                    <Users className="w-3.5 h-3.5 text-cyan-400" />
                    <span>Store Owners, Managers & Salesmen ({tenant.users.length})</span>
                  </div>

                  {tenant.users.length === 0 ? (
                    <div className="py-6 text-center text-xs text-slate-500">
                      No accounts provisioned in this tenant schema yet.
                    </div>
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs">
                        <thead className="bg-slate-950/60 text-slate-400 font-mono uppercase text-[10px] border-b border-slate-800">
                          <tr>
                            <th className="py-2.5 px-3">Role</th>
                            <th className="py-2.5 px-3">Username</th>
                            <th className="py-2.5 px-3">Full Name</th>
                            <th className="py-2.5 px-3">Phone / Email</th>
                            <th className="py-2.5 px-3">Branch</th>
                            <th className="py-2.5 px-3">Status</th>
                            <th className="py-2.5 px-3 text-right">Developer Actions</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800/60 font-sans">
                          {tenant.users.map((u) => (
                            <tr key={u.id} className="hover:bg-slate-850/40 transition">
                              <td className="py-2.5 px-3">
                                <span
                                  className={`px-2 py-0.5 rounded-md font-bold uppercase text-[10px] ${
                                    u.role === 'owner'
                                      ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                                      : u.role === 'manager'
                                      ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                                      : u.role === 'accountant'
                                      ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                                      : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                                  }`}
                                >
                                  {u.role === 'staff' ? 'Salesman' : u.role}
                                </span>
                              </td>
                              <td className="py-2.5 px-3 font-bold text-white">{u.username}</td>
                              <td className="py-2.5 px-3 text-slate-300">
                                {u.first_name || u.last_name ? `${u.first_name} ${u.last_name}` : '—'}
                              </td>
                              <td className="py-2.5 px-3 text-slate-400 font-mono text-[11px]">
                                {u.phone || u.email || '—'}
                              </td>
                              <td className="py-2.5 px-3 text-slate-400">{u.branch_name || 'Main'}</td>
                              <td className="py-2.5 px-3">
                                <span
                                  className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                                    u.is_active
                                      ? 'bg-emerald-500/20 text-emerald-400'
                                      : 'bg-rose-500/20 text-rose-400'
                                  }`}
                                >
                                  {u.is_active ? 'Active' : 'Disabled'}
                                </span>
                              </td>
                              <td className="py-2.5 px-3 text-right">
                                <div className="flex items-center justify-end gap-2">
                                  <button
                                    onClick={() =>
                                      setResetModal({
                                        schemaName: tenant.schema_name,
                                        userId: u.id,
                                        username: u.username,
                                      })
                                    }
                                    className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-[11px] font-semibold flex items-center gap-1 transition"
                                    title="Reset Password"
                                  >
                                    <KeyRound className="w-3 h-3 text-cyan-400" />
                                    <span>Reset Pwd</span>
                                  </button>

                                  <button
                                    onClick={() =>
                                      handleToggleUser(
                                        tenant.schema_name,
                                        u.id,
                                        u.username,
                                        u.is_active
                                      )
                                    }
                                    className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold transition ${
                                      u.is_active
                                        ? 'bg-rose-500/10 text-rose-300 hover:bg-rose-500/20'
                                        : 'bg-emerald-500/10 text-emerald-300 hover:bg-emerald-500/20'
                                    }`}
                                  >
                                    {u.is_active ? 'Deactivate' : 'Activate'}
                                  </button>
                                </div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Reset Password Modal */}
        {resetModal && (
          <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-xs flex items-center justify-center p-4">
            <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 w-full max-w-md space-y-4 shadow-2xl">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <KeyRound className="w-5 h-5 text-cyan-400" />
                  <h3 className="font-bold text-white text-sm">
                    Developer Password Override: {resetModal.username}
                  </h3>
                </div>
                <button
                  onClick={() => setResetModal(null)}
                  className="text-slate-400 hover:text-white"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <p className="text-xs text-slate-400">
                Schema: <code className="text-cyan-300">{resetModal.schemaName}</code>. Enforces the strict Jewellery Shield password policy.
              </p>

              <form onSubmit={handleResetPassword} className="space-y-3">
                <div className="relative flex items-center">
                  <input
                    type={showResetPassword ? 'text' : 'password'}
                    required
                    placeholder="New compliant password (e.g. Master*Key8)"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    className="w-full px-3.5 py-2.5 pr-10 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-hidden focus:ring-2 focus:ring-cyan-500/40 font-mono"
                  />
                  <button
                    type="button"
                    onClick={() => setShowResetPassword(!showResetPassword)}
                    className="absolute right-2.5 text-slate-400 hover:text-cyan-400 focus:outline-hidden cursor-pointer p-1"
                    title={showResetPassword ? 'Hide password' : 'Show password'}
                    aria-label={showResetPassword ? 'Hide password' : 'Show password'}
                  >
                    {showResetPassword ? (
                      <EyeOff className="w-4 h-4 text-cyan-400" />
                    ) : (
                      <Eye className="w-4 h-4 text-slate-400" />
                    )}
                  </button>
                </div>

                <PasswordPolicyChecklist password={newPassword} showWhenEmpty={true} />

                <div className="flex justify-end gap-2 pt-2">
                  <button
                    type="button"
                    onClick={() => setResetModal(null)}
                    className="px-3.5 py-1.5 border border-slate-700 text-slate-400 hover:bg-slate-800 rounded-xl text-xs font-semibold"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isResetting}
                    className="px-4 py-1.5 bg-gradient-to-r from-emerald-600 to-cyan-600 hover:from-emerald-500 hover:to-cyan-500 text-white rounded-xl text-xs font-bold shadow-md transition disabled:opacity-50"
                  >
                    {isResetting ? 'Saving...' : 'Set New Password'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};
