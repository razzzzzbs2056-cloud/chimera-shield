/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          'Inter',
          'ui-sans-serif',
          'system-ui',
          '-apple-system',
          'Segoe UI',
          'Roboto',
          'Helvetica Neue',
          'Arial',
          'sans-serif',
        ],
      },
      colors: {
        ink: {
          950: '#06070d',
          900: '#0a0c16',
          800: '#10121f',
          700: '#171a2b',
          600: '#1f2238',
        },
        brand: {
          DEFAULT: '#8b5cf6',
          soft: '#a78bfa',
          deep: '#6d28d9',
        },
        accent: '#22d3ee',
      },
      boxShadow: {
        glow: '0 0 0 1px rgba(139,92,246,0.25), 0 20px 60px -15px rgba(139,92,246,0.45)',
        premium: '0 30px 80px -30px rgba(0,0,0,0.8)',
      },
      backgroundImage: {
        'radial-fade':
          'radial-gradient(60% 60% at 50% 0%, rgba(139,92,246,0.18) 0%, rgba(6,7,13,0) 70%)',
        'brand-gradient':
          'linear-gradient(135deg, #8b5cf6 0%, #6d28d9 45%, #22d3ee 130%)',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '0% 50%' },
          '100%': { backgroundPosition: '200% 50%' },
        },
      },
      animation: {
        float: 'float 6s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
