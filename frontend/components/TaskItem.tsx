'use client';

import React from 'react';
import { Task } from '@/lib/types';
import { Button } from './Button';
import { PriorityBadge } from './PriorityBadge';
import clsx from 'clsx';

type Props = {
  task: Task;
  onComplete: (task: Task) => void;
  onEdit: (task: Task) => void;
  onDelete: (task: Task) => void;
};

function formatDueDate(dueDateStr: string): string {
  const dueDate = new Date(dueDateStr);
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);
  const dueDay = new Date(dueDate.getFullYear(), dueDate.getMonth(), dueDate.getDate());

  // Format time
  const timeStr = dueDate.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  });

  // Check if today, tomorrow, or specific date
  if (dueDay.getTime() === today.getTime()) {
    return `Today at ${timeStr}`;
  } else if (dueDay.getTime() === tomorrow.getTime()) {
    return `Tomorrow at ${timeStr}`;
  } else {
    const dateStr = dueDate.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: dueDate.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
    });
    return `${dateStr} at ${timeStr}`;
  }
}

export function TaskItem({ task, onComplete, onEdit, onDelete }: Props) {
  return (
    <div className="task-item rounded-2xl border border-theme bg-theme-surface/40 p-4 sm:p-5">
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div className="flex flex-col gap-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2">
          <span className="text-sm font-mono font-semibold text-theme-tertiary">
            #{task.id}
          </span>
          <span
            className={clsx(
              'task-title text-base sm:text-lg font-semibold truncate max-w-full',
              task.completed && 'line-through completed'
            )}
          >
            {task.title}
          </span>
          <PriorityBadge priority={task.priority} />
          {task.completed ? (
            <span className="rounded-full bg-green-500/20 px-2 py-0.5 text-xs text-green-200">Done</span>
          ) : null}
        </div>
        {task.description ? (
          <p className="task-description text-sm text-theme-secondary break-words">{task.description}</p>
        ) : null}
        {task.due_date ? (
          <div className="flex items-center gap-1 text-xs text-theme-secondary">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="16" y1="2" x2="16" y2="6"></line>
              <line x1="8" y1="2" x2="8" y2="6"></line>
              <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
            <span>{formatDueDate(task.due_date)}</span>
          </div>
        ) : null}
        </div>

        <div className="flex flex-wrap gap-2 sm:justify-end">
          <Button variant="secondary" onClick={() => onComplete(task)} className="px-3 py-2">
            {task.completed ? 'Mark Incomplete' : 'Complete'}
          </Button>
          <Button variant="ghost" onClick={() => onEdit(task)} className="px-3 py-2">
            Edit
          </Button>
          <Button
            variant="ghost"
            onClick={() => onDelete(task)}
            className="px-3 py-2 text-red-400 hover:text-red-300"
          >
            Delete
          </Button>
        </div>
      </div>
    </div>
  );
}
