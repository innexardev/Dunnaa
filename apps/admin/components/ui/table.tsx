import { cn } from "@/lib/utils";

export function Table({ children }: { children: React.ReactNode }) {
  return (
    <div className="overflow-x-auto rounded-lg border border-neutral-200">
      <table className="min-w-full divide-y divide-neutral-200 text-sm">{children}</table>
    </div>
  );
}

export function Th({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <th
      className={cn(
        "bg-neutral-50 px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-neutral-500",
        className,
      )}
    >
      {children}
    </th>
  );
}

export function Td({ children, className }: { children: React.ReactNode; className?: string }) {
  return <td className={cn("px-4 py-3 text-neutral-700", className)}>{children}</td>;
}

export function Tr({ children }: { children: React.ReactNode }) {
  return <tr className="border-t border-neutral-100 hover:bg-neutral-50">{children}</tr>;
}

export function EmptyRow({ colSpan, message }: { colSpan: number; message: string }) {
  return (
    <tr>
      <td colSpan={colSpan} className="px-4 py-8 text-center text-neutral-500">
        {message}
      </td>
    </tr>
  );
}

export function PageHeader({
  title,
  description,
  action,
}: {
  title: string;
  description?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="mb-6 flex items-start justify-between">
      <div>
        <h1 className="text-2xl font-semibold text-neutral-900">{title}</h1>
        {description && <p className="mt-1 text-sm text-neutral-500">{description}</p>}
      </div>
      {action}
    </div>
  );
}

export function Pagination({
  total,
  skip,
  limit,
  onPage,
}: {
  total: number;
  skip: number;
  limit: number;
  onPage: (skip: number) => void;
}) {
  const page = Math.floor(skip / limit) + 1;
  const totalPages = Math.max(1, Math.ceil(total / limit));

  return (
    <div className="mt-4 flex items-center justify-between text-sm text-neutral-600">
      <span>
        {total} registro{total !== 1 ? "s" : ""}
      </span>
      <div className="flex gap-2">
        <button
          type="button"
          disabled={page <= 1}
          onClick={() => onPage(Math.max(0, skip - limit))}
          className="rounded border px-3 py-1 disabled:opacity-40"
        >
          Anterior
        </button>
        <span className="px-2 py-1">
          {page} / {totalPages}
        </span>
        <button
          type="button"
          disabled={page >= totalPages}
          onClick={() => onPage(skip + limit)}
          className="rounded border px-3 py-1 disabled:opacity-40"
        >
          Próxima
        </button>
      </div>
    </div>
  );
}
