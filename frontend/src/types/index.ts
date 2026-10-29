export interface User {
  id: number;
  username: string;
  email: string;
  role: 'superadmin' | 'owner' | 'manager' | 'staff' | 'accountant';
  branch_id?: number;
}

export interface Branch {
  id: number;
  name: string;
  address: string;
  phone: string;
  gstin: string;
}

export interface Purity {
  id: number;
  name: string;
  fineness: string;
}

export interface Category {
  id: number;
  name: string;
  description: string;
}

export interface Product {
  id: number;
  name: string;
  sku: string;
  category: number;
  category_name?: string;
  purity: number;
  purity_name?: string;
  gross_weight: string;
  stone_weight: string;
  other_weight: string;
  net_weight: string;
  making_charge_type: 'per_gram' | 'percent' | 'fixed';
  making_charge_value: string;
  description: string;
  hsn_code: string;
  huid: string;
  photo_url?: string;
  qr_code_url?: string;
  item_status?: 'AVAILABLE' | 'IN_CART' | 'SOLD';
  is_active: boolean;
  created_at: string;
}

export interface GoldRate {
  id: number;
  purity: number;
  purity_id?: number;
  purity_name: string;
  rate_per_gram: string;
  effective_date: string;
  is_current: boolean;
}

export interface Customer {
  id: number;
  name: string;
  phone: string;
  email: string;
  address: string;
  pan_number: string;
  aadhar_last4?: string;
  created_at?: string;
}

export interface SaleItem {
  id: number;
  product?: number;
  product_id?: number;
  product_name: string;
  sku: string;
  purity: string;
  gross_weight: string | number;
  net_weight: string | number;
  gold_rate_per_gram: string | number;
  making_charge: string | number;
  stone_charge: string | number;
  unit_price: string | number;
  total_price: string | number;
  quantity: number;
  hsn_code?: string;
  gst_rate?: string | number;
  huid?: string;
  wastage_percent?: string | number;
}

export interface InvoiceSetting {
  id: number;
  branch_id: number;
  header_invocation: string;
  shop_name_primary: string;
  shop_name_secondary: string;
  tagline: string;
  address_primary: string;
  address_secondary: string;
  phone_landline: string;
  phone_mobile_1: string;
  phone_mobile_2: string;
  email: string;
  website: string;
  gstin: string;
  pan_number: string;
  state_name: string;
  state_code: string;
  bis_hallmark_licence: string;
  logo_url: string;
  template_style: 'traditional_bilingual' | 'modern_luxury' | 'royal_gold' | 'compact_thermal';
  default_paper_size: 'A4' | 'A5' | '80mm';
  show_invocation: boolean;
  show_bilingual_header: boolean;
  show_huid: boolean;
  show_purity: boolean;
  show_gross_net_weight: boolean;
  show_wastage: boolean;
  show_making_charge: boolean;
  show_stone_details: boolean;
  show_rate_per_gram: boolean;
  show_old_gold_section: boolean;
  show_upi_qr: boolean;
  show_bank_details: boolean;
  show_customer_address: boolean;
  show_hallmark_badge: boolean;
  bank_name: string;
  account_name: string;
  account_number: string;
  ifsc_code: string;
  upi_id: string;
  terms_and_conditions: string;
  declaration: string;
  signatory_title: string;
}

export interface Sale {
  id: number;
  invoice_number: string;
  customer?: number;
  customer_id?: number;
  customer_name?: string;
  customer_phone?: string;
  customer_address?: string;
  customer_pan?: string;
  branch_id?: number;
  sale_date: string;
  gold_rate_per_gram: string | number;
  subtotal: string | number;
  discount: string | number;
  cgst_amount: string | number;
  sgst_amount: string | number;
  igst_amount?: string | number;
  total_amount: string | number;
  amount_paid: string | number;
  old_gold_value: string | number;
  balance_due: string | number;
  payment_status: 'pending' | 'partial' | 'paid';
  sale_status: 'active' | 'cancelled';
  notes?: string;
  items?: SaleItem[];
  payments?: Array<{
    id: number;
    method: string;
    amount: string | number;
    reference?: string;
    paid_at: string;
    note?: string;
  }>;
  invoice_setting?: InvoiceSetting;
}

export interface DayBook {
  id: number;
  date: string;
  opening_balance: string;
  cash_in: string;
  cash_out: string;
  closing_balance: string;
  net_cash: string;
  is_closed: boolean;
}
