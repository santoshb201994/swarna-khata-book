import { describe, it, expect } from 'vitest';
import { detectProductMetal, resolveProductRate } from '../metalRateHelper';
import type { Product, GoldRate } from '../../../types';

describe('metalRateHelper', () => {
  const baseProduct: Product = {
    id: 1,
    name: 'Standard Gold Ring',
    sku: 'SKU-RNG-001',
    category: 1,
    category_name: 'Rings',
    purity: 1,
    purity_name: '22KT (916)',
    gross_weight: '5.500',
    stone_weight: '0.000',
    other_weight: '0.000',
    net_weight: '5.500',
    making_charge_type: 'per_gram',
    making_charge_value: '450.00',
    description: 'Gold ring',
    hsn_code: '7113',
    huid: 'HUID123456',
    is_active: true,
    created_at: '2026-11-04T10:00:00Z',
  };

  describe('detectProductMetal', () => {
    it('detects Silver from purity name', () => {
      const prod: Product = { ...baseProduct, purity_name: 'Silver 925' };
      const res = detectProductMetal(prod);
      expect(res.metalType).toBe('silver');
      expect(res.purityLabel).toBe('Silver 925');
    });

    it('detects Silver from keywords like payal / anklet / chandi', () => {
      const prod: Product = { ...baseProduct, name: 'Traditional Chandi Payal', category_name: 'Silver Anklet' };
      const res = detectProductMetal(prod);
      expect(res.metalType).toBe('silver');
    });

    it('detects Platinum from keywords', () => {
      const prod: Product = { ...baseProduct, name: 'Men Platinum Band', purity_name: 'Pt 950' };
      const res = detectProductMetal(prod);
      expect(res.metalType).toBe('platinum');
    });

    it('detects 24KT Gold', () => {
      const prod: Product = { ...baseProduct, purity_name: '24KT (999)', name: 'Pure Gold Coin' };
      const res = detectProductMetal(prod);
      expect(res.metalType).toBe('gold');
      expect(res.purityLabel).toContain('24KT');
    });

    it('detects 18KT Gold', () => {
      const prod: Product = { ...baseProduct, purity_name: '18KT (750)', name: 'Diamond Ring' };
      const res = detectProductMetal(prod);
      expect(res.metalType).toBe('gold');
      expect(res.purityLabel).toContain('18KT');
    });

    it('defaults to 22KT gold for unrecognized keywords', () => {
      const prod: Product = { ...baseProduct, purity_name: '22K' };
      const res = detectProductMetal(prod);
      expect(res.metalType).toBe('gold');
      expect(res.purityLabel).toBe('22K');
    });
  });

  describe('resolveProductRate', () => {
    const mockRates: GoldRate[] = [
      { id: 1, purity: 1, purity_id: 1, purity_name: '22KT', rate_per_gram: '7150.00', effective_date: '2026-11-04', is_current: true },
      { id: 2, purity: 2, purity_id: 2, purity_name: '24KT', rate_per_gram: '7800.00', effective_date: '2026-11-04', is_current: true },
      { id: 3, purity: 3, purity_id: 3, purity_name: 'Silver 925', rate_per_gram: '98.00', effective_date: '2026-11-04', is_current: true },
      { id: 4, purity: 4, purity_id: 4, purity_name: '18KT', rate_per_gram: '5850.00', effective_date: '2026-11-04', is_current: true },
    ];

    it('resolves direct purity ID match correctly', () => {
      const prod: Product = { ...baseProduct, purity: 1, purity_name: '22KT' };
      const resolved = resolveProductRate(prod, mockRates);
      expect(resolved.rate).toBe(7150);
      expect(resolved.metalType).toBe('gold');
    });

    it('guarantees silver is never billed at gold rate', () => {
      const silverProd: Product = {
        ...baseProduct,
        id: 99,
        name: 'Silver Kolusu Payal',
        category_name: 'Silver Ornaments',
        purity: 3,
        purity_name: 'Silver 925',
      };
      const resolved = resolveProductRate(silverProd, mockRates);
      expect(resolved.metalType).toBe('silver');
      expect(resolved.rate).toBe(98);
      expect(resolved.rate).toBeLessThan(500); // Silver is well under gold price
    });

    it('falls back to rateMapByName when ID is not present', () => {
      const rateMap = { '18KT': 5850, '22KT': 7150 };
      const prod: Product = { ...baseProduct, purity: 999, purity_name: '18KT' };
      const resolved = resolveProductRate(prod, [], rateMap);
      expect(resolved.rate).toBe(5850);
    });
  });
});
