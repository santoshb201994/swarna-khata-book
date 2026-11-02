import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import { KeyRound, ArrowRight, Eye, EyeOff, ShieldCheck, CheckCircle2 } from 'lucide-react';
import api from '../../api/client';
import { PasswordPolicyChecklist } from '../../components/PasswordPolicyChecklist';
import { validatePasswordPolicy } from '../../utils/passwordPolicy';
import toast from 'react-hot-toast';

export const ResetPasswordPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token') || '';

  const [isValidating, setIsValidating] = useState(true);
  const [tokenValid, setTokenValid] = useState(false);
  const [tokenError, setTokenError] = useState('');
  const [userEmail, setUserEmail] = useState('');

  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    if (!token) {
      setIsValidating(false);
      setTokenValid(false);
      setTokenError('No password reset token was provided in the link.');
      return;
    }

    const checkToken = async () => {
      try {
        const res = await api.post('/auth/verify-reset-token/', { token });
        if (res.data.valid) {
          setTokenValid(true);
          setUserEmail(res.data.email || '');
        } else {
          setTokenValid(false);
          setTokenError(res.data.error || 'This reset link has expired or is invalid.');
        }
      } catch (err: any) {
        setTokenValid(false);
        setTokenError(
          err.response?.data?.error ||
          'This password reset link is invalid or has expired. Please request a new one.'
        );
      } finally {
        setIsValidating(false);
      }
    };

    checkToken();
  }, [token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (newPassword !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    const policy = validatePasswordPolicy(newPassword);
    if (!policy.isValid) {
      toast.error(policy.errors[0] || 'Password does not meet Jewellery Shield policy');
      return;
    }

    try {
      setIsSubmitting(true);
      await api.post('/auth/reset-password/', {
        token,
        new_password: newPassword,
      });

      setIsComplete(true);
      toast.success('Password reset successfully! You can now sign in.');
    } catch (err: any) {
      const msg =
        err.response?.data?.error ||
        err.response?.data?.detail ||
        'Failed to reset password. The link may have expired.';
      toast.error(msg, { duration: 6000 });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-slate-50 to-amber-100/30 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white rounded-3xl shadow-2xl border border-slate-200/80 p-8 space-y-6">
        {/* Brand Header */}
        <div className="text-center space-y-2">
          <div className="w-14 h-14 bg-gradient-to-tr from-amber-600 to-amber-400 rounded-2xl flex items-center justify-center mx-auto shadow-md shadow-amber-500/20">
            <KeyRound className="w-7 h-7 text-white" />
          </div>
          <h2 className="text-2xl font-black text-slate-900 tracking-tight">Set New Password</h2>
          <p className="text-xs text-slate-500 font-medium">
            Swarna Khata Book • Jewellery Shield Security
          </p>
        </div>

        {/* Loading Token Validation State */}
        {isValidating && (
          <div className="py-8 text-center space-y-3">
            <div className="w-8 h-8 border-3 border-amber-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
            <p className="text-xs text-slate-600 font-medium">Verifying reset token security...</p>
          </div>
        )}

        {/* Invalid / Expired Token */}
        {!isValidating && !tokenValid && (
          <div className="space-y-4">
            <div className="p-4 bg-rose-50 border border-rose-200 rounded-2xl text-xs text-rose-800 space-y-2">
              <p className="font-bold">Link Expired or Invalid</p>
              <p>{tokenError}</p>
            </div>
            <Link
              to="/login"
              className="w-full py-3 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-xl text-center block text-sm transition"
            >
              Return to Sign In
            </Link>
          </div>
        )}

        {/* Reset Completed State */}
        {!isValidating && tokenValid && isComplete && (
          <div className="space-y-4 text-center">
            <div className="w-12 h-12 bg-emerald-100 rounded-2xl flex items-center justify-center mx-auto">
              <CheckCircle2 className="w-6 h-6 text-emerald-600" />
            </div>
            <h3 className="text-lg font-bold text-slate-900">Password Updated</h3>
            <p className="text-xs text-slate-600">
              Your password has been changed securely. You can now access your jewellery store with your new credentials.
            </p>
            <button
              type="button"
              onClick={() => navigate('/login')}
              className="w-full py-3 bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-700 hover:to-amber-600 text-white font-bold rounded-xl shadow-md transition cursor-pointer"
            >
              Sign In Now
            </button>
          </div>
        )}

        {/* Active Reset Password Form */}
        {!isValidating && tokenValid && !isComplete && (
          <form onSubmit={handleSubmit} className="space-y-4">
            {userEmail && (
              <div className="p-3 bg-amber-50/70 border border-amber-200 rounded-xl text-xs text-amber-900 flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-amber-700 shrink-0" />
                <span>
                  Resetting credentials for <b>{userEmail}</b>
                </span>
              </div>
            )}

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                New Password
              </label>
              <div className="relative flex items-center">
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="w-full px-4 py-2.5 pr-11 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-amber-500/20"
                  placeholder="e.g. Gold*Shield826"
                  autoFocus
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 text-slate-400 hover:text-slate-600 cursor-pointer p-1"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                Confirm New Password
              </label>
              <input
                type={showPassword ? 'text' : 'password'}
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-amber-500/20"
                placeholder="Re-enter password"
              />
            </div>

            {/* Live Policy Checklist */}
            <PasswordPolicyChecklist password={newPassword} showWhenEmpty={true} />

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full flex items-center justify-center gap-2 py-3 bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-700 hover:to-amber-600 text-white font-bold rounded-xl shadow-md transition disabled:opacity-50 cursor-pointer"
            >
              <span>{isSubmitting ? 'Updating Credentials...' : 'Save New Password'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <div className="text-center">
              <Link to="/login" className="text-xs text-slate-500 hover:text-slate-800 font-medium">
                Cancel and return to Sign In
              </Link>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
