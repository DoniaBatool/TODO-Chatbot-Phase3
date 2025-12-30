'use client';

import React, { useState, useEffect } from 'react';
import { Button } from './Button';
import { Input } from './Input';
import { Task } from '@/lib/types';
import { Alert } from './Alert';

type Props = {
  onSubmit: (payload: { title: string; description?: string }) => Promise<void> | void;
  initialTask?: Task | null;
  loading?: boolean;
};

export function TaskForm({ onSubmit, initialTask = null, loading = false }: Props) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (initialTask) {
      setTitle(initialTask.title || '');
      setDescription(initialTask.description || '');
    } else {
      setTitle('');
      setDescription('');
    }
  }, [initialTask]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!title || title.length < 1 || title.length > 200) {
      setError('Title must be between 1 and 200 characters.');
      return;
    }
    setError(null);
    await onSubmit({ title, description: description || undefined });
    if (!initialTask) {
      setTitle('');
      setDescription('');
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <Input
        label="Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="New task title"
        maxLength={200}
        required
      />
      <label className="flex flex-col gap-1 text-sm text-slate-200">
        <span>Description</span>
        <textarea
          className="rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-slate-100 placeholder:text-slate-500 focus:border-blue-500 focus:outline-none"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Optional description"
          maxLength={1000}
          rows={3}
        />
      </label>
      {error ? <Alert variant="error">{error}</Alert> : null}
      <div className="flex gap-2">
        <Button type="submit" disabled={loading}>
          {initialTask ? 'Update Task' : 'Create Task'}
        </Button>
      </div>
    </form>
  );
}
