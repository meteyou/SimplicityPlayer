/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/*.html", "./assets/js/*.js"],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/aspect-ratio'),
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('daisyui')
  ],
}

