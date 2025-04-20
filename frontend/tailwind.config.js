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
    },
  },
  plugins: [],
}