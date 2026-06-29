/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        risk: {
          low: '#10b981',
          moderate: '#f59e0b',
          high: '#ef4444',
          veryhigh: '#dc2626',
          critical: '#7f1d1d',
        }
      }
    },
  },
  plugins: [],
}
