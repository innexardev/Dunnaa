"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { ApiError, api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function LoginPage() {
  const router = useRouter();
  const [phone, setPhone] = useState("");
  const [code, setCode] = useState("");
  const [step, setStep] = useState<"phone" | "code">("phone");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSendCode(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const normalized = phone.startsWith("+") ? phone : `+55${phone.replace(/\D/g, "")}`;
      await api.auth.sendCode(normalized);
      setPhone(normalized);
      setStep("code");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erro ao enviar código");
    } finally {
      setLoading(false);
    }
  }

  async function handleVerify(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await api.auth.verify(phone, code);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Código inválido");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-neutral-50 px-4">
      <div className="w-full max-w-sm rounded-xl border border-neutral-200 bg-white p-8 shadow-sm">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-bold text-brand-700">DUNNAA</h1>
          <p className="mt-1 text-sm text-neutral-500">Painel administrativo</p>
        </div>

        {error && (
          <div className="mb-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>
        )}

        {step === "phone" ? (
          <form onSubmit={handleSendCode} className="space-y-4">
            <div>
              <label className="mb-1 block text-sm font-medium text-neutral-700">Telefone</label>
              <Input
                type="tel"
                placeholder="+5511999999999"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                required
              />
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Enviando..." : "Enviar código SMS"}
            </Button>
          </form>
        ) : (
          <form onSubmit={handleVerify} className="space-y-4">
            <div>
              <label className="mb-1 block text-sm font-medium text-neutral-700">
                Código SMS
              </label>
              <Input
                type="text"
                placeholder="123456"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                maxLength={6}
                required
              />
              <p className="mt-1 text-xs text-neutral-500">Enviado para {phone}</p>
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Verificando..." : "Entrar"}
            </Button>
            <button
              type="button"
              onClick={() => {
                setStep("phone");
                setCode("");
              }}
              className="w-full text-sm text-neutral-500 hover:text-neutral-700"
            >
              Voltar
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
