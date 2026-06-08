"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { AdminLayout } from "@/components/admin-layout";
import { Badge } from "@/components/ui/badge";
import { Input, Select } from "@/components/ui/input";
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
import { formatDate, formatPhone } from "@/lib/utils";
import type { AdminUser } from "@dunnaa/shared";

const LIMIT = 20;

export default function UsersPage() {
  const [items, setItems] = useState<AdminUser[]>([]);
  const [total, setTotal] = useState(0);
  const [skip, setSkip] = useState(0);
  const [search, setSearch] = useState("");
  const [role, setRole] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    api.admin
      .users({ skip, limit: LIMIT, search: search || undefined, role: role || undefined })
      .then((res) => {
        setItems(res.items);
        setTotal(res.total);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "Erro ao carregar"));
  }, [skip, search, role]);

  return (
    <AdminLayout>
      <PageHeader title="Usuários" description="Clientes, donos e equipe" />

      <div className="mb-4 flex gap-3">
        <Input
          placeholder="Buscar por nome ou telefone..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setSkip(0);
          }}
          className="max-w-xs"
        />
        <Select value={role} onChange={(e) => { setRole(e.target.value); setSkip(0); }}>
          <option value="">Todos os roles</option>
          <option value="customer">Customer</option>
          <option value="owner">Owner</option>
          <option value="staff">Staff</option>
          <option value="admin">Admin</option>
        </Select>
      </div>

      {error && (
        <div className="mb-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>
      )}

      <Table>
        <thead>
          <tr>
            <Th>Nome</Th>
            <Th>Telefone</Th>
            <Th>Role</Th>
            <Th>Criado em</Th>
          </tr>
        </thead>
        <tbody>
          {items.length === 0 ? (
            <EmptyRow colSpan={4} message="Nenhum usuário encontrado" />
          ) : (
            items.map((u) => (
              <Tr key={u.id}>
                <Td>
                  <Link
                    href={`/users/${u.id}`}
                    className="font-medium text-brand-600 hover:underline"
                  >
                    {u.name ?? "—"}
                  </Link>
                </Td>
                <Td>{formatPhone(u.phone)}</Td>
                <Td>
                  <Badge status={u.role} />
                </Td>
                <Td>{formatDate(u.created_at)}</Td>
              </Tr>
            ))
          )}
        </tbody>
      </Table>

      <Pagination total={total} skip={skip} limit={LIMIT} onPage={setSkip} />
    </AdminLayout>
  );
}
