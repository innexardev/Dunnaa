"use client";

import { useEffect, useState } from "react";

import { AdminLayout } from "@/components/admin-layout";
import { Card, CardTitle, CardValue } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/table";
import { ApiError, api } from "@/lib/api";
import { formatCurrency, formatDate } from "@/lib/utils";
import type { AdminDashboard } from "@dunnaa/shared";

export default function DashboardPage() {
  const [data, setData] = useState<AdminDashboard | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.admin
      .dashboard()
      .then(setData)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Erro ao carregar"));
  }, []);

  return (
    <AdminLayout>
      <PageHeader title="Dashboard" description="Visão geral da plataforma" />

      {error && (
        <div className="mb-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>
      )}

      {data && (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardTitle>Estabelecimentos</CardTitle>
              <CardValue>{data.active_establishments}</CardValue>
              <p className="mt-1 text-xs text-neutral-500">de {data.total_establishments} total</p>
            </Card>
            <Card>
              <CardTitle>Usuários</CardTitle>
              <CardValue>{data.total_users}</CardValue>
              <p className="mt-1 text-xs text-neutral-500">+{data.new_users_30d} nos últimos 30d</p>
            </Card>
            <Card>
              <CardTitle>Assinaturas ativas</CardTitle>
              <CardValue>{data.active_subscriptions}</CardValue>
            </Card>
            <Card>
              <CardTitle>Receita (30d)</CardTitle>
              <CardValue>{formatCurrency(data.platform_revenue_30d)}</CardValue>
              <p className="mt-1 text-xs text-neutral-500">
                {data.revenue_growth_percent_30d >= 0 ? "+" : ""}
                {data.revenue_growth_percent_30d.toFixed(1)}% vs período anterior
              </p>
            </Card>
          </div>

          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            <Card>
              <CardTitle>Receita total</CardTitle>
              <CardValue>{formatCurrency(data.platform_revenue_total)}</CardValue>
            </Card>
            <Card>
              <CardTitle>Novos estabelecimentos (30d)</CardTitle>
              <CardValue>{data.new_establishments_30d}</CardValue>
              <p className="mt-1 text-xs text-neutral-500">
                Atualizado em {formatDate(data.generated_at)}
              </p>
            </Card>
          </div>
        </>
      )}

      {!data && !error && <p className="text-neutral-500">Carregando...</p>}
    </AdminLayout>
  );
}
