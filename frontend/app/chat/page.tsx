'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Header } from '@/components/Header';
import { getToken, getUserIdFromToken } from '@/lib/auth';
import { apiFetch, AuthError } from '@/lib/api';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  tool_calls?: Array<{ tool: string; params: any; result: any }>;
}

interface Conversation {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  message_count?: number;
}

// Helper to get tool action description
const getToolActionDescription = (tool: string, params: any, result: any): string => {
  switch (tool) {
    case 'add_task':
      return `✅ Task "${params.title || result?.title || 'created'}" added successfully`;
    case 'update_task':
      const updates = [];
      if (params.title) updates.push(`title: "${params.title}"`);
      if (params.description !== undefined) updates.push(`description updated`);
      if (params.priority) updates.push(`priority: ${params.priority}`);
      if (params.due_date) updates.push(`due date: ${new Date(params.due_date).toLocaleString()}`);
      if (params.due_date === null || params.due_date === '') updates.push(`due date removed`);
      if (params.completed !== undefined) updates.push(`completed: ${params.completed ? 'Yes' : 'No'}`);
      return `✅ Task #${params.task_id} updated: ${updates.join(', ') || 'updated'}`;
    case 'delete_task':
      return `🗑️ Task #${params.task_id} deleted successfully`;
    case 'complete_task':
      return `✅ Task #${params.task_id} marked as complete`;
    case 'list_tasks':
      const count = result?.tasks?.length || 0;
      return `📋 Listed ${count} task${count !== 1 ? 's' : ''}`;
    case 'find_task':
      return `🔍 Found task: "${result?.title || params.query}"`;
    case 'set_task_deadline':
      if (params.due_date) {
        return `📅 Due date set for task #${params.task_id}: ${new Date(params.due_date).toLocaleString()}`;
      } else {
        return `📅 Due date removed from task #${params.task_id}`;
      }
    default:
      return `🔧 ${tool} executed`;
  }
};

// Generate conversation title from first message
const generateConversationTitle = (message: string): string => {
  const trimmed = message.trim();
  if (trimmed.length > 50) {
    return trimmed.substring(0, 50) + '...';
  }
  return trimmed || 'New Chat';
};

