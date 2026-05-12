/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        neon: {
          magenta: "#FF006E",
          green: "#00FF00",
          cyan: "#00FFFF",
        },
        dark: {
          bg: "#0a0e27",
          card: "#1a1f3a",
        },
      },
      fontFamily: {
        arcade: ["Arial Black", "Impact", "sans-serif"],
      },
      boxShadow: {
        "neon-magenta": "0 0 20px rgba(255, 0, 110, 0.8)",
        "neon-green": "0 0 20px rgba(0, 255, 0, 0.8)",
        "neon-cyan": "0 0 20px rgba(0, 255, 255, 0.8)",
      },
    },
  },
  plugins: [],
};
