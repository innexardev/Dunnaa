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
import type { AdminEstablishment, EstablishmentStatus } from "@dunnaa/shared";

export default function EstablishmentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [item, setItem] = useState<AdminEstablishment | null>(null);
  const [status, setStatus] = useState<EstablishmentStatus>("active");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    api.admin
      .establishment(id)
      .then((data) => {
        setItem(data);
        setStatus(data.status);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "Erro ao carregar"));
  }, [id]);

  async function handleSave() {
    setSaving(true);
    setError("");
    setSuccess("");
    try {
      const updated = await api.admin.updateEstablishment(id, { status });
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
        title={item?.name ?? "Estabelecimento"}
        action={
          <Button variant="ghost" onClick={() => router.push("/establishments")}>
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
            <p className="text-sm text-neutral-500">Slug</p>
            <p className="font-medium">{item.slug}</p>
          </div>
          <div>
            <p className="text-sm text-neutral-500">Telefone</p>
            <p className="font-medium">{formatPhone(item.phone)}</p>
          </div>
          <div>
            <p className="text-sm text-neutral-500">Localização</p>
            <p className="font-medium">
              {item.city}, {item.state}
            </p>
          </div>
          <div>
            <p className="text-sm text-neutral-500">Status atual</p>
            <Badge status={item.status} />
          </div>
          <div>
            <p className="mb-1 text-sm text-neutral-500">Alterar status</p>
            <Select value={status} onChange={(e) => setStatus(e.target.value as EstablishmentStatus)}>
              <option value="pending">Pending</option>
              <option value="active">Active</option>
              <option value="suspended">Suspended</option>
              <option value="closed">Closed</option>
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
