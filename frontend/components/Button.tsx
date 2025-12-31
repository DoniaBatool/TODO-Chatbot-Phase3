'use client';

import clsx from 'clsx';
import React from 'react';

type Props = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'secondary' | 'ghost';
};

export function Button({ variant = 'primary', className, children, ...props }: Props) {
  const styles = clsx(
    'rounded-md px-4 py-2 text-sm font-medium transition-colors disabled:opacity-60 disabled:cursor-not-allowed',
    variant === 'primary' && 'bg-blue-600 text-white hover:bg-blue-500',
    variant === 'secondary' && 'bg-slate-700 text-slate-100 hover:bg-slate-600',
    variant === 'ghost' && 'bg-transparent text-slate-200 hover:bg-slate-800',
    className,
  );
  return (
    <button className={styles} {...props}>
      {children}
    </button>
  );
}
