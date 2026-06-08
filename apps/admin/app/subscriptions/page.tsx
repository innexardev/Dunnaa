"use client";

import { useEffect, useState } from "react";

import { AdminLayout } from "@/components/admin-layout";
import { Badge } from "@/components/ui/badge";
import { Select } from "@/components/ui/input";
import {
  EmptyRow,
  PageHeader,
  Pagination,
  Table,
  Td,
  Th,
  Tr,
} from "@/components/ui/table";
import { ApiError, api } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import type { AdminSubscription } from "@dunnaa/shared";

const LIMIT = 20;

export default function SubscriptionsPage() {
  const [items, setItems] = useState<AdminSubscription[]>([]);
  const [total, setTotal] = useState(0);
  const [skip, setSkip] = useState(0);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    api.admin
      .subscriptions({ skip, limit: LIMIT, status: status || undefined })
      .then((res) => {
        setItems(res.items);
        setTotal(res.total);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "Erro ao carregar"));
  }, [skip, status]);

  return (
    <AdminLayout>
      <PageHeader
        title="Assinaturas"
        description="Planos ativos e histórico"
        action={
          <Select value={status} onChange={(e) => { setStatus(e.target.value); setSkip(0); }}>
            <option value="">Todos os status</option>
            <option value="active">Active</option>
            <option value="cancelled">Cancelled</option>
            <option value="expired">Expired</option>
            <option value="paused">Paused</option>
          </Select>
        }
      />

      {error && (
        <div className="mb-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>
      )}

      <Table>
        <thead>
          <tr>
            <Th>ID</Th>
            <Th>Usuário</Th>
            <Th>Plano</Th>
            <Th>Status</Th>
            <Th>Período</Th>
            <Th>Criado em</Th>
          </tr>
        </thead>
        <tbody>
          {items.length === 0 ? (
            <EmptyRow colSpan={6} message="Nenhuma assinatura encontrada" />
          ) : (
            items.map((s) => (
              <Tr key={s.id}>
                <Td className="font-mono text-xs">{s.id.slice(0, 8)}…</Td>
                <Td className="font-mono text-xs">{s.user_id.slice(0, 8)}…</Td>
                <Td className="font-mono text-xs">{s.plan_id.slice(0, 8)}…</Td>
                <Td>
                  <Badge status={s.status} />
                </Td>
                <Td>
                  {s.current_period_start && s.current_period_end
                    ? `${formatDate(s.current_period_start)} – ${formatDate(s.current_period_end)}`
                    : "—"}
                </Td>
                <Td>{formatDate(s.created_at)}</Td>
              </Tr>
            ))
          )}
        </tbody>
      </Table>

      <Pagination total={total} skip={skip} limit={LIMIT} onPage={setSkip} />
    </AdminLayout>
  );
}
