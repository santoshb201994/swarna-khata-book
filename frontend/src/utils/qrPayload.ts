import QRCode from 'qrcode';

export const QR_PREFIX = 'SKB:';

// UUID v4 regular expression (standard 8-4-4-4-12 hex string)
export const UUID_V4_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

export interface ParsedQRPayload {
  isCanonical: boolean;
  qrToken: string | null;
  sku: string | null;
  isTray: boolean;
  trayCode: string | null;
  raw: string;
}

/**
 * Returns the canonical QR payload for a given jewellery item UUID token.
 * Canonical format: SKB:<UUID>
 */
export function getQRPayload(qrToken: string): string {
  const clean = (qrToken || '').trim();
  if (clean.toUpperCase().startsWith(QR_PREFIX)) {
    return clean;
  }
  return `${QR_PREFIX}${clean}`;
}

/**
 * Parses any scanned QR code payload, handling canonical SKB:<UUID> format,
 * raw UUIDs, legacy JSON tags, tray tags, and plain text SKUs.
 */
export function parseQRPayload(scannedText: string): ParsedQRPayload {
  const raw = (scannedText || '').trim();
  if (!raw) {
    return {
      isCanonical: false,
      qrToken: null,
      sku: null,
      isTray: false,
      trayCode: null,
      raw: '',
    };
  }

  // 1. Check Canonical Prefix "SKB:<UUID>"
  if (raw.toUpperCase().startsWith(QR_PREFIX)) {
    const candidateUuid = raw.substring(QR_PREFIX.length).trim();
    if (UUID_V4_REGEX.test(candidateUuid)) {
      return {
        isCanonical: true,
        qrToken: candidateUuid.toLowerCase(),
        sku: null,
        isTray: false,
        trayCode: null,
        raw,
      };
    }
    // Prefix present but not valid UUID (fallback token)
    return {
      isCanonical: false,
      qrToken: candidateUuid,
      sku: candidateUuid,
      isTray: false,
      trayCode: null,
      raw,
    };
  }

  // 2. Check if raw string is directly a valid UUID
  if (UUID_V4_REGEX.test(raw)) {
    return {
      isCanonical: true,
      qrToken: raw.toLowerCase(),
      sku: null,
      isTray: false,
      trayCode: null,
      raw,
    };
  }

  // 3. Check if payload is a Tray / Group code
  if (raw.toUpperCase().startsWith('TRAY-')) {
    return {
      isCanonical: false,
      qrToken: null,
      sku: null,
      isTray: true,
      trayCode: raw,
      raw,
    };
  }

  // 4. Check if payload is legacy JSON
  if (raw.startsWith('{') && raw.endsWith('}')) {
    try {
      const parsed = JSON.parse(raw);
      if (parsed && typeof parsed === 'object') {
        if (parsed.type === 'tray' || parsed.is_tray || parsed.tray_id || (parsed.code && String(parsed.code).toUpperCase().startsWith('TRAY-'))) {
          return {
            isCanonical: false,
            qrToken: null,
            sku: null,
            isTray: true,
            trayCode: parsed.code || parsed.tray_code || String(parsed.tray_id || ''),
            raw,
          };
        }
        if (parsed.qr_token && UUID_V4_REGEX.test(parsed.qr_token)) {
          return {
            isCanonical: true,
            qrToken: String(parsed.qr_token).toLowerCase(),
            sku: parsed.sku ? String(parsed.sku) : null,
            isTray: false,
            trayCode: null,
            raw,
          };
        }
        return {
          isCanonical: false,
          qrToken: null,
          sku: parsed.sku ? String(parsed.sku) : null,
          isTray: false,
          trayCode: null,
          raw,
        };
      }
    } catch {
      // Not valid JSON, continue to plain SKU
    }
  }

  // 5. Default fallback: legacy plain SKU or custom tag string
  return {
    isCanonical: false,
    qrToken: null,
    sku: raw,
    isTray: false,
    trayCode: null,
    raw,
  };
}

/**
 * Centralized QR image generator producing high-contrast Data URLs.
 * Encodes the canonical payload `SKB:<UUID>` dynamically in React.
 */
export async function generateQRDataUrl(
  qrTokenOrSku: string,
  options?: QRCode.QRCodeToDataURLOptions
): Promise<string> {
  const token = (qrTokenOrSku || '').trim();
  const payload = UUID_V4_REGEX.test(token)
    ? getQRPayload(token)
    : (token || 'SKB:UNKNOWN');

  const defaultOptions: QRCode.QRCodeToDataURLOptions = {
    errorCorrectionLevel: 'M',
    type: 'image/png',
    margin: 1,
    width: 256,
    color: {
      dark: '#0f172a',
      light: '#ffffff',
    },
    ...options,
  };

  return await QRCode.toDataURL(payload, defaultOptions);
}

/**
 * Centralized QR SVG generator for vector-sharp printing.
 */
export async function generateQRSvg(
  qrTokenOrSku: string,
  options?: QRCode.QRCodeToStringOptions
): Promise<string> {
  const token = (qrTokenOrSku || '').trim();
  const payload = UUID_V4_REGEX.test(token)
    ? getQRPayload(token)
    : (token || 'SKB:UNKNOWN');

  const defaultOptions: QRCode.QRCodeToStringOptions = {
    type: 'svg',
    errorCorrectionLevel: 'M',
    margin: 1,
    color: {
      dark: '#0f172a',
      light: '#ffffff',
    },
    ...options,
  };

  return await QRCode.toString(payload, defaultOptions);
}

/**
 * Validates a scanned physical tag payload against an item's expected identity.
 */
export function validateQRPayload(
  scannedText: string,
  expectedQrToken?: string | null,
  expectedSku?: string | null
): { match: boolean; message: string; isCanonical: boolean; scannedToken: string | null } {
  const parsed = parseQRPayload(scannedText);

  // Match against QR token (UUID)
  if (expectedQrToken && parsed.qrToken) {
    const cleanExpected = expectedQrToken.trim().toLowerCase();
    const cleanScanned = parsed.qrToken.trim().toLowerCase();
    if (cleanExpected === cleanScanned) {
      return {
        match: true,
        message: 'Valid Physical Tag! Canonical UUID verified and matches inventory record.',
        isCanonical: parsed.isCanonical,
        scannedToken: parsed.qrToken,
      };
    }
  }

  // Fallback match against SKU for legacy tags
  if (expectedSku && parsed.sku) {
    if (expectedSku.trim().toLowerCase() === parsed.sku.trim().toLowerCase()) {
      return {
        match: true,
        message: 'Valid Legacy Tag! SKU matches inventory record.',
        isCanonical: false,
        scannedToken: parsed.sku,
      };
    }
  }

  return {
    match: false,
    message: `Tag mismatch! Scanned [${parsed.qrToken || parsed.sku || parsed.raw}] does not match expected identity.`,
    isCanonical: parsed.isCanonical,
    scannedToken: parsed.qrToken || parsed.sku,
  };
}
