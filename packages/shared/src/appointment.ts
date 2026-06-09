export type AppointmentStatus =
  | "pending"
  | "confirmed"
  | "awaiting_deposit"
  | "completed"
  | "cancelled"
  | "no_show";

export interface Appointment {
  id: string;
  establishment_id: string;
  service_id: string;
  staff_id: string;
  scheduled_at: string;
  duration_minutes: number;
  status: AppointmentStatus;
  total_price: number | null;
  payment_type: string;
}

export interface AvailabilitySlot {
  start_at: string;
  end_at: string;
}

export interface AvailabilityResponse {
  establishment_id: string;
  staff_id: string;
  service_id: string;
  date: string;
  slots: AvailabilitySlot[];
}
