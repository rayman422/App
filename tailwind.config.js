/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        scripture: {
          50: '#fefdf8',
          100: '#fef7e0',
          200: '#feefc7',
          300: '#fde5a3',
          400: '#fbd776',
          500: '#f8c845',
          600: '#eab308',
          700: '#ca8a04',
          800: '#a16207',
          900: '#854d0e',
        }
      },
      fontFamily: {
        'scripture': ['Georgia', 'Times New Roman', 'serif'],
      }
    },
  },
  plugins: [],
}