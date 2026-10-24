import React, { useState, useEffect } from 'react';
import {
  X,
  UserPlus,
  Users,
  KeyRound,
  UserCheck,
  UserX,
  Search,
} from 'lucide-react';
import api from '../../api/client';
import { PasswordPolicyChecklist } from '../../components/PasswordPolicyChecklist';
import { validatePasswordPolicy } from '../../utils/passwordPolicy';
import toast from 'react-hot-toast';

interface UserItem {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  phone: string;
  branch_id?: number;
  branch_name?: string;
  is_active: boolean;
}

interface StaffManagementModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentUserRole?: string;
}

export const StaffManagementModal: React.FC<StaffManagementModalProps> = ({
  isOpen,
  onClose,
  currentUserRole,
}) => {
  const [users, setUsers] = useState<UserItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [activeTab, setActiveTab] = useState<'list' | 'add'>('list');

  // Form states for adding new staff
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [role, setRole] = useState('staff');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Reset password modal state
  const [resetTargetUser, setResetTargetUser] = useState<UserItem | null>(null);
  const [newPassword, setNewPassword] = useState('');
  const [isResetting, setIsResetting] = useState(false);

  const fetchUsers = async () => {
    try {
      setIsLoading(true);
      const res = await api.get('/users/');
      setUsers(res.data);
    } catch {
      toast.error('Failed to load showroom staff');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchUsers();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleCreateStaff = async (e: React.FormEvent) => {
    e.preventDefault();
    const policy = validatePasswordPolicy(password);
    if (!policy.isValid) {
      toast.error(policy.errors[0] || 'Password does not meet Jewellery Shield policy');
      return;
    }

    try {
      setIsSubmitting(true);
      await api.post('/users/', {
        username: username.trim(),
        password,
        first_name: firstName.trim(),
        last_name: lastName.trim(),
        email: email.trim(),
        phone: phone.trim(),
        role,
      });

      toast.success(`Staff member '${username}' created successfully!`);
      setUsername('');
      setPassword('');
      setFirstName('');
      setLastName('');
      setEmail('');
      setPhone('');
      setRole('staff');
      setActiveTab('list');
      fetchUsers();
    } catch (err: any) {
      const msg = err.response?.data?.error || err.response?.data?.message || 'Failed to create staff member';
      toast.error(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleToggleStatus = async (user: UserItem) => {
    const nextStatus = !user.is_active;
    const actionName = nextStatus ? 'activate' : 'deactivate';
    if (!confirm(`Are you sure you want to ${actionName} access for '${user.username}'?`)) {
      return;
    }

    try {
      await api.post(`/users/${user.id}/toggle-status/`, { is_active: nextStatus });
      toast.success(`User '${user.username}' ${nextStatus ? 'activated' : 'deactivated'}.`);
      setUsers((prev) =>
        prev.map((u) => (u.id === user.id ? { ...u, is_active: nextStatus } : u))
      );
    } catch (err: any) {
      const msg = err.response?.data?.error || 'Action failed';
      toast.error(msg);
    }
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resetTargetUser) return;
    const policy = validatePasswordPolicy(newPassword);
    if (!policy.isValid) {
      toast.error(policy.errors[0] || 'Password does not meet policy');
      return;
    }

    try {
      setIsResetting(true);
      await api.post(`/users/${resetTargetUser.id}/reset-password/`, { new_password: newPassword });
      toast.success(`Password for '${resetTargetUser.username}' successfully reset.`);
      setResetTargetUser(null);
      setNewPassword('');
    } catch (err: any) {
      toast.error(err.response?.data?.error || 'Failed to reset password');
    } finally {
      setIsResetting(false);
    }
  };

  const filteredUsers = users.filter((u) =>
    u.username.toLowerCase().includes(search.toLowerCase()) ||
    u.first_name.toLowerCase().includes(search.toLowerCase()) ||
    u.role.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl shadow-2xl border border-slate-200 w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="p-5 border-b border-slate-200 flex items-center justify-between bg-gradient-to-r from-amber-50 to-slate-50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-700">
              <Users className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-black text-slate-900 tracking-tight flex items-center gap-2">
                Showroom Staff & Access Control
                <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 border border-amber-200">
                  Owner Dashboard
                </span>
              </h2>
              <p className="text-xs text-slate-500">
                Manage salesman credentials, POS access, and role permissions with strict policy controls.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Selector */}
        <div className="px-6 pt-3 flex gap-2 border-b border-slate-100 bg-white">
          <button
            onClick={() => setActiveTab('list')}
            className={`pb-3 px-3 text-xs font-bold border-b-2 flex items-center gap-2 transition ${
              activeTab === 'list'
                ? 'border-amber-600 text-amber-700'
                : 'border-transparent text-slate-400 hover:text-slate-600'
            }`}
          >
            <Users className="w-4 h-4" />
            <span>Staff Directory ({users.length})</span>
          </button>
          <button
            onClick={() => setActiveTab('add')}
            className={`pb-3 px-3 text-xs font-bold border-b-2 flex items-center gap-2 transition ${
              activeTab === 'add'
                ? 'border-amber-600 text-amber-700'
                : 'border-transparent text-slate-400 hover:text-slate-600'
            }`}
          >
            <UserPlus className="w-4 h-4" />
            <span>Add New Salesman / Staff</span>
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto flex-1 bg-slate-50/50">
          {activeTab === 'list' ? (
            <div className="space-y-4">
              {/* Search Bar */}
              <div className="relative">
                <Search className="w-4 h-4 absolute left-3.5 top-3 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search staff by username, name, or role..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-white border border-slate-200 rounded-xl text-xs focus:ring-2 focus:ring-amber-500/20 focus:outline-hidden"
                />
              </div>

              {isLoading ? (
                <div className="py-12 text-center text-xs text-slate-400">Loading showroom staff...</div>
              ) : filteredUsers.length === 0 ? (
                <div className="py-12 text-center text-xs text-slate-400">No staff accounts found.</div>
              ) : (
                <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden divide-y divide-slate-100">
                  {filteredUsers.map((u) => {
                    const isSelf = currentUserRole === 'owner' && u.role === 'owner';
                    return (
                      <div
                        key={u.id}
                        className={`p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 transition ${
                          !u.is_active ? 'bg-slate-50/80 opacity-70' : 'hover:bg-amber-50/30'
                        }`}
                      >
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-sm text-slate-900">{u.username}</span>
                            <span
                              className={`text-[10px] font-black uppercase px-2 py-0.5 rounded-full border ${
                                u.role === 'owner'
                                  ? 'bg-purple-50 text-purple-700 border-purple-200'
                                  : u.role === 'manager'
                                  ? 'bg-blue-50 text-blue-700 border-blue-200'
                                  : u.role === 'accountant'
                                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                                  : 'bg-amber-50 text-amber-700 border-amber-200'
                              }`}
                            >
                              {u.role === 'staff' ? 'Salesman' : u.role}
                            </span>
                            <span
                              className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                                u.is_active
                                  ? 'bg-emerald-100 text-emerald-800'
                                  : 'bg-rose-100 text-rose-800'
                              }`}
                            >
                              {u.is_active ? 'Active' : 'Deactivated'}
                            </span>
                          </div>
                          <div className="text-xs text-slate-500 flex flex-wrap gap-x-4">
                            {u.first_name && <span>Name: {u.first_name} {u.last_name}</span>}
                            {u.phone && <span>Phone: {u.phone}</span>}
                            {u.email && <span>Email: {u.email}</span>}
                          </div>
                        </div>

                        {/* Actions */}
                        <div className="flex items-center gap-2 self-end sm:self-center">
                          <button
                            onClick={() => {
                              setResetTargetUser(u);
                              setNewPassword('');
                            }}
                            className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition"
                            title="Reset Password"
                          >
                            <KeyRound className="w-3.5 h-3.5 text-slate-500" />
                            <span>Reset Pwd</span>
                          </button>

                          {!isSelf && (
                            <button
                              onClick={() => handleToggleStatus(u)}
                              className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition ${
                                u.is_active
                                  ? 'bg-rose-50 text-rose-700 hover:bg-rose-100 border border-rose-200'
                                  : 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200'
                              }`}
                            >
                              {u.is_active ? (
                                <>
                                  <UserX className="w-3.5 h-3.5" />
                                  <span>Deactivate</span>
                                </>
                              ) : (
                                <>
                                  <UserCheck className="w-3.5 h-3.5" />
                                  <span>Activate</span>
                                </>
                              )}
                            </button>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          ) : (
            /* Add Staff Form */
            <form onSubmit={handleCreateStaff} className="bg-white p-6 rounded-2xl border border-slate-200 space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                    Username *
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. ramesh_sales"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-amber-500/20"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                    Role *
                  </label>
                  <select
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-amber-500/20"
                  >
                    <option value="staff">Salesman / Cashier (POS & Billing Only)</option>
                    <option value="manager">Showroom Manager (Operations & Rates)</option>
                    <option value="accountant">Accountant (Daybook & Ledgers)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                    First Name
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Ramesh"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:bg-white focus:outline-hidden"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                    Phone Number
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. 9876543210"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:bg-white focus:outline-hidden"
                  />
                </div>

                <div className="sm:col-span-2">
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                    Initial Password *
                  </label>
                  <input
                    type="password"
                    required
                    placeholder="Must meet Jewellery Shield policy (e.g. Gold*Vault8)"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-amber-500/20"
                  />
                </div>
              </div>

              {/* Password Policy Live Checklist */}
              <PasswordPolicyChecklist password={password} showWhenEmpty={true} />

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setActiveTab('list')}
                  className="px-4 py-2 border border-slate-200 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-5 py-2 bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-700 hover:to-amber-600 text-white text-xs font-bold rounded-xl shadow-md transition disabled:opacity-50"
                >
                  {isSubmitting ? 'Creating Staff Account...' : 'Create Staff Member'}
                </button>
              </div>
            </form>
          )}
        </div>

        {/* Reset Password Modal */}
        {resetTargetUser && (
          <div className="fixed inset-0 z-60 bg-slate-950/70 backdrop-blur-xs flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl shadow-xl border border-slate-200 w-full max-w-md p-6 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-sm text-slate-900 flex items-center gap-2">
                  <KeyRound className="w-4 h-4 text-amber-600" />
                  Reset Password for {resetTargetUser.username}
                </h3>
                <button
                  onClick={() => setResetTargetUser(null)}
                  className="text-slate-400 hover:text-slate-600"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <form onSubmit={handleResetPassword} className="space-y-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                    New Password
                  </label>
                  <input
                    type="password"
                    required
                    placeholder="Must meet policy (e.g. Safe*Pass9)"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-amber-500/20"
                  />
                </div>

                <PasswordPolicyChecklist password={newPassword} showWhenEmpty={true} />

                <div className="flex justify-end gap-2 pt-2">
                  <button
                    type="button"
                    onClick={() => setResetTargetUser(null)}
                    className="px-3 py-1.5 border border-slate-200 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isResetting}
                    className="px-4 py-1.5 bg-amber-600 hover:bg-amber-700 text-white rounded-xl text-xs font-bold shadow-md transition disabled:opacity-50"
                  >
                    {isResetting ? 'Saving...' : 'Set New Password'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
