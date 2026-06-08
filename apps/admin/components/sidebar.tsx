"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";

const NAV = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/establishments", label: "Estabelecimentos" },
  { href: "/users", label: "Usuários" },
  { href: "/subscriptions", label: "Assinaturas" },
  { href: "/payments", label: "Pagamentos" },
  { href: "/audit-logs", label: "Audit Logs" },
  { href: "/settings", label: "Configurações" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex w-60 shrink-0 flex-col border-r border-neutral-200 bg-white">
      <div className="border-b border-neutral-200 px-5 py-4">
        <span className="text-lg font-bold text-brand-700">DUNNAA</span>
        <p className="text-xs text-neutral-500">Painel Admin</p>
      </div>
      <nav className="flex flex-1 flex-col gap-0.5 p-3">
        {NAV.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "rounded-md px-3 py-2 text-sm font-medium transition-colors",
              pathname === item.href || pathname.startsWith(`${item.href}/`)
                ? "bg-brand-50 text-brand-700"
                : "text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900",
            )}
          >
            {item.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
