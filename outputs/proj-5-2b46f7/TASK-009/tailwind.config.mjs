/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // 科幻风格配色
        scifi: {
          bg: '#0a0a0f',
          card: '#12121a',
          primary: '#00d4ff',
          secondary: '#7000ff',
          accent: '#ff006e',
          text: '#e0e0e0',
          muted: '#6b7280',
          border: '#1f2937',
        },
        // 霓虹颜色
        neon: {
          cyan: '#00d4ff',
          purple: '#7000ff',
          pink: '#ff006e',
          green: '#00ff88',
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
        'float': 'float 3s ease-in-out infinite',
        'shimmer': 'shimmer 2s linear infinite',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px #00d4ff, 0 0 10px #00d4ff' },
          '100%': { boxShadow: '0 0 20px #00d4ff, 0 0 30px #00d4ff' },
        },
        pulseGlow: {
          '0%, 100%': {
            boxShadow: '0 0 5px rgba(0, 212, 255, 0.5), 0 0 10px rgba(0, 212, 255, 0.3)',
          },
          '50%': {
            boxShadow: '0 0 10px rgba(0, 212, 255, 0.6), 0 0 20px rgba(0, 212, 255, 0.4)',
          },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
};