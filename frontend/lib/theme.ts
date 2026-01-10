/**
 * Comprehensive Theme System for TaskMate AI
 * Supports both dark and light modes with consistent colors across all components
 */

export const theme = {
  dark: {
    // Backgrounds
    bg: {
      primary: '#0f172a',      // Main background
      secondary: '#1e293b',    // Card/section background
      tertiary: '#334155',     // Elevated elements
      gradient: 'radial-gradient(circle at 20% 20%, #1e293b, #0f172a 50%)',
    },
    // Text colors
    text: {
      primary: '#f1f5f9',      // Main text
      secondary: '#cbd5e1',    // Secondary text
      tertiary: '#94a3b8',     // Muted text
      inverse: '#0f172a',      // Text on light backgrounds
    },
    // Border colors
    border: {
      primary: '#334155',
      secondary: '#475569',
      focus: '#3b82f6',
    },
    // Input colors
    input: {
      bg: '#1e293b',
      border: '#334155',
      text: '#f1f5f9',
      placeholder: '#64748b',
      focus: '#3b82f6',
    },
    // Button colors
    button: {
      primary: {
        bg: 'linear-gradient(to right, #3b82f6, #8b5cf6)',
        text: '#ffffff',
        hover: 'linear-gradient(to right, #2563eb, #7c3aed)',
      },
      secondary: {
        bg: '#334155',
        text: '#f1f5f9',
        hover: '#475569',
      },
    },
  },
  light: {
    // Backgrounds
    bg: {
      primary: '#ffffff',      // Main background
      secondary: '#f8fafc',    // Card/section background
      tertiary: '#e2e8f0',     // Elevated elements
      gradient: 'radial-gradient(circle at 20% 20%, #f1f5f9, #ffffff 50%)',
    },
    // Text colors
    text: {
      primary: '#0f172a',      // Main text
      secondary: '#475569',    // Secondary text
      tertiary: '#64748b',     // Muted text
      inverse: '#ffffff',      // Text on dark backgrounds
    },
    // Border colors
    border: {
      primary: '#e2e8f0',
      secondary: '#cbd5e1',
      focus: '#3b82f6',
    },
    // Input colors
    input: {
      bg: '#ffffff',
      border: '#e2e8f0',
      text: '#0f172a',
      placeholder: '#94a3b8',
      focus: '#3b82f6',
    },
    // Button colors
    button: {
      primary: {
        bg: 'linear-gradient(to right, #3b82f6, #8b5cf6)',
        text: '#ffffff',
        hover: 'linear-gradient(to right, #2563eb, #7c3aed)',
      },
      secondary: {
        bg: '#f1f5f9',
        text: '#0f172a',
        hover: '#e2e8f0',
      },
    },
  },
};

export type ThemeMode = 'dark' | 'light';
