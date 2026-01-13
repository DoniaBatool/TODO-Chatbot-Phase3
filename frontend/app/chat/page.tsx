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
      if (params.due_date === null) updates.push(`due date removed`);
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

export default function ChatPage() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<number | null>(null);
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
    
    // Load conversation history
    loadConversationHistory(user);
  }, [router]);

  const loadConversationHistory = async (userId: string) => {
    try {
      const response = await apiFetch(`/api/${userId}/conversations`) as any;
      if (response.conversations && response.conversations.length > 0) {
        const latestConversation = response.conversations[0];
        setConversationId(latestConversation.id);
        
        // Load messages for this conversation
        const messagesResponse = await apiFetch(`/api/${userId}/conversations/${latestConversation.id}`) as any;
        if (messagesResponse.messages) {
          const loadedMessages: Message[] = messagesResponse.messages.map((msg: any) => ({
            id: msg.id,
            role: msg.sender === 'user' ? 'user' : 'assistant',
            content: msg.message,
            timestamp: new Date(msg.created_at),
            tool_calls: msg.tool_calls,
          }));
          setMessages(loadedMessages);
        }
      }
    } catch (error) {
      console.error('Failed to load conversation history:', error);
    }
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
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await apiFetch(`/api/${userId}/chat`, {
        method: 'POST',
        body: JSON.stringify({
          message: inputMessage,
          conversation_id: conversationId,
        }),
      }) as any;

      if (response.conversation_id && !conversationId) {
        setConversationId(response.conversation_id);
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        tool_calls: response.tool_calls,
      };

      setMessages((prev) => [...prev, assistantMessage]);
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
        <div className="flex-1 px-2 sm:px-4 py-4 sm:py-8">
          <div className="mx-auto flex max-w-4xl flex-col h-[calc(100vh-8rem)] sm:h-[calc(100vh-10rem)]">
            {/* Header */}
            <div className="flex items-center justify-between flex-wrap gap-2 px-2 sm:px-4 mb-4">
              <div>
                <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-theme-primary">
                  AI Chat Assistant
                </h1>
                <p className="text-xs sm:text-sm text-theme-secondary">
                  Chat naturally to manage your tasks with AI
                </p>
              </div>
            </div>

            {/* Chat Container */}
            <div className="flex-1 flex flex-col bg-theme-card rounded-2xl shadow-lg overflow-hidden border border-theme">
              {/* Messages Area */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 ? (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center text-theme-secondary">
                      <p className="text-lg mb-2">👋 Welcome!</p>
                      <p className="text-sm mb-1">Start a conversation to manage your tasks with AI</p>
                      <p className="text-xs mt-2 text-theme-tertiary">Try: &quot;Add a task to buy groceries&quot; or &quot;Show my tasks&quot;</p>
                      <div className="mt-4 text-left text-xs text-theme-tertiary space-y-1 max-w-md mx-auto">
                        <p className="font-semibold text-theme-secondary mb-2">You can:</p>
                        <p>• Add tasks: &quot;Add task to call mom tomorrow&quot;</p>
                        <p>• Update tasks: &quot;Update task 1 title to Buy groceries&quot;</p>
                        <p>• Delete tasks: &quot;Delete task 2&quot;</p>
                        <p>• Mark complete: &quot;Mark task 1 as complete&quot;</p>
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
                              {message.role === 'user' ? '🔧 Actions performed:' : '✅ Actions completed:'}
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
        </div>
      </div>
    </>
  );
}
