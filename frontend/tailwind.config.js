/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
      },
      colors: {
        auth: {
          bg: '#0B0F19',
          card: '#111827',
          input: '#151D2B',
          border: '#263244',
          primary: '#6366F1',
          text: '#F8FAFC',
          muted: '#94A3B8',
          success: '#22C55E',
          error: '#EF4444',
        },
        brand: {
          50: '#f0f7ff',
          100: '#e0effe',
          500: '#2563eb',
          600: '#1d4ed8',
          700: '#1e40af',
          900: '#1e3a8a',
        }
      }
    },
  },
  plugins: [],
}
