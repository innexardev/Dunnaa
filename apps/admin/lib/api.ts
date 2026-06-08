import type {
  AdminAuditLog,
  AdminDashboard,
  AdminEstablishment,
  AdminPayment,
  AdminSubscription,
  AdminUser,
  AuthResponse,
  Paginated,
  SendCodeResponse,
  SystemSetting,
} from "@dunnaa/shared";

import { clearTokens, getAccessToken, getRefreshToken, setTokens } from "./auth-storage";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  retry = true,
): Promise<T> {
  const token = getAccessToken();
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(options.headers ?? {}),
  };
  if (token) {
    (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE}${path}`, { ...options, headers });

  if (res.status === 401 && retry) {
    const refreshed = await refreshAccessToken();
    if (refreshed) return request<T>(path, options, false);
    clearTokens();
    if (typeof window !== "undefined") window.location.href = "/login";
    throw new ApiError(401, "Sessão expirada");
  }

  if (!res.ok) {
    let message = res.statusText;
    try {
      const body = await res.json();
      message = body?.error?.message ?? body?.detail ?? message;
    } catch {
      /* ignore */
    }
    throw new ApiError(res.status, String(message));
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

async function refreshAccessToken(): Promise<boolean> {
  const refresh = getRefreshToken();
  if (!refresh) return false;
  try {
    const res = await fetch(`${BASE}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refresh }),
    });
    if (!res.ok) return false;
    const data = await res.json();
    setTokens(data.access_token, data.refresh_token ?? refresh);
    return true;
  } catch {
    return false;
  }
}

export const api = {
  auth: {
    sendCode: (phone: string) =>
      request<SendCodeResponse>("/auth/send-code", {
        method: "POST",
        body: JSON.stringify({ phone }),
      }),

    verify: async (phone: string, code: string) => {
      const data = await request<AuthResponse>("/auth/verify", {
        method: "POST",
        body: JSON.stringify({ phone, code }),
      });
      if (data.user.role !== "admin") {
        throw new ApiError(403, "Acesso restrito a administradores");
      }
      setTokens(data.tokens.access_token, data.tokens.refresh_token);
      return data;
    },

    logout: () => {
      clearTokens();
    },
  },

  admin: {
    dashboard: () => request<AdminDashboard>("/admin/dashboard"),

    establishments: (params?: { skip?: number; limit?: number; status?: string }) => {
      const q = new URLSearchParams();
      if (params?.skip) q.set("skip", String(params.skip));
      if (params?.limit) q.set("limit", String(params.limit));
      if (params?.status) q.set("status", params.status);
      const qs = q.toString();
      return request<Paginated<AdminEstablishment>>(
        `/admin/establishments${qs ? `?${qs}` : ""}`,
      );
    },

    establishment: (id: string) =>
      request<AdminEstablishment>(`/admin/establishments/${id}`),

    updateEstablishment: (id: string, body: Record<string, unknown>) =>
      request<AdminEstablishment>(`/admin/establishments/${id}`, {
        method: "PATCH",
        body: JSON.stringify(body),
      }),

    users: (params?: { skip?: number; limit?: number; search?: string; role?: string }) => {
      const q = new URLSearchParams();
      if (params?.skip) q.set("skip", String(params.skip));
      if (params?.limit) q.set("limit", String(params.limit));
      if (params?.search) q.set("search", params.search);
      if (params?.role) q.set("role", params.role);
      const qs = q.toString();
      return request<Paginated<AdminUser>>(`/admin/users${qs ? `?${qs}` : ""}`);
    },

    user: (id: string) => request<AdminUser>(`/admin/users/${id}`),

    updateUser: (id: string, body: Record<string, unknown>) =>
      request<AdminUser>(`/admin/users/${id}`, {
        method: "PATCH",
        body: JSON.stringify(body),
      }),

    subscriptions: (params?: { skip?: number; limit?: number; status?: string }) => {
      const q = new URLSearchParams();
      if (params?.skip) q.set("skip", String(params.skip));
      if (params?.limit) q.set("limit", String(params.limit));
      if (params?.status) q.set("status", params.status);
      const qs = q.toString();
      return request<Paginated<AdminSubscription>>(
        `/admin/subscriptions${qs ? `?${qs}` : ""}`,
      );
    },

    payments: (params?: { skip?: number; limit?: number; status?: string }) => {
      const q = new URLSearchParams();
      if (params?.skip) q.set("skip", String(params.skip));
      if (params?.limit) q.set("limit", String(params.limit));
      if (params?.status) q.set("status", params.status);
      const qs = q.toString();
      return request<Paginated<AdminPayment>>(`/admin/payments${qs ? `?${qs}` : ""}`);
    },

    auditLogs: (params?: { skip?: number; limit?: number }) => {
      const q = new URLSearchParams();
      if (params?.skip) q.set("skip", String(params.skip));
      if (params?.limit) q.set("limit", String(params.limit));
      const qs = q.toString();
      return request<Paginated<AdminAuditLog>>(`/admin/audit-logs${qs ? `?${qs}` : ""}`);
    },

    settings: () =>
      request<{ items: SystemSetting[]; total: number }>("/admin/settings"),
  },
};

export { ApiError };
