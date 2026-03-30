import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./src/**/*.{ts,tsx}'],
  darkMode: ['class', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        primary: { DEFAULT: '#6366F1', light: '#818CF8', dark: '#4F46E5' },
        success: { DEFAULT: '#10B981', light: '#34D399', dark: '#059669' },
        warning: { DEFAULT: '#F59E0B', light: '#FBBF24', dark: '#D97706' },
        danger: { DEFAULT: '#EF4444', light: '#F87171', dark: '#DC2626' },
        base: 'var(--bg-base)',
        card: 'var(--bg-card)',
        surface: 'var(--bg-surface)',
      },
      boxShadow: {
        'glow-primary': '0 0 20px rgba(99, 102, 241, 0.3)',
        'glow-success': '0 0 20px rgba(16, 185, 129, 0.3)',
        'glow-danger': '0 0 20px rgba(239, 68, 68, 0.3)',
      },
    },
  },
  plugins: [],
};

export default config;

