export type QueueStatus = "waiting" | "called" | "serving" | "completed" | "cancelled";

export interface QueueEntry {
  id: string;
  establishment_id: string;
  position: number;
  status: QueueStatus;
  entered_at: string;
  estimated_wait_minutes: number | null;
}
