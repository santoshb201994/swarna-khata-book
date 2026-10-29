import React from 'react';
import { Check, X, ShieldAlert } from 'lucide-react';
import { validatePasswordPolicy, ALLOWED_SPECIAL_DISPLAY } from '../utils/passwordPolicy';

interface PasswordPolicyChecklistProps {
  password: string;
  showWhenEmpty?: boolean;
}

export const PasswordPolicyChecklist: React.FC<PasswordPolicyChecklistProps> = ({
  password,
  showWhenEmpty = false,
}) => {
  if (!password && !showWhenEmpty) {
    return null;
  }

  const { criteria, errors } = validatePasswordPolicy(password);

  const rules = [
    { label: '8 to 64 characters', passed: criteria.minLength },
    { label: 'At least 1 uppercase letter (A-Z)', passed: criteria.hasUpper },
    { label: 'At least 1 lowercase letter (a-z)', passed: criteria.hasLower },
    { label: 'At least 1 number (0-9)', passed: criteria.hasNumber },
    { label: `1 special character from ${ALLOWED_SPECIAL_DISPLAY}`, passed: criteria.hasSpecial },
    { label: 'No consecutive duplicate characters (e.g. aa, 11)', passed: criteria.noConsecutiveDuplicates },
    { label: 'No sequential characters (e.g. abc, 123)', passed: criteria.noSequentialRuns },
    { label: 'Only allowed symbols (no quotes, backslashes, <>)', passed: criteria.noInvalidCharacters },
  ];

  return (
    <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-2 text-xs">
      <div className="flex items-center justify-between font-bold text-slate-700">
        <span className="flex items-center gap-1.5">
          <ShieldAlert className="w-3.5 h-3.5 text-amber-600" />
          Jewellery Shield Password Policy:
        </span>
        <span className={errors.length === 0 && password.length > 0 ? 'text-emerald-600 font-black' : 'text-slate-400'}>
          {rules.filter((r) => r.passed).length}/{rules.length} requirements met
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5 pt-1">
        {rules.map((rule, idx) => (
          <div
            key={idx}
            className={`flex items-center gap-1.5 transition-colors ${
              rule.passed
                ? 'text-emerald-700 font-medium'
                : password.length > 0
                ? 'text-rose-600'
                : 'text-slate-500'
            }`}
          >
            {rule.passed ? (
              <span className="w-4 h-4 rounded-full bg-emerald-100 flex items-center justify-center shrink-0">
                <Check className="w-2.5 h-2.5 text-emerald-700 stroke-[3]" />
              </span>
            ) : (
              <span className="w-4 h-4 rounded-full bg-slate-200 flex items-center justify-center shrink-0">
                <X className="w-2.5 h-2.5 text-slate-400 stroke-[2.5]" />
              </span>
            )}
            <span className="truncate">{rule.label}</span>
          </div>
        ))}
      </div>

      {errors.length > 0 && password.length > 0 && (
        <div className="text-[11px] text-rose-600 font-medium bg-rose-50 p-2 rounded-lg border border-rose-200 mt-2">
          {errors[0]}
        </div>
      )}
    </div>
  );
};
