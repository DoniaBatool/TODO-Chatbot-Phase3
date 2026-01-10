export type Task = {
  id: number;
  title: string;
  description?: string | null;
  completed: boolean;
  created_at?: string;
  updated_at?: string;
};

export type AuthUser = {
  id: string;
  email: string;
  name?: string | null;
};

export type LoginResponse = {
  access_token: string;
  token_type: string;
  user: AuthUser;
};

export type SignupResponse = {
  id: string;
  email: string;
  name?: string | null;
};

export type ApiError = {
  status: number;
  message: string;
  unauthorized?: boolean;
};
