module.exports = {
    content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
    safelist: [
      'text-zipup-600', 
      'hover:bg-zipup-700', 
    ],
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
  