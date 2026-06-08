const TOKEN_KEY = "dunnaa_admin_access";
const REFRESH_KEY = "dunnaa_admin_refresh";
const COOKIE_KEY = "dunnaa_admin_token";

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(REFRESH_KEY);
}

export function setTokens(access: string, refresh: string) {
  localStorage.setItem(TOKEN_KEY, access);
  localStorage.setItem(REFRESH_KEY, refresh);
  document.cookie = `${COOKIE_KEY}=${access}; path=/; max-age=${60 * 60 * 24 * 7}; SameSite=Lax`;
}

export function clearTokens() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
  document.cookie = `${COOKIE_KEY}=; path=/; max-age=0`;
}

export function isAuthenticated(): boolean {
  return !!getAccessToken();
}