export default function ChatPage() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [loadingConversations, setLoadingConversations] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const token = getToken();
    const user = getUserIdFromToken();
    
    if (!token || !user) {
      router.replace('/login');
      return;
    }
    
    setIsAuthenticated(true);
    setUserId(user);
    
    // Load conversations list
    loadConversations(user);
    
    // Load latest conversation
    loadLatestConversation(user);
  }, [router]);

  const loadConversations = async (userId: string) => {
    setLoadingConversations(true);
    try {
      const response = await apiFetch(`/api/${userId}/conversations`) as any;
      if (response.conversations) {
        setConversations(response.conversations);
      }
    } catch (error) {
      console.error('Failed to load conversations:', error);
    } finally {
      setLoadingConversations(false);
    }
  };

  const loadLatestConversation = async (userId: string) => {
    try {
      const response = await apiFetch(`/api/${userId}/conversations`) as any;
      if (response.conversations && response.conversations.length > 0) {
        const latestConversation = response.conversations[0];
        await loadConversation(userId, latestConversation.id);
      }
    } catch (error) {
      console.error('Failed to load latest conversation:', error);
    }
  };

  const loadConversation = async (userId: string, convId: number) => {
    try {
      setConversationId(convId);
      const messagesResponse = await apiFetch(`/api/${userId}/conversations/${convId}`) as any;
      if (messagesResponse.messages) {
        const loadedMessages: Message[] = messagesResponse.messages.map((msg: any) => ({
          id: msg.id.toString(),
          role: msg.sender === 'user' ? 'user' : 'assistant',
          content: msg.message,
          timestamp: new Date(msg.created_at),
          tool_calls: msg.tool_calls,
        }));
        setMessages(loadedMessages);
      } else {
        setMessages([]);
      }
    } catch (error) {
      console.error('Failed to load conversation:', error);
    }
  };

  const startNewChat = () => {
    setConversationId(null);
    setMessages([]);
    setInputMessage('');
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputMessage.trim() || !userId || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const currentInput = inputMessage;
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await apiFetch(`/api/${userId}/chat`, {
        method: 'POST',
        body: JSON.stringify({
          message: currentInput,
          conversation_id: conversationId,
        }),
      }) as any;

      // Update conversation ID if new conversation was created
      if (response.conversation_id) {
        const newConvId = response.conversation_id;
        if (newConvId !== conversationId) {
          setConversationId(newConvId);
          // Reload conversations list to include new conversation
          await loadConversations(userId);
        }
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        tool_calls: response.tool_calls,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Reload conversations to update titles/timestamps
      await loadConversations(userId);
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isAuthenticated || !userId) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-theme-background">
        <div className="text-center">
          <p className="text-theme-secondary">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Header />
      <div className="flex min-h-screen bg-theme-background">
        {/* Sidebar */}
        <div
          className={`${
            sidebarOpen ? 'w-64' : 'w-0'
          } transition-all duration-300 border-r border-theme bg-theme-surface overflow-hidden flex flex-col`}
        >
          <div className="p-4 border-b border-theme">
            <button
              onClick={startNewChat}
              className="w-full px-4 py-2 bg-blue-500 hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700 text-white rounded-lg font-medium transition-colors flex items-center gap-2 justify-center shadow-sm"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              New Chat
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-2">
            {loadingConversations ? (
              <div className="text-center text-theme-tertiary text-sm py-4">Loading...</div>
            ) : conversations.length === 0 ? (
              <div className="text-center text-theme-tertiary text-sm py-4">No conversations yet</div>
            ) : (
              <div className="space-y-1">
                {conversations.map((conv) => (
                  <button
                    key={conv.id}
                    onClick={() => loadConversation(userId, conv.id)}
                    className={`w-full text-left px-3 py-2 rounded-lg transition-colors border ${
                      conversationId === conv.id
                        ? 'bg-blue-500/20 dark:bg-blue-500/30 text-blue-600 dark:text-blue-400 border-blue-500/40 dark:border-blue-500/50'
                        : 'hover:bg-theme-card dark:hover:bg-theme-card/50 text-theme-secondary border-transparent hover:border-theme'
                    }`}
                  >
                    <div className="text-sm font-medium truncate text-theme-primary">
                      {conv.title || `Chat ${conv.id}`}
                    </div>
                    <div className="text-xs text-theme-tertiary mt-1">
                      {new Date(conv.updated_at).toLocaleDateString()}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col">
          {/* Top Bar */}
          <div className="border-b border-theme bg-theme-surface p-4 flex items-center justify-between">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 hover:bg-theme-card dark:hover:bg-theme-card/50 rounded-lg transition-colors text-theme-secondary hover:text-theme-primary"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <h1 className="text-lg font-semibold text-theme-primary">AI Chat Assistant</h1>
            <div className="w-9"></div>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center text-theme-secondary max-w-2xl">
                  <p className="text-2xl mb-4">👋 Welcome!</p>
                  <p className="text-base mb-2">Start a conversation to manage your tasks with AI</p>
                  <p className="text-sm mt-4 text-theme-tertiary">Try: &quot;Add a task to buy groceries&quot; or &quot;Show my tasks&quot;</p>
                  <div className="mt-6 text-left text-sm text-theme-tertiary space-y-2 max-w-md mx-auto">
                    <p className="font-semibold text-theme-secondary mb-3">You can:</p>
                    <p>• Add tasks: &quot;Add task to call mom tomorrow&quot;</p>
                    <p>• Update by ID or title: &quot;Update task 1 title to Buy groceries&quot; or &quot;Update buy milk task title to Buy groceries&quot;</p>
                    <p>• Delete by ID or title: &quot;Delete task 2&quot; or &quot;Delete buy milk task&quot;</p>
                    <p>• Mark complete: &quot;Mark task 1 as complete&quot; or &quot;Mark buy milk task as complete&quot;</p>
                    <p>• Mark incomplete: &quot;Mark task 1 as incomplete&quot; or &quot;Mark grocery task as incomplete&quot;</p>
                    <p>• Set due dates: &quot;Set due date for task 1 to Jan 20, 2026 3 PM&quot;</p>
                    <p>• Remove due dates: &quot;Remove due date from task 1&quot;</p>
                  </div>
                </div>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                      message.role === 'user'
                        ? 'bg-blue-500 text-white'
                        : 'bg-theme-surface text-theme-primary'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap break-words">{message.content}</p>
                    {message.tool_calls && message.tool_calls.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-theme">
                        <p className="text-xs font-semibold mb-2 opacity-90">
                          ✅ Actions completed:
                        </p>
                        <div className="space-y-1.5">
                          {message.tool_calls.map((tool, idx) => {
                            const description = getToolActionDescription(
                              tool.tool,
                              tool.params || {},
                              tool.result || {}
                            );
                            return (
                              <div
                                key={idx}
                                className={`text-xs p-2 rounded-lg ${
                                  message.role === 'user'
                                    ? 'bg-blue-400/20 text-white'
                                    : 'bg-green-500/10 text-green-600 dark:text-green-400'
                                }`}
                              >
                                {description}
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}
                    <p className={`text-xs mt-2 ${message.role === 'user' ? 'text-blue-100' : 'text-theme-tertiary'}`}>
                      {message.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))
            )}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-theme-surface rounded-2xl px-4 py-3">
                  <div className="flex items-center gap-2 text-theme-secondary">
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                        fill="none"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>
                    <span className="text-sm">AI is thinking...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-theme p-4 bg-theme-surface">
            <form onSubmit={handleSendMessage} className="flex gap-2">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Type your message... (e.g., 'Update task 1 title to Buy groceries')"
                disabled={isLoading}
                className="flex-1 px-4 py-3 rounded-xl border border-theme bg-theme-card text-theme-primary placeholder:text-theme-tertiary focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                style={{
                  backgroundColor: 'var(--bg-card)',
                  color: 'var(--text-primary)',
                  borderColor: 'var(--border-color)',
                }}
              />
              <button
                type="submit"
                disabled={isLoading || !inputMessage.trim()}
                className="px-6 py-3 bg-blue-500 text-white rounded-xl hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
              >
                {isLoading ? (
                  <span className="flex items-center gap-2">
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                        fill="none"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>
                    Sending...
                  </span>
                ) : (
                  'Send'
                )}
              </button>
            </form>
          </div>
        </div>
      </div>
    </>
  );
}
