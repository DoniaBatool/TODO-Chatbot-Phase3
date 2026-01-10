import { clearToken, getToken } from './auth';
import type { ApiError } from './types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class AuthError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers,
  });

  const isJson = res.headers.get('content-type')?.includes('application/json');
  const body = isJson ? await res.json().catch(() => undefined) : undefined;

  if (!res.ok) {
    if (res.status === 401 || res.status === 403) {
      clearToken();
      throw new AuthError(body?.detail || 'Unauthorized', res.status);
    }
    
    // Handle validation errors (array of error objects)
    let errorMessage = 'Request failed';
    if (body?.detail) {
      if (Array.isArray(body.detail)) {
        // Format Pydantic validation errors
        errorMessage = body.detail
          .map((err: any) => {
            const field = err.loc?.slice(1).join('.') || 'field';
            return `${field}: ${err.msg || 'Invalid value'}`;
          })
          .join(', ');
      } else if (typeof body.detail === 'string') {
        errorMessage = body.detail;
      } else {
        errorMessage = body.detail?.message || 'Request failed';
      }
    } else if (body?.message) {
      errorMessage = body.message;
    }
    
    const err: ApiError = {
      status: res.status,
      message: errorMessage,
    };
    throw err;
  }

  return body as T;
}
