import type { Product, GoldRate } from '../../types';

export type MetalType = 'gold' | 'silver' | 'platinum' | 'other';

export interface ResolvedMetalRate {
  rate: number;
  metalType: MetalType;
  purityLabel: string;
}

/**
 * Normalizes text for keyword matching by removing special characters and lowering case.
 */
function clean(str?: string | null): string {
  return (str || '').toLowerCase().trim();
}

/**
 * Determines whether a product belongs to a specific metal category (Silver, Platinum, or Gold).
 * Checks purity name, category name, product name, and SKU.
 */
export function detectProductMetal(product: Product): { metalType: MetalType; purityLabel: string } {
  const pName = clean(product.purity_name);
  const cName = clean(product.category_name);
  const prodName = clean(product.name);
  const sku = clean(product.sku);
  const combined = `${pName} ${cName} ${prodName} ${sku}`;

  // 1. Check for Silver keywords
  const isSilver = /(silver|chandi|925|\bslv\b|\bsil\b|payal|kolusu|anklet|silver\s*ornament)/i.test(combined);
  if (isSilver) {
    const purity = product.purity_name || 'Silver (925)';
    return { metalType: 'silver', purityLabel: purity };
  }

  // 2. Check for Platinum keywords
  const isPlatinum = /(platinum|\bpt\b|950)/i.test(combined);
  if (isPlatinum) {
    const purity = product.purity_name || 'Platinum 950';
    return { metalType: 'platinum', purityLabel: purity };
  }

  // 3. Gold Karat breakdown
  if (/(24kt|24k|999|pure\s*gold)/i.test(combined)) {
    return { metalType: 'gold', purityLabel: product.purity_name || '24KT (999)' };
  }
  if (/(18kt|18k|750)/i.test(combined)) {
    return { metalType: 'gold', purityLabel: product.purity_name || '18KT (750)' };
  }
  if (/(14kt|14k|585)/i.test(combined)) {
    return { metalType: 'gold', purityLabel: product.purity_name || '14KT (585)' };
  }

  // Default to standard 22KT gold
  return { metalType: 'gold', purityLabel: product.purity_name || '22KT (916)' };
}

/**
 * Resolves the applicable metal rate (₹/gram) for a product based on live/scraped store rates.
 * Guarantees that items other than gold (e.g. Silver, Platinum) will NEVER be billed at the 22KT gold rate.
 */
export function resolveProductRate(
  product: Product,
  ratesList: GoldRate[] = [],
  rateMapByName: Record<string, number> = {}
): ResolvedMetalRate {
  const { metalType, purityLabel } = detectProductMetal(product);

  // 1. Try Direct Purity ID match if available in ratesList
  const purityId = product.purity || (product as any).purity_id;
  if (purityId && ratesList.length > 0) {
    const matchedRateObj = ratesList.find(
      (r) => (r.purity_id === purityId || r.purity === purityId) && r.rate_per_gram
    );
    if (matchedRateObj) {
      const parsed = parseFloat(String(matchedRateObj.rate_per_gram));
      if (!isNaN(parsed) && parsed > 0) {
        // Confirm that the purity name of the matched rate matches the detected metal
        const rName = clean(matchedRateObj.purity_name);
        const rateIsSilver = /silver|925|chandi/i.test(rName);
        const rateIsPlat = /platinum|950/i.test(rName);

        if (
          (metalType === 'silver' && rateIsSilver) ||
          (metalType === 'platinum' && rateIsPlat) ||
          (metalType === 'gold' && !rateIsSilver && !rateIsPlat)
        ) {
          return {
            rate: parsed,
            metalType,
            purityLabel: matchedRateObj.purity_name || purityLabel,
          };
        }
      }
    }
  }

  // 2. Try Exact Name match in rateMapByName
  if (product.purity_name && rateMapByName[product.purity_name]) {
    const directVal = rateMapByName[product.purity_name];
    if (directVal > 0) {
      const pLower = clean(product.purity_name);
      const isSilv = /silver|925|chandi/i.test(pLower);
      const isPlat = /platinum|950/i.test(pLower);
      if (
        (metalType === 'silver' && isSilv) ||
        (metalType === 'platinum' && isPlat) ||
        (metalType === 'gold' && !isSilv && !isPlat)
      ) {
        return { rate: directVal, metalType, purityLabel: product.purity_name };
      }
    }
  }

  // 3. Fallback matching per metal type
  if (metalType === 'silver') {
    // Search ratesList for any silver rate
    const silverObj = ratesList.find((r) => /silver|925|chandi/i.test(r.purity_name));
    if (silverObj) {
      const val = parseFloat(String(silverObj.rate_per_gram));
      if (!isNaN(val) && val > 0) {
        return { rate: val, metalType: 'silver', purityLabel: silverObj.purity_name || purityLabel };
      }
    }
    // Check rateMap keys for silver
    for (const [key, val] of Object.entries(rateMapByName)) {
      if (/silver|925|chandi/i.test(key) && val > 0) {
        return { rate: val, metalType: 'silver', purityLabel: key };
      }
    }
    // Standard bullion benchmark for silver (e.g. ₹92/g) - never gold rate
    return { rate: 92, metalType: 'silver', purityLabel: purityLabel || 'Silver (925)' };
  }

  if (metalType === 'platinum') {
    const platObj = ratesList.find((r) => /platinum|950|\bpt\b/i.test(r.purity_name));
    if (platObj) {
      const val = parseFloat(String(platObj.rate_per_gram));
      if (!isNaN(val) && val > 0) {
        return { rate: val, metalType: 'platinum', purityLabel: platObj.purity_name || purityLabel };
      }
    }
    for (const [key, val] of Object.entries(rateMapByName)) {
      if (/platinum|950/i.test(key) && val > 0) {
        return { rate: val, metalType: 'platinum', purityLabel: key };
      }
    }
    return { rate: 3200, metalType: 'platinum', purityLabel: purityLabel || 'Platinum 950' };
  }

  // 4. Gold rate resolution by Karat
  const pName = clean(product.purity_name);
  if (/24kt|999/i.test(pName)) {
    const obj = ratesList.find((r) => /24kt|999/i.test(r.purity_name));
    const val = obj ? parseFloat(String(obj.rate_per_gram)) : (rateMapByName['24KT (999)'] || 7450);
    return { rate: val || 7450, metalType: 'gold', purityLabel: product.purity_name || '24KT (999)' };
  }
  if (/18kt|750/i.test(pName)) {
    const obj = ratesList.find((r) => /18kt|750/i.test(r.purity_name));
    const val = obj ? parseFloat(String(obj.rate_per_gram)) : (rateMapByName['18KT (750)'] || 5590);
    return { rate: val || 5590, metalType: 'gold', purityLabel: product.purity_name || '18KT (750)' };
  }
  if (/14kt|585/i.test(pName)) {
    const obj = ratesList.find((r) => /14kt|585/i.test(r.purity_name));
    const val = obj ? parseFloat(String(obj.rate_per_gram)) : (rateMapByName['14KT (585)'] || 4350);
    return { rate: val || 4350, metalType: 'gold', purityLabel: product.purity_name || '14KT (585)' };
  }

  // Default: 22KT Hallmarked Gold
  const obj22 = ratesList.find((r) => /22kt|916/i.test(r.purity_name));
  const val22 = obj22 ? parseFloat(String(obj22.rate_per_gram)) : (rateMapByName['22KT (916)'] || 6830);
  return { rate: val22 || 6830, metalType: 'gold', purityLabel: product.purity_name || '22KT (916)' };
}
