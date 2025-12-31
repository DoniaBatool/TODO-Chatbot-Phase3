'use client';

import React from 'react';
import clsx from 'clsx';

type Props = {
  children: React.ReactNode;
  className?: string;
};

export function Card({ children, className }: Props) {
  return (
    <div className={clsx('rounded-lg border border-slate-800 bg-[#101631] p-6 shadow-lg', className)}>
      {children}
    </div>
  );
}
