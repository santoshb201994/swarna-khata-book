import api from '../api/client';
import toast from 'react-hot-toast';

/**
 * Downloads high-precision Tax Invoice PDF using authenticated API call.
 * Uses Blob object URL to ensure Authorization and Tenant headers are transmitted.
 */
export const downloadInvoicePdf = async (saleId: number, invoiceNumber?: string): Promise<boolean> => {
  const loadingToast = toast.loading(`Preparing PDF for Invoice #${invoiceNumber || saleId}...`);
  try {
    const response = await api.get(`/sales/${saleId}/invoice-pdf/`, {
      responseType: 'blob',
    });

    const blob = new Blob([response.data], { type: 'application/pdf' });
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.setAttribute('download', `invoice_${invoiceNumber || saleId}.pdf`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);

    toast.dismiss(loadingToast);
    toast.success(`Invoice #${invoiceNumber || saleId} PDF downloaded!`);
    return true;
  } catch (error: any) {
    console.warn('[PDF Download] Blob download failed, attempting query token fallback...', error);
    toast.dismiss(loadingToast);

    // Fallback: Query parameter token navigation
    const token = localStorage.getItem('access_token');
    if (token) {
      const fallbackUrl = `/api/sales/${saleId}/invoice-pdf/?token=${encodeURIComponent(token)}`;
      window.open(fallbackUrl, '_blank');
      return true;
    }

    toast.error('Unable to download invoice PDF. Please ensure you are logged in.');
    return false;
  }
};
