"use client";

import Link from "next/link";
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
import type { AdminEstablishment } from "@dunnaa/shared";

const LIMIT = 20;

export default function EstablishmentsPage() {
  const [items, setItems] = useState<AdminEstablishment[]>([]);
  const [total, setTotal] = useState(0);
  const [skip, setSkip] = useState(0);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    api.admin
      .establishments({ skip, limit: LIMIT, status: status || undefined })
      .then((res) => {
        setItems(res.items);
        setTotal(res.total);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "Erro ao carregar"));
  }, [skip, status]);

  return (
    <AdminLayout>
      <PageHeader
        title="Estabelecimentos"
        description="Gerenciar barbearias e salões"
        action={
          <Select value={status} onChange={(e) => { setStatus(e.target.value); setSkip(0); }}>
            <option value="">Todos os status</option>
            <option value="pending">Pending</option>
            <option value="active">Active</option>
            <option value="suspended">Suspended</option>
            <option value="closed">Closed</option>
          </Select>
        }
      />

      {error && (
        <div className="mb-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>
      )}

      <Table>
        <thead>
          <tr>
            <Th>Nome</Th>
            <Th>Cidade</Th>
            <Th>Status</Th>
            <Th>Criado em</Th>
          </tr>
        </thead>
        <tbody>
          {items.length === 0 ? (
            <EmptyRow colSpan={4} message="Nenhum estabelecimento encontrado" />
          ) : (
            items.map((e) => (
              <Tr key={e.id}>
                <Td>
                  <Link
                    href={`/establishments/${e.id}`}
                    className="font-medium text-brand-600 hover:underline"
                  >
                    {e.name}
                  </Link>
                </Td>
                <Td>
                  {e.city}, {e.state}
                </Td>
                <Td>
                  <Badge status={e.status} />
                </Td>
                <Td>{formatDate(e.created_at)}</Td>
              </Tr>
            ))
          )}
        </tbody>
      </Table>

      <Pagination total={total} skip={skip} limit={LIMIT} onPage={setSkip} />
    </AdminLayout>
  );
}
