/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./*.html"
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          950: '#030305',
          900: '#08080c',
          800: '#0f0f15',
          700: '#171721',
          600: '#21212e',
          500: '#2e2e3f',
        },
        primary: {
          500: '#6366f1',
          600: '#4f46e5',
          400: '#818cf8',
        },
        cosmic: {
          purple: '#8b5cf6',
          teal: '#14b8a6',
          pink: '#ec4899',
        }
      },
      fontFamily: {
        sans: ['Outfit', 'Inter', 'sans-serif'],
      },
      boxShadow: {
        glow: '0 0 15px rgba(99, 102, 241, 0.2)',
        'glow-purple': '0 0 20px rgba(139, 92, 246, 0.25)',
        'glow-teal': '0 0 20px rgba(20, 184, 166, 0.25)',
      }
    },
  },
  plugins: [],
}
