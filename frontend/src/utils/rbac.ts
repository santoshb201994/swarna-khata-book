export type UserRole = 'superadmin' | 'owner' | 'manager' | 'accountant' | 'staff';

export const ROLE_LEVELS: Record<UserRole, number> = {
  superadmin: 100,
  owner: 80,
  manager: 60,
  accountant: 40,
  staff: 20,
};

export const ROLE_HIERARCHY: Record<UserRole, UserRole[]> = {
  superadmin: ['superadmin', 'owner', 'manager', 'accountant', 'staff'],
  owner: ['owner', 'manager', 'accountant', 'staff'],
  manager: ['manager', 'staff'],
  accountant: ['accountant', 'staff'],
  staff: ['staff'],
};

export type WebappFeature =
  | 'developer_portal'       // Level 100: Superadmin multi-tenant control plane
  | 'export_all_shops_data'  // Level 100: Superadmin global multi-shop archive export
  | 'invoice_studio'         // Level 80: Store Owner legal branding, GSTIN, Bank details
  | 'export_shop_data'       // Level 80: Store Owner & Superadmin full shop data export
  | 'manage_staff'           // Level 60: Owner & Manager staff account administration
  | 'add_edit_products'      // Level 60: Owner & Manager inventory creation & pricing
  | 'sync_gold_rates'        // Level 60: Owner & Manager bullion rate sync & manual overrides
  | 'close_daybook'          // Level 60: Owner & Manager day-close financial sign-off
  | 'view_accounting'        // Level 40: Accountant, Manager, Owner accounting & daybook tab
  | 'record_cash_vouchers'   // Level 40: Accountant, Manager, Owner daily cash in/out entries
  | 'view_inventory_catalog' // Level 20: All store roles
  | 'pos_billing'            // Level 20: All store roles
  | 'customer_directory'     // Level 20: All store roles
  | 'mobile_scanner';        // Level 20: All store roles

export const FEATURE_MIN_LEVELS: Record<WebappFeature, number> = {
  developer_portal: 100,
  export_all_shops_data: 100,
  invoice_studio: 80,
  export_shop_data: 80,
  manage_staff: 60,
  add_edit_products: 60,
  sync_gold_rates: 60,
  close_daybook: 60,
  view_accounting: 40,
  record_cash_vouchers: 40,
  view_inventory_catalog: 20,
  pos_billing: 20,
  customer_directory: 20,
  mobile_scanner: 20,
};

export function getRoleRank(role: string | undefined): number {
  if (!role) return 0;
  return ROLE_LEVELS[role as UserRole] || 0;
}

export function canAccessFeature(role: string | undefined, feature: WebappFeature): boolean {
  const userRank = getRoleRank(role);
  const minRequired = FEATURE_MIN_LEVELS[feature] || 0;
  return userRank >= minRequired;
}
