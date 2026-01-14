'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Alert } from '@/components/Alert';
import { Card } from '@/components/Card';
import { TaskForm } from '@/components/TaskForm';
import { TaskItem } from '@/components/TaskItem';
import { TaskTable } from '@/components/TaskTable';
import { Header } from '@/components/Header';
import { apiFetch, AuthError } from '@/lib/api';
import { clearToken, getToken } from '@/lib/auth';
import { Task } from '@/lib/types';

export default function TasksPage() {
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actioning, setActioning] = useState(false);
  const [editing, setEditing] = useState<Task | null>(null);
  const [viewMode, setViewMode] = useState<'list' | 'table'>('table'); // Default, but we auto-switch on mobile

  const hasToken = useMemo(() => !!getToken(), []);

  useEffect(() => {
    if (!hasToken) {
      router.replace('/login');
      return;
    }
    // Mobile UX: default to list view on small screens
    try {
      if (typeof window !== 'undefined' && window.innerWidth < 768) {
        setViewMode('list');
      }
    } catch {}
    fetchTasks();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hasToken]);

  async function fetchTasks() {
    setLoading(true);
    setError(null);
    try {
      const data = await apiFetch<Task[]>('/api/tasks');
      setTasks(data || []);
    } catch (err: any) {
      if (err instanceof AuthError) {
        clearToken();
        router.replace('/login');
        return;
      }
      setError(err?.message || 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  }

  async function handleCreate(payload: { title: string; description?: string; priority?: string; due_date?: string }) {
    setActioning(true);
    setError(null);
    try {
      await apiFetch<Task>('/api/tasks', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      await fetchTasks();
    } catch (err: any) {
      if (err instanceof AuthError) {
        clearToken();
        router.replace('/login');
        return;
      }
      setError(err?.message || 'Create failed');
    } finally {
      setActioning(false);
    }
  }

  async function handleUpdate(payload: { title: string; description?: string; priority?: string; due_date?: string }) {
    if (!editing) return;
    setActioning(true);
    setError(null);
    try {
      await apiFetch<Task>(`/api/tasks/${editing.id}`, {
        method: 'PUT',
        body: JSON.stringify(payload),
      });
      setEditing(null);
      await fetchTasks();
    } catch (err: any) {
      if (err instanceof AuthError) {
        clearToken();
        router.replace('/login');
        return;
      }
      setError(err?.message || 'Update failed');
    } finally {
      setActioning(false);
    }
  }

  async function handleComplete(task: Task) {
    setActioning(true);
    setError(null);
    try {
      await apiFetch<Task>(`/api/tasks/${task.id}/complete`, {
        method: 'PATCH',
        body: JSON.stringify({ completed: !task.completed }),
      });
      await fetchTasks();
    } catch (err: any) {
      if (err instanceof AuthError) {
        clearToken();
        router.replace('/login');
        return;
      }
      setError(err?.message || 'Complete failed');
    } finally {
      setActioning(false);
    }
  }

  async function handleDelete(task: Task) {
    setActioning(true);
    setError(null);
    try {
      await apiFetch<void>(`/api/tasks/${task.id}`, {
        method: 'DELETE',
      });
      await fetchTasks();
    } catch (err: any) {
      if (err instanceof AuthError) {
        clearToken();
        router.replace('/login');
        return;
      }
      setError(err?.message || 'Delete failed');
    } finally {
      setActioning(false);
    }
  }

  return (
    <>
      <Header />
      <div className="min-h-screen px-3 sm:px-4 py-6 sm:py-8">
        <div className="mx-auto flex w-full max-w-5xl flex-col gap-5 sm:gap-6">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-theme-primary">Your Tasks</h1>
            <p className="text-sm text-theme-secondary">Manage your todos securely.</p>
          </div>

        {error ? <Alert variant="error">{error}</Alert> : null}

        <Card>
          <h2 className="text-lg font-semibold text-theme-primary">
            {editing ? 'Edit task' : 'Create a new task'}
          </h2>
          <TaskForm
            onSubmit={editing ? handleUpdate : handleCreate}
            initialTask={editing}
            loading={actioning}
          />
          {editing ? (
            <div className="mt-3 text-sm text-slate-400">
              Editing task #{editing.id}. <button className="text-blue-300" onClick={() => setEditing(null)}>Cancel</button>
            </div>
          ) : null}
        </Card>

        <Card className="space-y-3">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <h2 className="text-lg font-semibold text-theme-primary">Task list</h2>
            <div className="flex items-center gap-2">
              <span className="text-sm text-theme-secondary">View:</span>
              <div className="inline-flex rounded-xl border border-theme bg-theme-surface p-1">
                <button
                  onClick={() => setViewMode('table')}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    viewMode === 'table'
                      ? 'bg-blue-500 text-white'
                      : 'text-theme-secondary hover:text-theme-primary'
                  }`}
                >
                  Table
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    viewMode === 'list'
                      ? 'bg-blue-500 text-white'
                      : 'text-theme-secondary hover:text-theme-primary'
                  }`}
                >
                  List
                </button>
              </div>
            </div>
            {loading ? <span className="text-sm text-theme-tertiary">Loading...</span> : null}
          </div>
          {loading ? (
            <p className="text-theme-secondary">Fetching tasks...</p>
          ) : tasks.length === 0 ? (
            <p className="text-theme-secondary">No tasks yet. Add your first task above.</p>
          ) : viewMode === 'table' ? (
            <TaskTable
              tasks={tasks}
              onComplete={handleComplete}
              onEdit={setEditing}
              onDelete={handleDelete}
            />
          ) : (
            <div className="space-y-3">
              {tasks.map((task) => (
                <TaskItem
                  key={task.id}
                  task={task}
                  onComplete={handleComplete}
                  onEdit={setEditing}
                  onDelete={handleDelete}
                />
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
    </>
  );
}
