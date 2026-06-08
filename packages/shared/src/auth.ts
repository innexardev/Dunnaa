export interface SendCodeResponse {
  message: string;
  expires_in_seconds: number;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface User {
  id: string;
  phone: string;
  name: string | null;
  email: string | null;
  avatar_url: string | null;
  role: "customer" | "owner" | "staff" | "admin";
  referral_code: string | null;
  referred_by_id: string | null;
}

export interface AuthResponse {
  tokens: TokenResponse;
  user: User;
}
