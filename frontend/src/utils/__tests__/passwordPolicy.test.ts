import { describe, it, expect } from 'vitest';
import { validatePasswordPolicy } from '../passwordPolicy';

describe('Jewellery Shield Password Policy', () => {
  it('accepts compliant passwords', () => {
    const valid = 'Karat*Vault9';
    const result = validatePasswordPolicy(valid);
    expect(result.isValid).toBe(true);
    expect(result.errors).toHaveLength(0);
    expect(result.criteria.minLength).toBe(true);
    expect(result.criteria.hasUpper).toBe(true);
    expect(result.criteria.hasLower).toBe(true);
    expect(result.criteria.hasNumber).toBe(true);
    expect(result.criteria.hasSpecial).toBe(true);
    expect(result.criteria.noConsecutiveDuplicates).toBe(true);
    expect(result.criteria.noSequentialRuns).toBe(true);
  });

  it('rejects passwords shorter than 8 characters', () => {
    const res = validatePasswordPolicy('Ab1@xyz');
    expect(res.isValid).toBe(false);
    expect(res.criteria.minLength).toBe(false);
    expect(res.errors).toContain('Password must be between 8 and 64 characters.');
  });

  it('rejects passwords without special characters', () => {
    const res = validatePasswordPolicy('SecurePass12');
    expect(res.isValid).toBe(false);
    expect(res.criteria.hasSpecial).toBe(false);
  });

  it('rejects consecutive duplicates (e.g. "aa", "11", "@@")', () => {
    const res = validatePasswordPolicy('Swarna**1234');
    expect(res.isValid).toBe(false);
    expect(res.criteria.noConsecutiveDuplicates).toBe(false);
    expect(res.errors.some(e => e.includes('consecutive duplicate'))).toBe(true);
  });

  it('rejects 3+ sequential numbers (e.g. "123", "789")', () => {
    const res = validatePasswordPolicy('Secure*123');
    expect(res.isValid).toBe(false);
    expect(res.criteria.noSequentialRuns).toBe(false);
  });

  it('rejects 3+ sequential letters (e.g. "abc", "xyz")', () => {
    const res = validatePasswordPolicy('Abc*Vault9');
    expect(res.isValid).toBe(false);
    expect(res.criteria.noSequentialRuns).toBe(false);
  });

  it('rejects disallowed characters outside whitelist', () => {
    const res = validatePasswordPolicy('Secure^Vault9'); // '^' not in @#$%*!&_
    expect(res.isValid).toBe(false);
    expect(res.criteria.noInvalidCharacters).toBe(false);
  });
});
