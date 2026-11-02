import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Sparkles, ArrowRight, ShieldCheck, Store, UserPlus, Building2, Eye, EyeOff, Mail, KeyRound, CheckCircle2, RotateCw } from 'lucide-react';
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

  // Async Provisioning progress state
  const [provisioningState, setProvisioningState] = useState<{
    isProvisioning: boolean;
    schemaName: string;
    shopName: string;
    progress: number;
    message: string;
  } | null>(null);

  // Forgot Password modal fields
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [forgotEmail, setForgotEmail] = useState('');
  const [forgotSubmitting, setForgotSubmitting] = useState(false);
  const [forgotSent, setForgotSent] = useState(false);

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
          ? 'Backend server took too long to respond. The instance may be waking up from sleep. Please wait 30 seconds and try again.'
          : err.message || 'Invalid username or password');
      toast.error(msg, { duration: 6000 });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleForgotPasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!forgotEmail.trim() || !forgotEmail.includes('@')) {
      toast.error('Please enter a valid email address');
      return;
    }

    try {
      setForgotSubmitting(true);
      await api.post('/auth/forgot-password/', { email: forgotEmail.trim() });
      setForgotSent(true);
      toast.success('Reset instructions sent to your email.');
    } catch (err: any) {
      // Always show generic message to prevent account enumeration
      setForgotSent(true);
      toast.success('If an account exists, instructions have been sent.');
    } finally {
      setForgotSubmitting(false);
    }
  };

  const finishStoreLogin = async (
    access: string,
    refresh: string,
    schemaName: string,
    ownerUsername: string,
    shopName: string
  ) => {
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    localStorage.setItem('tenant_schema', schemaName);

    try {
      const meRes = await api.get('/auth/me');
      localStorage.setItem('user_info', JSON.stringify(meRes.data));
    } catch {
      localStorage.setItem(
        'user_info',
        JSON.stringify({ username: ownerUsername, role: 'owner', tenant_schema: schemaName })
      );
    }

    toast.success(`Store '${shopName}' provisioned successfully!`);
    window.location.href = '/';
  };

  const handleRegisterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

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

      // Clean slate before store registration
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('tenant_schema');
      localStorage.removeItem('user_info');

      const res = await api.post('/tenants/register-store/', {
        shop_name: regShopName.trim(),
        owner_username: regUsername.trim(),
        owner_password: regPassword,
        owner_email: regEmail.trim(),
        owner_phone: regPhone.trim(),
        address: regAddress.trim(),
        gstin: regGstin.trim(),
      });

      const { schema_name, provisioning_status, access, refresh } = res.data;

      // If already active (e.g. fast sync or idempotent replay)
      if (provisioning_status === 'active' && access) {
        await finishStoreLogin(access, refresh, schema_name, regUsername, regShopName);
        return;
      }

      // Start non-blocking polling state
      setProvisioningState({
        isProvisioning: true,
        schemaName: schema_name,
        shopName: regShopName.trim(),
        progress: 20,
        message: 'Creating isolated PostgreSQL schema...',
      });

      let attempts = 0;
      const pollInterval = setInterval(async () => {
        attempts++;
        try {
          const statusRes = await api.get(`/tenants/status/${schema_name}/`);
          const statusData = statusRes.data;

          if (statusData.provisioning_status === 'active') {
            clearInterval(pollInterval);
            setProvisioningState((prev) =>
              prev ? { ...prev, progress: 100, message: 'Store activated! Redirecting...' } : null
            );
            await finishStoreLogin(
              statusData.access,
              statusData.refresh,
              schema_name,
              regUsername,
              regShopName
            );
          } else if (statusData.provisioning_status === 'failed') {
            clearInterval(pollInterval);
            setProvisioningState(null);
            setIsSubmitting(false);
            toast.error(statusData.error || 'Store provisioning failed.');
          } else {
            // Still in progress: animate progress indicator smoothly
            const progressVal = Math.min(20 + attempts * 4, 94);
            const stepMsg =
              attempts > 18
                ? 'Seeding default categories, purities, and gold rates...'
                : attempts > 8
                ? 'Applying multi-tenant database migrations...'
                : 'Creating isolated PostgreSQL schema...';
            setProvisioningState((prev) =>
              prev ? { ...prev, progress: progressVal, message: stepMsg } : null
            );
          }
        } catch (pollErr: any) {
          if (pollErr.response?.data?.provisioning_status === 'failed') {
            clearInterval(pollInterval);
            setProvisioningState(null);
            setIsSubmitting(false);
            toast.error(pollErr.response?.data?.error || 'Store provisioning encountered an issue.');
          }
        }

        if (attempts >= 90) { // 3.5 minutes max
          clearInterval(pollInterval);
          setProvisioningState(null);
          setIsSubmitting(false);
          toast.error('Provisioning is taking longer than usual. Please try logging in with your owner credentials in a moment.');
        }
      }, 2500);

    } catch (err: any) {
      setIsSubmitting(false);
      let msg = 'Failed to register new store';
      if (err.response?.data?.error) {
        msg = err.response.data.error;
      } else if (err.response?.data?.detail) {
        if (Array.isArray(err.response.data.detail)) {
          msg = err.response.data.detail.map((d: any) => d.msg || d.message).join(', ');
        } else if (typeof err.response.data.detail === 'string') {
          msg = err.response.data.detail;
        }
      } else if (err.message) {
        msg = err.message;
      }
      toast.error(msg, { duration: 8000 });
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

        {/* Persona Selector Tabs */}
        {!provisioningState && !showForgotPassword && (
          <div className="grid grid-cols-2 gap-1.5 p-1 bg-slate-100 rounded-2xl text-xs font-bold">
            <button
              type="button"
              onClick={() => setActivePersona('store_login')}
              className={`py-2 px-1 rounded-xl transition flex items-center justify-center gap-1.5 cursor-pointer ${
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
              className={`py-2 px-1 rounded-xl transition flex items-center justify-center gap-1.5 cursor-pointer ${
                activePersona === 'register_store'
                  ? 'bg-white text-slate-900 shadow-xs'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              <UserPlus className="w-3.5 h-3.5 text-amber-600" />
              <span className="truncate">Register Store</span>
            </button>
          </div>
        )}

        {/* Forgot Password View */}
        {showForgotPassword && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-slate-900 font-bold text-base">
              <KeyRound className="w-5 h-5 text-amber-600" />
              <span>Reset Your Store Password</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              Enter your registered account email. If the email exists in our system, we will send you a secure, single-use reset link via Brevo transactional email.
            </p>

            {forgotSent ? (
              <div className="space-y-4 text-center py-4">
                <div className="w-12 h-12 bg-emerald-100 rounded-2xl flex items-center justify-center mx-auto">
                  <CheckCircle2 className="w-6 h-6 text-emerald-600" />
                </div>
                <h4 className="text-sm font-bold text-slate-900">Email Dispatched</h4>
                <p className="text-xs text-slate-600">
                  If an account is associated with <b>{forgotEmail}</b>, you will receive password reset instructions shortly. Please check your inbox and spam folder.
                </p>
                <button
                  type="button"
                  onClick={() => {
                    setShowForgotPassword(false);
                    setForgotSent(false);
                    setForgotEmail('');
                  }}
                  className="w-full py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-xl text-xs transition cursor-pointer"
                >
                  Return to Sign In
                </button>
              </div>
            ) : (
              <form onSubmit={handleForgotPasswordSubmit} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                    Registered Email Address *
                  </label>
                  <div className="relative flex items-center">
                    <input
                      type="email"
                      required
                      value={forgotEmail}
                      onChange={(e) => setForgotEmail(e.target.value)}
                      className="w-full px-4 py-2.5 pl-10 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-amber-500/20"
                      placeholder="owner@jewellers.com"
                      autoFocus
                    />
                    <Mail className="w-4 h-4 text-slate-400 absolute left-3 pointer-events-none" />
                  </div>
                </div>

                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => {
                      setShowForgotPassword(false);
                      setForgotEmail('');
                    }}
                    className="w-1/2 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl text-xs transition cursor-pointer"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={forgotSubmitting}
                    className="w-1/2 py-2.5 bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-700 hover:to-amber-600 text-white font-bold rounded-xl text-xs shadow-md transition disabled:opacity-50 cursor-pointer"
                  >
                    {forgotSubmitting ? 'Sending...' : 'Send Reset Link'}
                  </button>
                </div>
              </form>
            )}
          </div>
        )}

        {/* Live Provisioning Progress Card */}
        {provisioningState && (
          <div className="p-6 bg-amber-50/70 border border-amber-200 rounded-2xl space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-amber-500/10 rounded-xl flex items-center justify-center shrink-0">
                <RotateCw className="w-5 h-5 text-amber-600 animate-spin" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-slate-900">Provisioning '{provisioningState.shopName}'</h4>
                <p className="text-xs text-amber-900 font-medium">{provisioningState.message}</p>
              </div>
            </div>

            {/* Progress bar */}
            <div className="w-full bg-amber-200/60 rounded-full h-2.5 overflow-hidden">
              <div
                className="bg-gradient-to-r from-amber-500 to-amber-600 h-2.5 rounded-full transition-all duration-500 ease-out"
                style={{ width: `${provisioningState.progress}%` }}
              ></div>
            </div>

            <div className="flex justify-between text-[11px] text-slate-500 font-medium">
              <span>PostgreSQL Schema: <code className="font-bold text-slate-700">{provisioningState.schemaName}</code></span>
              <span>{provisioningState.progress}% complete</span>
            </div>
          </div>
        )}

        {/* Store Sign In Form */}
        {!showForgotPassword && !provisioningState && activePersona === 'store_login' && (
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
                placeholder="e.g. owner or admin"
                autoComplete="username"
                autoFocus
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="block text-xs font-bold text-slate-700 uppercase">
                  Password
                </label>
                <button
                  type="button"
                  onClick={() => setShowForgotPassword(true)}
                  className="text-xs text-amber-700 hover:text-amber-800 font-semibold cursor-pointer"
                >
                  Forgot Password?
                </button>
              </div>
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
                  className="absolute right-3 text-slate-400 hover:text-slate-600 cursor-pointer p-1"
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
              className="w-full flex items-center justify-center gap-2 py-3 bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-700 hover:to-amber-600 text-white font-bold rounded-xl shadow-md transition transform active:scale-98 disabled:opacity-50 cursor-pointer"
            >
              <span>{isSubmitting ? 'Signing in...' : 'Sign In to Store'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            {/* Single Temporary Test Account Helper */}
            <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-center justify-between text-xs text-slate-700">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-amber-600 shrink-0" />
                <span>
                  <b>Test Account:</b> <code className="font-bold bg-slate-200 px-1 py-0.5 rounded text-slate-800">admin</code> / <code className="font-bold bg-slate-200 px-1 py-0.5 rounded text-slate-800">admin123</code>
                </span>
              </div>
              <button
                type="button"
                onClick={() => {
                  setUsername('admin');
                  setPassword('admin123');
                }}
                className="text-amber-700 hover:text-amber-800 font-bold underline cursor-pointer text-xs ml-2"
              >
                Auto Fill
              </button>
            </div>
          </form>
        )}

        {/* Self-Service Store Registration Form */}
        {!showForgotPassword && !provisioningState && activePersona === 'register_store' && (
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
                    className="absolute right-2.5 text-slate-400 hover:text-slate-600 cursor-pointer p-1"
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
              className="w-full flex items-center justify-center gap-2 py-3 bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-700 hover:to-amber-600 text-white font-bold rounded-xl shadow-md transition disabled:opacity-50 mt-2 cursor-pointer"
            >
              <span>{isSubmitting ? 'Starting Store Provisioning...' : 'Create Jewellery Store Account'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        )}
      </div>
    </div>
  );
};
