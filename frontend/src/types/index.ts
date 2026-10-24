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
}

export interface SaleItem {
  id: number;
  product: number;
  product_name: string;
  sku: string;
  purity: string;
  gross_weight: string;
  net_weight: string;
  gold_rate_per_gram: string;
  making_charge: string;
  stone_charge: string;
  unit_price: string;
  total_price: string;
  quantity: number;
}

export interface Sale {
  id: number;
  invoice_number: string;
  customer?: number;
  customer_name?: string;
  sale_date: string;
  gold_rate_per_gram: string;
  subtotal: string;
  discount: string;
  cgst_amount: string;
  sgst_amount: string;
  total_amount: string;
  amount_paid: string;
  old_gold_value: string;
  balance_due: string;
  payment_status: 'pending' | 'partial' | 'paid';
  sale_status: 'active' | 'cancelled';
  items?: SaleItem[];
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
