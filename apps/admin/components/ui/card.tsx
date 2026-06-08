import { cn } from "@/lib/utils";

export function Card({
  className,
  children,
}: {
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <div className={cn("rounded-lg border border-neutral-200 bg-white p-5 shadow-sm", className)}>
      {children}
    </div>
  );
}

export function CardTitle({ children }: { children: React.ReactNode }) {
  return <h3 className="text-sm font-medium text-neutral-500">{children}</h3>;
}

export function CardValue({ children }: { children: React.ReactNode }) {
  return <p className="mt-1 text-2xl font-semibold text-neutral-900">{children}</p>;
}
