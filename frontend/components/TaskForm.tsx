'use client';

import React, { useState, useEffect } from 'react';
import { Button } from './Button';
import { Input } from './Input';
import { Task } from '@/lib/types';
import { Alert } from './Alert';

type Props = {
  onSubmit: (payload: { title: string; description?: string; priority?: string; due_date?: string }) => Promise<void> | void;
  initialTask?: Task | null;
  loading?: boolean;
};

export function TaskForm({ onSubmit, initialTask = null, loading = false }: Props) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState('medium');
  const [dueDate, setDueDate] = useState('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (initialTask) {
      setTitle(initialTask.title || '');
      setDescription(initialTask.description || '');
      setPriority(initialTask.priority || 'medium');

      // Format due_date for datetime-local input
      if (initialTask.due_date) {
        const date = new Date(initialTask.due_date);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        setDueDate(`${year}-${month}-${day}T${hours}:${minutes}`);
      } else {
        setDueDate('');
      }
    } else {
      setTitle('');
      setDescription('');
      setPriority('medium');
      setDueDate('');
    }
  }, [initialTask]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!title || title.length < 1 || title.length > 200) {
      setError('Title must be between 1 and 200 characters.');
      return;
    }
    setError(null);

    // Convert due_date to ISO format preserving local timezone
    // datetime-local input gives us local time, we need to preserve it
    let dueDateISO: string | undefined = undefined;
    if (dueDate) {
      // datetime-local parses as local time. Converting to ISO (UTC) is correct for storage.
      // IMPORTANT: Do NOT manually apply timezoneOffset here (it double-shifts time).
      dueDateISO = new Date(dueDate).toISOString();
    }

    await onSubmit({
      title,
      description: description || undefined,
      priority,
      due_date: dueDateISO
    });

    if (!initialTask) {
      setTitle('');
      setDescription('');
      setPriority('medium');
      setDueDate('');
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label="Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="New task title"
        maxLength={200}
        required
      />
      <label className="flex flex-col gap-1 text-sm text-theme-secondary">
        <span className="text-theme-primary">Description</span>
        <textarea
          className="task-textarea rounded-xl px-3 py-2 min-h-[96px]"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Optional description"
          maxLength={1000}
          rows={3}
        />
      </label>
      <label className="flex flex-col gap-1 text-sm text-theme-secondary">
        <span className="text-theme-primary">Priority</span>
        <select
          className="input-theme w-full rounded-xl border px-3 py-2 transition-all duration-200"
          value={priority}
          onChange={(e) => setPriority(e.target.value)}
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      </label>
      <label className="flex flex-col gap-1 text-sm text-theme-secondary">
        <span className="text-theme-primary">Due Date & Time (Optional)</span>
        <input
          type="datetime-local"
          className="input-theme w-full rounded-xl border px-3 py-2 transition-all duration-200"
          value={dueDate}
          onChange={(e) => setDueDate(e.target.value)}
        />
      </label>
      {error ? <Alert variant="error">{error}</Alert> : null}
      <div className="flex flex-col sm:flex-row gap-2">
        <Button type="submit" disabled={loading}>
          {initialTask ? 'Update Task' : 'Create Task'}
        </Button>
      </div>
    </form>
  );
}
