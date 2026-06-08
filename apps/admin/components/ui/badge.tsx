import { cn } from "@/lib/utils";

const COLORS: Record<string, string> = {
  active: "bg-green-100 text-green-800",
  pending: "bg-yellow-100 text-yellow-800",
  suspended: "bg-orange-100 text-orange-800",
  closed: "bg-neutral-100 text-neutral-600",
  cancelled: "bg-neutral-100 text-neutral-600",
  expired: "bg-red-100 text-red-800",
  paused: "bg-blue-100 text-blue-800",
  succeeded: "bg-green-100 text-green-800",
  failed: "bg-red-100 text-red-800",
  processing: "bg-blue-100 text-blue-800",
  refunded: "bg-purple-100 text-purple-800",
  customer: "bg-neutral-100 text-neutral-700",
  owner: "bg-brand-100 text-brand-800",
  staff: "bg-blue-100 text-blue-800",
  admin: "bg-purple-100 text-purple-800",
};

export function Badge({ status }: { status: string }) {
  return (
    <span
      className={cn(
        "inline-flex rounded-full px-2 py-0.5 text-xs font-medium capitalize",
        COLORS[status] ?? "bg-neutral-100 text-neutral-700",
      )}
    >
      {status}
    </span>
  );
}
