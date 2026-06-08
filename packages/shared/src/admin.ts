export type EstablishmentStatus = "pending" | "active" | "suspended" | "closed";
export type UserRole = "customer" | "owner" | "staff" | "admin";
export type SubscriptionStatus = "active" | "cancelled" | "expired" | "paused";
export type PaymentStatus =
  | "pending"
  | "processing"
  | "succeeded"
  | "failed"
  | "refunded";

export interface Paginated<T> {
  items: T[];
  total: number;
}

export interface AdminDashboard {
  total_establishments: number;
  active_establishments: number;
  total_users: number;
  active_subscriptions: number;
  platform_revenue_total: number;
  platform_revenue_30d: number;
  revenue_growth_percent_30d: number;
  new_users_30d: number;
  new_establishments_30d: number;
  generated_at: string;
}

export interface AdminEstablishment {
  id: string;
  owner_id: string;
  name: string;
  slug: string;
  city: string;
  state: string;
  status: EstablishmentStatus;
  phone: string;
  created_at: string;
}

export interface AdminUser {
  id: string;
  phone: string;
  name: string | null;
  email: string | null;
  role: UserRole;
  created_at: string;
}

export interface AdminSubscription {
  id: string;
  user_id: string;
  plan_id: string;
  establishment_id: string;
  status: SubscriptionStatus;
  current_period_start: string | null;
  current_period_end: string | null;
  created_at: string;
}

export interface AdminPayment {
  id: string;
  user_id: string;
  establishment_id: string;
  amount: number;
  platform_fee: number;
  status: PaymentStatus;
  purpose: string;
  created_at: string;
}

export interface AdminAuditLog {
  id: string;
  user_id: string | null;
  action: string;
  resource_type: string;
  resource_id: string | null;
  establishment_id: string | null;
  ip_address: string | null;
  request_id: string | null;
  created_at: string;
}

export interface SystemSetting {
  key: string;
  value: string | null;
  description: string | null;
  is_secret: boolean;
  category: string;
}
