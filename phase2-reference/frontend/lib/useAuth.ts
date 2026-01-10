'use client';

import { useEffect, useState } from 'react';
import { clearToken, getToken, setToken } from './auth';
import type { AuthUser, LoginResponse, SignupResponse } from './types';
import { apiFetch, AuthError } from './api';

export type AuthState = {
  token: string | null;
  user: AuthUser | null;
  loading: boolean;
  error: string | null;
};

export function useAuth() {
  const [state, setState] = useState<AuthState>({
    token: null,
    user: null,
    loading: true,
    error: null,
  });

  useEffect(() => {
    const token = getToken();
    setState((prev) => ({ ...prev, token, loading: false }));
  }, []);

  async function login(email: string, password: string) {
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const data = await apiFetch<LoginResponse>('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });
      setToken(data.access_token);
      setState({ token: data.access_token, user: data.user, loading: false, error: null });
      return data;
    } catch (err: any) {
      const message = err?.message || 'Login failed';
      setState((prev) => ({ ...prev, loading: false, error: message }));
      throw err;
    }
  }

  async function signup(email: string, password: string, name?: string) {
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const data = await apiFetch<SignupResponse>('/api/auth/signup', {
        method: 'POST',
        body: JSON.stringify({ email, password, name }),
      });
      setState((prev) => ({ ...prev, loading: false }));
      return data;
    } catch (err: any) {
      const message = err?.message || 'Signup failed';
      setState((prev) => ({ ...prev, loading: false, error: message }));
      throw err;
    }
  }

  function logout() {
    clearToken();
    setState({ token: null, user: null, loading: false, error: null });
  }

  return { ...state, login, logout, signup };
}

export function useAuthGuard() {
  const [token, setTokenState] = useState<string | null>(null);
  useEffect(() => {
    const t = getToken();
    setTokenState(t);
  }, []);
  return token;
}
