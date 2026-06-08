"use client";

import { useEffect, useState } from "react";

import { AdminLayout } from "@/components/admin-layout";
import {
  EmptyRow,
  PageHeader,
  Table,
  Td,
  Th,
  Tr,
} from "@/components/ui/table";
import { ApiError, api } from "@/lib/api";
import type { SystemSetting } from "@dunnaa/shared";

export default function SettingsPage() {
  const [items, setItems] = useState<SystemSetting[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api.admin
      .settings()
      .then((res) => setItems(res.items))
      .catch((err) => setError(err instanceof ApiError ? err.message : "Erro ao carregar"));
  }, []);

  return (
    <AdminLayout>
      <PageHeader
        title="Configurações"
        description="Parâmetros do sistema (somente leitura)"
      />

      {error && (
        <div className="mb-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>
      )}

      <Table>
        <thead>
          <tr>
            <Th>Chave</Th>
            <Th>Valor</Th>
            <Th>Categoria</Th>
            <Th>Descrição</Th>
          </tr>
        </thead>
        <tbody>
          {items.length === 0 ? (
            <EmptyRow colSpan={4} message="Nenhuma configuração encontrada" />
          ) : (
            items.map((s) => (
              <Tr key={s.key}>
                <Td className="font-mono text-sm">{s.key}</Td>
                <Td>{s.is_secret ? "••••••••" : (s.value ?? "—")}</Td>
                <Td>{s.category}</Td>
                <Td className="text-neutral-500">{s.description ?? "—"}</Td>
              </Tr>
            ))
          )}
        </tbody>
      </Table>
    </AdminLayout>
  );
}
