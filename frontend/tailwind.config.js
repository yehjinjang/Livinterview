const colors = require('tailwindcss/colors')

module.exports = {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        zipup: {
          600: '#433CFF',
          700: '#2f2fcc',
          white: '#ffffff',
        },
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out', 
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
}
