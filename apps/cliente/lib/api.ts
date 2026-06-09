import type {
  Appointment,
  AuthResponse,
  AvailabilityResponse,
  Establishment,
  EstablishmentList,
  QueueEntry,
  SendCodeResponse,
  Service,
  StaffMember,
} from "@dunnaa/shared";

import { clearTokens, getAccessToken, getRefreshToken, setTokens } from "./auth";

const BASE = process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

async function parseError(res: Response): Promise<string> {
  try {
    const body = await res.json();
    return body?.error?.message ?? body?.detail?.message ?? body?.detail ?? res.statusText;
  } catch {
    return res.statusText;
  }
}

async function request<T>(path: string, options: RequestInit = {}, retry = true): Promise<T> {
  const token = await getAccessToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${BASE}${path}`, { ...options, headers });

  if (res.status === 401 && retry) {
    const refreshed = await refreshAccessToken();
    if (refreshed) return request<T>(path, options, false);
    await clearTokens();
    throw new ApiError(401, "Sessão expirada");
  }

  if (!res.ok) throw new ApiError(res.status, await parseError(res));
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

async function refreshAccessToken(): Promise<boolean> {
  const refresh = await getRefreshToken();
  if (!refresh) return false;
  try {
    const res = await fetch(`${BASE}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refresh }),
    });
    if (!res.ok) return false;
    const data = await res.json();
    await setTokens(data.access_token, data.refresh_token ?? refresh);
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
      await setTokens(data.tokens.access_token, data.tokens.refresh_token);
      return data;
    },

    logout: () => clearTokens(),
  },

  establishments: {
    search: (params?: { q?: string; city?: string; page?: number }) => {
      const q = new URLSearchParams();
      if (params?.q) q.set("q", params.q);
      if (params?.city) q.set("city", params.city);
      if (params?.page) q.set("page", String(params.page));
      const qs = q.toString();
      return request<EstablishmentList>(`/establishments${qs ? `?${qs}` : ""}`);
    },

    get: (id: string) => request<Establishment>(`/establishments/${id}`),

    services: (id: string) =>
      request<Service[]>(`/establishments/${id}/services`),

    staff: (id: string) =>
      request<StaffMember[]>(`/establishments/${id}/staff`),
  },

  appointments: {
    list: () => request<Appointment[]>("/appointments"),

    create: (body: {
      establishment_id: string;
      service_id: string;
      staff_id: string;
      scheduled_at: string;
      payment_type?: string;
    }) =>
      request<Appointment>("/appointments", {
        method: "POST",
        body: JSON.stringify(body),
      }),
  },

  availability: (establishmentId: string, staffId: string, serviceId: string, date: string) =>
    request<AvailabilityResponse>(
      `/establishments/${establishmentId}/staff/${staffId}/availability?service_id=${serviceId}&date=${date}`,
    ),

  queue: {
    my: () => request<QueueEntry[]>("/queue/my"),

    join: (establishmentId: string) =>
      request<QueueEntry>("/queue", {
        method: "POST",
        body: JSON.stringify({ establishment_id: establishmentId }),
      }),
  },

  checkin: {
    scan: (qrToken: string) =>
      request<{ success: boolean; message?: string }>("/checkins", {
        method: "POST",
        body: JSON.stringify({ qr_token: qrToken }),
      }),
  },
};
