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
import { formatCurrency, formatDate } from "@/lib/utils";
import type { AdminPayment } from "@dunnaa/shared";

const LIMIT = 20;

export default function PaymentsPage() {
  const [items, setItems] = useState<AdminPayment[]>([]);
  const [total, setTotal] = useState(0);
  const [skip, setSkip] = useState(0);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    api.admin
      .payments({ skip, limit: LIMIT, status: status || undefined })
      .then((res) => {
        setItems(res.items);
        setTotal(res.total);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "Erro ao carregar"));
  }, [skip, status]);

  return (
    <AdminLayout>
      <PageHeader
        title="Pagamentos"
        description="Transações da plataforma"
        action={
          <Select value={status} onChange={(e) => { setStatus(e.target.value); setSkip(0); }}>
            <option value="">Todos os status</option>
            <option value="pending">Pending</option>
            <option value="processing">Processing</option>
            <option value="succeeded">Succeeded</option>
            <option value="failed">Failed</option>
            <option value="refunded">Refunded</option>
          </Select>
        }
      />

      {error && (
        <div className="mb-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>
      )}

      <Table>
        <thead>
          <tr>
            <Th>Valor</Th>
            <Th>Taxa plataforma</Th>
            <Th>Finalidade</Th>
            <Th>Status</Th>
            <Th>Criado em</Th>
          </tr>
        </thead>
        <tbody>
          {items.length === 0 ? (
            <EmptyRow colSpan={5} message="Nenhum pagamento encontrado" />
          ) : (
            items.map((p) => (
              <Tr key={p.id}>
                <Td className="font-medium">{formatCurrency(p.amount)}</Td>
                <Td>{formatCurrency(p.platform_fee)}</Td>
                <Td>{p.purpose}</Td>
                <Td>
                  <Badge status={p.status} />
                </Td>
                <Td>{formatDate(p.created_at)}</Td>
              </Tr>
            ))
          )}
        </tbody>
      </Table>

      <Pagination total={total} skip={skip} limit={LIMIT} onPage={setSkip} />
    </AdminLayout>
  );
}
