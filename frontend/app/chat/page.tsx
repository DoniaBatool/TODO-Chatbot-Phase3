'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ChatKit, useChatKit } from '@openai/chatkit-react';
import { Header } from '@/components/Header';
import { getToken, getUserIdFromToken } from '@/lib/auth';
import { apiFetch, AuthError } from '@/lib/api';

export default function ChatPage() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);

  useEffect(() => {
    const token = getToken();
    const user = getUserIdFromToken();
    
    if (!token || !user) {
      router.replace('/login');
      return;
    }
    
    setIsAuthenticated(true);
    setUserId(user);
  }, [router]);

  // Build API URL for ChatKit adapter endpoint
  const apiUrl = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/chatkit`;
  
  // Domain key for production (required for hosted ChatKit)
  const domainKeyValue = process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY;

  // Build API config - conditionally include domainKey only if it exists
  const apiConfig: {
    url: string;
    domainKey?: string;
    fetch: (input: RequestInfo | URL, init?: RequestInit) => Promise<Response>;
  } = {
    url: apiUrl,
    // Custom fetch function to inject JWT token in headers
    fetch: async (input: RequestInfo | URL, init?: RequestInit) => {
      const token = getToken();
      
      // Add authentication header
      const headers = {
        ...init?.headers,
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
      };

      return fetch(input, {
        ...init,
        headers,
        credentials: 'include',
      });
    },
  };

  // Only add domainKey if it exists (required for production)
  if (domainKeyValue) {
    apiConfig.domainKey = domainKeyValue;
  }

  const { control } = useChatKit({
    api: apiConfig,
  });

  if (!isAuthenticated || !userId) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-theme-secondary">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Header />
      <div className="flex min-h-screen">
        <div className="flex-1 px-2 sm:px-4 py-4 sm:py-8 lg:pl-0">
          <div className="mx-auto flex max-w-4xl flex-col gap-3 sm:gap-4 h-[calc(100vh-8rem)] sm:h-[calc(100vh-12rem)]">
            {/* Header */}
            <div className="flex items-center justify-between flex-wrap gap-2 px-2 sm:px-0">
              <div>
                <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-theme-primary">
                  AI Chat Assistant
                </h1>
                <p className="text-xs sm:text-sm text-theme-secondary">
                  Chat naturally to manage your tasks with AI
                </p>
              </div>
            </div>

            {/* ChatKit Component */}
            <div className="flex-1 rounded-2xl shadow-inner overflow-hidden" style={{ minHeight: '500px' }}>
              <ChatKit 
                control={control} 
                className="h-full w-full"
              />
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
