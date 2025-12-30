'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Alert } from '@/components/Alert';
import { Button } from '@/components/Button';
import { Card } from '@/components/Card';
import { TaskForm } from '@/components/TaskForm';
import { TaskItem } from '@/components/TaskItem';
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

  const hasToken = useMemo(() => !!getToken(), []);

  useEffect(() => {
    if (!hasToken) {
      router.replace('/login');
      return;
    }
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

  async function handleCreate(payload: { title: string; description?: string }) {
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

  async function handleUpdate(payload: { title: string; description?: string }) {
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

  function handleLogout() {
    clearToken();
    router.replace('/login');
  }

  return (
    <div className="min-h-screen px-4 py-8">
      <div className="mx-auto flex max-w-5xl flex-col gap-6">
        <header className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white">Your Tasks</h1>
            <p className="text-sm text-slate-300">Manage your todos securely.</p>
          </div>
          <Button variant="secondary" onClick={handleLogout}>
            Logout
          </Button>
        </header>

        {error ? <Alert variant="error">{error}</Alert> : null}

        <Card>
          <h2 className="text-lg font-semibold text-white">
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
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">Task list</h2>
            {loading ? <span className="text-sm text-slate-400">Loading...</span> : null}
          </div>
          {loading ? (
            <p className="text-slate-400">Fetching tasks...</p>
          ) : tasks.length === 0 ? (
            <p className="text-slate-300">No tasks yet. Add your first task above.</p>
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
  );
}
