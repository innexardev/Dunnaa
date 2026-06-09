export interface Establishment {
  id: string;
  name: string;
  slug: string;
  category: string;
  description: string | null;
  address: string;
  city: string;
  state: string;
  phone: string;
  logo_url: string | null;
  cover_url: string | null;
  distance: number | null;
  queue_mode_enabled: boolean;
  status: string;
}

export interface EstablishmentList {
  items: Establishment[];
  total: number;
  page: number;
  page_size: number;
}

export interface Service {
  id: string;
  establishment_id: string;
  name: string;
  description: string | null;
  price: number;
  duration_minutes: number;
  active: boolean;
}

export interface StaffMember {
  id: string;
  establishment_id: string;
  name: string;
  role: string;
  active: boolean;
}
