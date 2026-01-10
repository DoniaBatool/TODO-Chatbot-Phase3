const TOKEN_KEY = 'todo_token';

export function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  if (typeof window === 'undefined') return;
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  if (typeof window === 'undefined') return;
  window.localStorage.removeItem(TOKEN_KEY);
}

export function hasToken(): boolean {
  return !!getToken();
}

export function getUserIdFromToken(): string | null {
  const token = getToken();
  if (!token) return null;

  try {
    // JWT is in format: header.payload.signature
    const parts = token.split('.');
    if (parts.length !== 3) return null;

    // Decode the payload (base64url)
    const payload = JSON.parse(atob(parts[1]));

    // JWT typically has 'sub' (subject) field containing user ID
    return payload.sub || payload.user_id || payload.id || null;
  } catch (error) {
    console.error('Failed to decode JWT:', error);
    return null;
  }
}
