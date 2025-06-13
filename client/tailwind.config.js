/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        primary: '#1e40af',
        secondary: '#1e293b',
        accent: '#22d3ee',
        success: '#16a34a',
        warning: '#eab308',
        danger: '#dc2626',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
      },
      minHeight: {
        screen: '100vh',
      },
    },
  },
  plugins: [],
}
