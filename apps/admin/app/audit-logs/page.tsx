"use client";

import { useEffect, useState } from "react";

import { AdminLayout } from "@/components/admin-layout";
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
import type { AdminAuditLog } from "@dunnaa/shared";

const LIMIT = 30;

export default function AuditLogsPage() {
  const [items, setItems] = useState<AdminAuditLog[]>([]);
  const [total, setTotal] = useState(0);
  const [skip, setSkip] = useState(0);
  const [error, setError] = useState("");

  useEffect(() => {
    api.admin
      .auditLogs({ skip, limit: LIMIT })
      .then((res) => {
        setItems(res.items);
        setTotal(res.total);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "Erro ao carregar"));
  }, [skip]);

  return (
    <AdminLayout>
      <PageHeader title="Audit Logs" description="Registro de ações sensíveis" />

      {error && (
        <div className="mb-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>
      )}

      <Table>
        <thead>
          <tr>
            <Th>Ação</Th>
            <Th>Recurso</Th>
            <Th>Usuário</Th>
            <Th>IP</Th>
            <Th>Data</Th>
          </tr>
        </thead>
        <tbody>
          {items.length === 0 ? (
            <EmptyRow colSpan={5} message="Nenhum log encontrado" />
          ) : (
            items.map((log) => (
              <Tr key={log.id}>
                <Td className="font-medium">{log.action}</Td>
                <Td>
                  {log.resource_type}
                  {log.resource_id && (
                    <span className="ml-1 font-mono text-xs text-neutral-400">
                      {log.resource_id.slice(0, 8)}…
                    </span>
                  )}
                </Td>
                <Td className="font-mono text-xs">
                  {log.user_id ? `${log.user_id.slice(0, 8)}…` : "—"}
                </Td>
                <Td>{log.ip_address ?? "—"}</Td>
                <Td>{formatDate(log.created_at)}</Td>
              </Tr>
            ))
          )}
        </tbody>
      </Table>

      <Pagination total={total} skip={skip} limit={LIMIT} onPage={setSkip} />
    </AdminLayout>
  );
}
