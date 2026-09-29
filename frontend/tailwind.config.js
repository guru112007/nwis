/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          900: '#070A10',
          800: '#0B0F19',
          700: '#141B2D',
          600: '#1E293B',
          500: '#334155'
        },
        brand: {
          cyan: '#0EA5E9',
          amber: '#F59E0B',
          red: '#EF4444',
          green: '#10B981',
          purple: '#8B5CF6'
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif']
      }
    },
  },
  plugins: [],
}
