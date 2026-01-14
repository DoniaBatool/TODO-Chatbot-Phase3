'use client';

import React from 'react';
import { Task } from '@/lib/types';
import { Button } from './Button';
import { PriorityBadge } from './PriorityBadge';
import clsx from 'clsx';

type Props = {
  tasks: Task[];
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

export function TaskTable({ tasks, onComplete, onEdit, onDelete }: Props) {
  if (tasks.length === 0) {
    return (
      <div className="text-center py-8 text-theme-secondary">
        No tasks found. Create your first task above.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-2xl border border-theme bg-theme-background">
      <table className="min-w-[900px] w-full divide-y divide-theme-border">
        <thead className="bg-theme-surface/80 backdrop-blur sticky top-0 z-10">
          <tr>
            <th className="px-4 sm:px-6 py-3 text-left text-xs font-medium text-theme-secondary uppercase tracking-wider">
              ID
            </th>
            <th className="px-4 sm:px-6 py-3 text-left text-xs font-medium text-theme-secondary uppercase tracking-wider">
              Task
            </th>
            <th className="px-4 sm:px-6 py-3 text-left text-xs font-medium text-theme-secondary uppercase tracking-wider">
              Priority
            </th>
            <th className="px-4 sm:px-6 py-3 text-left text-xs font-medium text-theme-secondary uppercase tracking-wider">
              Status
            </th>
            <th className="hidden md:table-cell px-4 sm:px-6 py-3 text-left text-xs font-medium text-theme-secondary uppercase tracking-wider">
              Due Date
            </th>
            <th className="hidden lg:table-cell px-4 sm:px-6 py-3 text-left text-xs font-medium text-theme-secondary uppercase tracking-wider">
              Created
            </th>
            <th className="px-4 sm:px-6 py-3 text-right text-xs font-medium text-theme-secondary uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-theme-background divide-y divide-theme-border">
          {tasks.map((task) => (
            <tr
              key={task.id}
              className={clsx(
                'hover:bg-theme-surface/60 transition-colors',
                task.completed && 'opacity-60'
              )}
            >
              <td className="px-4 sm:px-6 py-4 whitespace-nowrap">
                <span className="text-sm font-mono font-semibold text-theme-primary">
                  #{task.id}
                </span>
              </td>
              <td className="px-4 sm:px-6 py-4">
                <div className="flex flex-col">
                  <span
                    className={clsx(
                      'task-title font-medium text-theme-primary',
                      task.completed && 'line-through'
                    )}
                  >
                    {task.title}
                  </span>
                  {task.description && (
                    <span className="task-description text-sm text-theme-secondary mt-1">
                      {task.description}
                    </span>
                  )}
                </div>
              </td>
              <td className="px-4 sm:px-6 py-4 whitespace-nowrap">
                <PriorityBadge priority={task.priority} />
              </td>
              <td className="px-4 sm:px-6 py-4 whitespace-nowrap">
                <span
                  className={clsx(
                    'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                    task.completed
                      ? 'bg-green-100 text-green-800 bg-green-500/20 text-green-200'
                      : 'bg-gray-100 text-gray-800 bg-slate-500/20 text-slate-200'
                  )}
                >
                  {task.completed ? 'Completed' : 'Pending'}
                </span>
              </td>
              <td className="hidden md:table-cell px-4 sm:px-6 py-4 whitespace-nowrap text-theme-secondary">
                {task.due_date ? formatDueDate(task.due_date) : '—'}
              </td>
              <td className="hidden lg:table-cell px-4 sm:px-6 py-4 whitespace-nowrap text-theme-secondary text-sm">
                {task.created_at ? new Date(task.created_at).toLocaleDateString() : '—'}
              </td>
              <td className="px-4 sm:px-6 py-4 whitespace-nowrap text-right text-sm font-medium min-w-[240px]">
                <div className="flex justify-end gap-2 flex-nowrap">
                <Button
                  variant="secondary"
                  onClick={() => onComplete(task)}
                  className="px-3 py-1 text-sm"
                >
                  {task.completed ? 'Mark Incomplete' : 'Complete'}
                </Button>
                <Button
                  variant="ghost"
                  onClick={() => onEdit(task)}
                  className="px-3 py-1 text-sm"
                >
                  Edit
                </Button>
                <Button
                  variant="ghost"
                  onClick={() => onDelete(task)}
                  className="px-3 py-1 text-sm text-red-400 hover:text-red-300"
                >
                  Delete
                </Button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}