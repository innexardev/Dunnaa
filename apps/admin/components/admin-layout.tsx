"use client";

import { useRouter } from "next/navigation";

import { api } from "@/lib/api";

import { Sidebar } from "./sidebar";

export function AdminLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();

  function handleLogout() {
    api.auth.logout();
    router.push("/login");
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <header className="flex h-14 items-center justify-end border-b border-neutral-200 bg-white px-6">
          <button
            type="button"
            onClick={handleLogout}
            className="text-sm text-neutral-600 hover:text-neutral-900"
          >
            Sair
          </button>
        </header>
        <main className="flex-1 overflow-auto p-6">{children}</main>
      </div>
    </div>
  );
}
