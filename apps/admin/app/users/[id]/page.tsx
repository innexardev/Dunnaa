"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { AdminLayout } from "@/components/admin-layout";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/input";
import { PageHeader } from "@/components/ui/table";
import { ApiError, api } from "@/lib/api";
import { formatDate, formatPhone } from "@/lib/utils";
import type { AdminUser, UserRole } from "@dunnaa/shared";

export default function UserDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [item, setItem] = useState<AdminUser | null>(null);
  const [role, setRole] = useState<UserRole>("customer");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    api.admin
      .user(id)
      .then((data) => {
        setItem(data);
        setRole(data.role);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "Erro ao carregar"));
  }, [id]);

  async function handleSave() {
    setSaving(true);
    setError("");
    setSuccess("");
    try {
      const updated = await api.admin.updateUser(id, { role });
      setItem(updated);
      setSuccess("Salvo com sucesso");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erro ao salvar");
    } finally {
      setSaving(false);
    }
  }

  return (
    <AdminLayout>
      <PageHeader
        title={item?.name ?? item?.phone ?? "Usuário"}
        action={
          <Button variant="ghost" onClick={() => router.push("/users")}>
            Voltar
          </Button>
        }
      />

      {error && (
        <div className="mb-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>
      )}
      {success && (
        <div className="mb-4 rounded-md bg-green-50 px-3 py-2 text-sm text-green-700">
          {success}
        </div>
      )}

      {item && (
        <div className="max-w-lg space-y-4 rounded-lg border border-neutral-200 bg-white p-6">
          <div>
            <p className="text-sm text-neutral-500">Telefone</p>
            <p className="font-medium">{formatPhone(item.phone)}</p>
          </div>
          <div>
            <p className="text-sm text-neutral-500">Email</p>
            <p className="font-medium">{item.email ?? "—"}</p>
          </div>
          <div>
            <p className="text-sm text-neutral-500">Role atual</p>
            <Badge status={item.role} />
          </div>
          <div>
            <p className="mb-1 text-sm text-neutral-500">Alterar role</p>
            <Select value={role} onChange={(e) => setRole(e.target.value as UserRole)}>
              <option value="customer">Customer</option>
              <option value="owner">Owner</option>
              <option value="staff">Staff</option>
              <option value="admin">Admin</option>
            </Select>
          </div>
          <div>
            <p className="text-sm text-neutral-500">Criado em</p>
            <p className="font-medium">{formatDate(item.created_at)}</p>
          </div>
          <Button onClick={handleSave} disabled={saving}>
            {saving ? "Salvando..." : "Salvar"}
          </Button>
        </div>
      )}

      {!item && !error && <p className="text-neutral-500">Carregando...</p>}
    </AdminLayout>
  );
}
