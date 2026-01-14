'use client';

import React from 'react';
import clsx from 'clsx';

type Props = {
  children: React.ReactNode;
  className?: string;
};

export function Card({ children, className }: Props) {
  return (
    <div
      className={clsx(
        'card-theme rounded-2xl p-4 sm:p-6 shadow-sm hover:shadow-md transition-all duration-300',
        className
      )}
    >
      {children}
    </div>
  );
}
