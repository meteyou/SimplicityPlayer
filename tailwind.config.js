/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./module/templates/*.html", "./assets/js/*.js"],
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

