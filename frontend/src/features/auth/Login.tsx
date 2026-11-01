import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Sparkles, ArrowRight, ShieldCheck, Store, UserPlus, Building2, Eye, EyeOff } from 'lucide-react';
import api from '../../api/client';
import { PasswordPolicyChecklist } from '../../components/PasswordPolicyChecklist';
import { validatePasswordPolicy } from '../../utils/passwordPolicy';
import toast from 'react-hot-toast';

export const Login: React.FC = () => {
  const [activePersona, setActivePersona] = useState<'store_login' | 'register_store'>('store_login');
  
  // Login fields
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { login } = useAuth();

  // Registration fields
  const [regShopName, setRegShopName] = useState('');
  const [regUsername, setRegUsername] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [showRegPassword, setShowRegPassword] = useState(false);
  const [regEmail, setRegEmail] = useState('');
  const [regPhone, setRegPhone] = useState('');
  const [regAddress, setRegAddress] = useState('');
  const [regGstin, setRegGstin] = useState('');

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsSubmitting(true);
      await login(username, password);
      toast.success('Welcome back to Swarna Khata!');
      window.location.href = '/';
    } catch (err: any) {
      const msg =
        err.response?.data?.error ||
        err.response?.data?.detail ||
        (err.code === 'ECONNABORTED' || err.message?.includes('timeout')
          ? 'Backend server took too long to respond. The Render free tier instance may be waking up from sleep. Please wait 30 seconds and try again.'
          : err.message || 'Invalid username or password');
      toast.error(msg, { duration: 6000 });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRegisterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Client-side validation
    if (!regShopName.trim()) {
      toast.error('Please enter your jewellery shop name');
      return;
    }
    if (!regUsername.trim() || regUsername.trim().length < 3) {
      toast.error('Owner username must be at least 3 characters');
      return;
    }
    const cleanPhone = regPhone.trim().replace(/\D/g, '');
    if (cleanPhone.length < 10) {
      toast.error('Please enter a valid 10-digit mobile number');
      return;
    }
    const cleanGstin = regGstin.trim().toUpperCase();
    if (cleanGstin && !/^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}Z[A-Z\d]{1}$/.test(cleanGstin)) {
      toast.error('Invalid GSTIN format (e.g. 29AAAAA0000A1Z5)');
      return;
    }

    const policy = validatePasswordPolicy(regPassword);
    if (!policy.isValid) {
      toast.error(policy.errors[0] || 'Password does not meet Jewellery Shield policy');
      return;
    }

    try {
      setIsSubmitting(true);

      // Ensure no stale session or tenant context interferes with onboarding
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('tenant_schema');
      localStorage.removeItem('user_info');

      const res = await api.post(
        '/tenants/register-store/',
        {
          shop_name: regShopName.trim(),
          owner_username: regUsername.trim(),
          owner_password: regPassword,
          owner_email: regEmail.trim(),
          owner_phone: regPhone.trim(),
          address: regAddress.trim(),
          gstin: regGstin.trim(),
        },
        {
          timeout: 240000, // 4-minute timeout for multi-tenant schema creation & migrations on remote DB
        }
      );

      const { access, refresh, schema_name } = res.data;
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      localStorage.setItem('tenant_schema', schema_name);

      // Fetch user profile
      try {
        const meRes = await api.get('/auth/me');
        localStorage.setItem('user_info', JSON.stringify(meRes.data));
      } catch {
        // fallback
        localStorage.setItem(
          'user_info',
          JSON.stringify({ username: regUsername, role: 'owner' })
        );
      }

      toast.success(`Store '${regShopName}' provisioned successfully!`);
      window.location.href = '/';
    } catch (err: any) {
      let msg = 'Failed to register new store';
      if (err.response?.data?.error) {
        msg = err.response.data.error;
      } else if (err.response?.data?.detail) {
        if (Array.isArray(err.response.data.detail)) {
          msg = err.response.data.detail.map((d: any) => d.msg || d.message).join(', ');
        } else if (typeof err.response.data.detail === 'string') {
          msg = err.response.data.detail;
        }
      } else if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
        msg = 'Database schema provisioning is taking longer than expected. Please wait a moment and try logging in, or try again.';
      } else if (err.message) {
        msg = err.message;
      }
      toast.error(msg, { duration: 8000 });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-slate-50 to-amber-100/30 flex items-center justify-center p-4">
      <div className="w-full max-w-lg bg-white rounded-3xl shadow-2xl border border-slate-200/80 p-8 space-y-6">
        {/* Brand Header */}
        <div className="text-center space-y-2">
          <div className="w-14 h-14 bg-gradient-to-tr from-amber-600 to-amber-400 rounded-2xl flex items-center justify-center mx-auto shadow-md shadow-amber-500/20">
            <Sparkles className="w-7 h-7 text-white" />
          </div>
          <h2 className="text-2xl font-black text-slate-900 tracking-tight">Swarna Khata Book</h2>
          <p className="text-xs text-slate-500 font-medium">
            Jewellery Shop ERP • Billing • Accounting • Multi-Tenant SaaS
          </p>
        </div>

        {/* Two Store Persona Selector Tabs */}
        <div className="grid grid-cols-2 gap-1.5 p-1 bg-slate-100 rounded-2xl text-xs font-bold">
          <button
            type="button"
            onClick={() => setActivePersona('store_login')}
            className={`py-2 px-1 rounded-xl transition flex items-center justify-center gap-1.5 ${
              activePersona === 'store_login'
                ? 'bg-white text-slate-900 shadow-xs'
                : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            <Store className="w-3.5 h-3.5 text-amber-600" />
            <span className="truncate">Store Sign In</span>
          </button>

          <button
            type="button"
            onClick={() => setActivePersona('register_store')}
            className={`py-2 px-1 rounded-xl transition flex items-center justify-center gap-1.5 ${
              activePersona === 'register_store'
                ? 'bg-white text-slate-900 shadow-xs'
                : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            <UserPlus className="w-3.5 h-3.5 text-amber-600" />
            <span className="truncate">Register Store</span>
          </button>
        </div>

        {/* Store Sign In Form */}
        {activePersona === 'store_login' && (
          <form onSubmit={handleLoginSubmit} className="space-y-4">
            <div className="bg-slate-50 p-3 rounded-xl border border-slate-200 text-xs text-slate-600 flex items-center gap-2">
              <Building2 className="w-4 h-4 text-amber-600 shrink-0" />
              <span>
                Showroom Portal: Sign in with your Shop Owner or Salesman account.
              </span>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                Username
              </label>
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-amber-500/20"
                placeholder="e.g. owner or ramesh_sales"
                autoComplete="username"
                autoFocus
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                Password
              </label>
              <div className="relative flex items-center">
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-2.5 pr-11 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-amber-500/20"
                  placeholder="••••••••"
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 text-slate-400 hover:text-slate-600 focus:outline-hidden cursor-pointer p-1"
                  title={showPassword ? 'Hide password' : 'Show password'}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? (
                    <EyeOff className="w-4 h-4 text-slate-500" />
                  ) : (
                    <Eye className="w-4 h-4 text-slate-400" />
                  )}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full flex items-center justify-center gap-2 py-3 bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-700 hover:to-amber-600 text-white font-bold rounded-xl shadow-md transition transform active:scale-98 disabled:opacity-50"
            >
              <span>{isSubmitting ? 'Signing in (connecting to backend)...' : 'Sign In to Store'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl flex items-center gap-2 text-xs text-amber-900">
              <ShieldCheck className="w-4 h-4 text-amber-700 shrink-0" />
              <span>
                <b>Demo Accounts:</b> Admin: <code className="font-bold">admin</code> /{' '}
                <code className="font-bold">admin123</code> | Cashier:{' '}
                <code className="font-bold">cashier</code>
              </span>
            </div>
          </form>
        )}

        {/* Persona 2: Self-Service Store Registration Form */}
        {activePersona === 'register_store' && (
          <form onSubmit={handleRegisterSubmit} className="space-y-3.5">
            <div className="bg-amber-50/70 p-3 rounded-xl border border-amber-200 text-xs text-amber-900 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-amber-700 shrink-0" />
              <span>
                Registers your jewellery store and instantly provisions an isolated PostgreSQL schema!
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div className="sm:col-span-2">
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                  Jewellery Shop Name *
                </label>
                <input
                  type="text"
                  required
                  value={regShopName}
                  onChange={(e) => setRegShopName(e.target.value)}
                  className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-amber-500/20"
                  placeholder="e.g. Sri Lakshmi Jewellers"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                  Owner Username *
                </label>
                <input
                  type="text"
                  required
                  value={regUsername}
                  onChange={(e) => setRegUsername(e.target.value)}
                  className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:bg-white focus:outline-hidden"
                  placeholder="e.g. lakshmi_owner"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                  Owner Phone *
                </label>
                <input
                  type="text"
                  required
                  value={regPhone}
                  onChange={(e) => setRegPhone(e.target.value)}
                  className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:bg-white focus:outline-hidden"
                  placeholder="e.g. 9876543210"
                />
              </div>

              <div className="sm:col-span-2">
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                  Owner Email
                </label>
                <input
                  type="email"
                  value={regEmail}
                  onChange={(e) => setRegEmail(e.target.value)}
                  className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:bg-white focus:outline-hidden"
                  placeholder="e.g. owner@jewellers.com"
                />
              </div>

              <div className="sm:col-span-2">
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                  Owner Password *
                </label>
                <div className="relative flex items-center">
                  <input
                    type={showRegPassword ? 'text' : 'password'}
                    required
                    value={regPassword}
                    onChange={(e) => setRegPassword(e.target.value)}
                    className="w-full px-3.5 py-2 pr-10 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-amber-500/20"
                    placeholder="e.g. Gold*Vault8"
                  />
                  <button
                    type="button"
                    onClick={() => setShowRegPassword(!showRegPassword)}
                    className="absolute right-2.5 text-slate-400 hover:text-slate-600 focus:outline-hidden cursor-pointer p-1"
                    title={showRegPassword ? 'Hide password' : 'Show password'}
                    aria-label={showRegPassword ? 'Hide password' : 'Show password'}
                  >
                    {showRegPassword ? (
                      <EyeOff className="w-4 h-4 text-slate-500" />
                    ) : (
                      <Eye className="w-4 h-4 text-slate-400" />
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* Live Password Policy Checklist */}
            <PasswordPolicyChecklist password={regPassword} showWhenEmpty={true} />

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                  Showroom Address
                </label>
                <input
                  type="text"
                  value={regAddress}
                  onChange={(e) => setRegAddress(e.target.value)}
                  className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:bg-white focus:outline-hidden"
                  placeholder="e.g. Main Market, Zaveri Bazaar"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                  GSTIN (Optional)
                </label>
                <input
                  type="text"
                  value={regGstin}
                  onChange={(e) => setRegGstin(e.target.value.toUpperCase())}
                  className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:bg-white focus:outline-hidden uppercase"
                  placeholder="29AAAAA0000A1Z5"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full flex items-center justify-center gap-2 py-3 bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-700 hover:to-amber-600 text-white font-bold rounded-xl shadow-md transition disabled:opacity-50 mt-2"
            >
              <span>{isSubmitting ? 'Provisioning Store & Schema...' : 'Create Jewellery Store Account'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        )}
      </div>
    </div>
  );
};
