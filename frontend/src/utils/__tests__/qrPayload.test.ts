import { describe, it, expect } from 'vitest';
import { getQRPayload, parseQRPayload } from '../qrPayload';

describe('QR Payload Parser & Formatter', () => {
  const sampleUuid = 'a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d';

  describe('getQRPayload', () => {
    it('prepends SKB: prefix to raw UUID', () => {
      expect(getQRPayload(sampleUuid)).toBe(`SKB:${sampleUuid}`);
    });

    it('does not double prefix if SKB: already present', () => {
      expect(getQRPayload(`SKB:${sampleUuid}`)).toBe(`SKB:${sampleUuid}`);
    });
  });

  describe('parseQRPayload', () => {
    it('parses canonical SKB:<UUID> format', () => {
      const parsed = parseQRPayload(`SKB:${sampleUuid}`);
      expect(parsed.isCanonical).toBe(true);
      expect(parsed.qrToken).toBe(sampleUuid.toLowerCase());
      expect(parsed.isTray).toBe(false);
    });

    it('parses bare UUID without prefix', () => {
      const parsed = parseQRPayload(sampleUuid);
      expect(parsed.isCanonical).toBe(true);
      expect(parsed.qrToken).toBe(sampleUuid.toLowerCase());
      expect(parsed.isTray).toBe(false);
    });

    it('detects Tray QR codes starting with TRAY-', () => {
      const trayPayload = 'TRAY-2026-001';
      const parsed = parseQRPayload(trayPayload);
      expect(parsed.isTray).toBe(true);
      expect(parsed.trayCode).toBe('TRAY-2026-001');
      expect(parsed.isCanonical).toBe(false);
    });

    it('parses legacy JSON payload', () => {
      const jsonPayload = JSON.stringify({ sku: 'RING-GOLD-01', name: 'Ring' });
      const parsed = parseQRPayload(jsonPayload);
      expect(parsed.sku).toBe('RING-GOLD-01');
    });

    it('parses legacy plain text SKU fallback', () => {
      const parsed = parseQRPayload('SKU-NECK-100');
      expect(parsed.isCanonical).toBe(false);
      expect(parsed.sku).toBe('SKU-NECK-100');
    });

    it('handles empty or whitespace inputs gracefully', () => {
      const parsed = parseQRPayload('   ');
      expect(parsed.isCanonical).toBe(false);
      expect(parsed.qrToken).toBeNull();
      expect(parsed.sku).toBeNull();
    });
  });
});
