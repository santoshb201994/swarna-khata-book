/**
 * Jewellery Shield Password Policy (Client-Side Mirror)
 *
 * Rules:
 * 1. Min 8 characters, max 64 characters.
 * 2. At least 1 uppercase letter (A-Z).
 * 3. At least 1 lowercase letter (a-z).
 * 4. At least 1 number (0-9).
 * 5. At least 1 special character from whitelisted set: @ # $ % * ! & _
 * 6. No disallowed characters outside [A-Za-z0-9@#$%*!&_].
 * 7. Avoid consecutive duplicate characters (e.g., 'aa', '11', '@@').
 * 8. Avoid consecutive sequential letters or numbers of length 3+ (e.g., 'abc', '123', 'cba', '321').
 */

export const ALLOWED_SPECIAL_CHARS = '@#$%*!&_';
export const ALLOWED_SPECIAL_DISPLAY = '@ # $ % * ! & _';

export interface PasswordCriteria {
  minLength: boolean;
  hasUpper: boolean;
  hasLower: boolean;
  hasNumber: boolean;
  hasSpecial: boolean;
  noConsecutiveDuplicates: boolean;
  noSequentialRuns: boolean;
  noInvalidCharacters: boolean;
}

export interface PasswordValidationResult {
  isValid: boolean;
  criteria: PasswordCriteria;
  errors: string[];
}

export function validatePasswordPolicy(password: string): PasswordValidationResult {
  const criteria: PasswordCriteria = {
    minLength: password.length >= 8 && password.length <= 64,
    hasUpper: /[A-Z]/.test(password),
    hasLower: /[a-z]/.test(password),
    hasNumber: /\d/.test(password),
    hasSpecial: /[@#$%*!&_]/.test(password),
    noConsecutiveDuplicates: true,
    noSequentialRuns: true,
    noInvalidCharacters: true,
  };

  const errors: string[] = [];

  if (!criteria.minLength) {
    errors.push('Password must be between 8 and 64 characters.');
  }
  if (!criteria.hasUpper) {
    errors.push('Must contain at least 1 uppercase letter (A-Z).');
  }
  if (!criteria.hasLower) {
    errors.push('Must contain at least 1 lowercase letter (a-z).');
  }
  if (!criteria.hasNumber) {
    errors.push('Must contain at least 1 number (0-9).');
  }

  // Check invalid/disallowed characters
  const allowedSet = new Set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%*!&_');
  for (let i = 0; i < password.length; i++) {
    if (!allowedSet.has(password[i])) {
      criteria.noInvalidCharacters = false;
      errors.push(`Disallowed character '${password[i]}'. Only alphanumeric and ${ALLOWED_SPECIAL_DISPLAY} are permitted.`);
      break;
    }
  }

  if (!criteria.hasSpecial) {
    errors.push(`Must contain at least 1 special character from: ${ALLOWED_SPECIAL_DISPLAY}`);
  }

  // Check consecutive duplicate characters (case-insensitive for letters)
  const lowerPass = password.toLowerCase();
  for (let i = 0; i < lowerPass.length - 1; i++) {
    if (lowerPass[i] === lowerPass[i + 1]) {
      criteria.noConsecutiveDuplicates = false;
      errors.push(`Avoid consecutive duplicate characters ('${password[i]}${password[i + 1]}').`);
      break;
    }
  }

  // Check 3+ sequential letters or numbers (ascending or descending)
  for (let i = 0; i < lowerPass.length - 2; i++) {
    const c1 = lowerPass[i];
    const c2 = lowerPass[i + 1];
    const c3 = lowerPass[i + 2];

    // Numbers
    if (/\d/.test(c1) && /\d/.test(c2) && /\d/.test(c3)) {
      const d1 = parseInt(c1, 10);
      const d2 = parseInt(c2, 10);
      const d3 = parseInt(c3, 10);
      if ((d2 === d1 + 1 && d3 === d2 + 1) || (d2 === d1 - 1 && d3 === d2 - 1)) {
        criteria.noSequentialRuns = false;
        errors.push(`Avoid consecutive sequential numbers ('${password[i]}${password[i + 1]}${password[i + 2]}').`);
        break;
      }
    }

    // Letters
    if (/[a-z]/.test(c1) && /[a-z]/.test(c2) && /[a-z]/.test(c3)) {
      const o1 = c1.charCodeAt(0);
      const o2 = c2.charCodeAt(0);
      const o3 = c3.charCodeAt(0);
      if ((o2 === o1 + 1 && o3 === o2 + 1) || (o2 === o1 - 1 && o3 === o2 - 1)) {
        criteria.noSequentialRuns = false;
        errors.push(`Avoid consecutive sequential letters ('${password[i]}${password[i + 1]}${password[i + 2]}').`);
        break;
      }
    }
  }

  const isValid =
    criteria.minLength &&
    criteria.hasUpper &&
    criteria.hasLower &&
    criteria.hasNumber &&
    criteria.hasSpecial &&
    criteria.noConsecutiveDuplicates &&
    criteria.noSequentialRuns &&
    criteria.noInvalidCharacters;

  return { isValid, criteria, errors };
}
