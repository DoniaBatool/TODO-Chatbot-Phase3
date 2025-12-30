'use client';

import React from 'react';
import clsx from 'clsx';

type Props = {
  variant?: 'error' | 'success' | 'info';
  children: React.ReactNode;
  className?: string;
};

export function Alert({ variant = 'info', children, className }: Props) {
  const styles = clsx(
    'rounded-md px-3 py-2 text-sm',
    variant === 'error' && 'bg-red-500/10 text-red-200 border border-red-500/30',
    variant === 'success' && 'bg-green-500/10 text-green-200 border border-green-500/30',
    variant === 'info' && 'bg-slate-700/50 text-slate-100 border border-slate-600/60',
    className,
  );
  return <div className={styles}>{children}</div>;
}
