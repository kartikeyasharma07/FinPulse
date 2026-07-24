/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        surface: {
          light: '#F7F8FA',
          dark: '#0B0F14',
        },
        card: {
          light: '#FFFFFF',
          dark: '#131A22',
        },
        accent: {
          DEFAULT: '#0F9D8A',
          light: '#12B39D',
        },
        gain: '#16A34A',
        loss: '#DC2626',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
    },
  },
  plugins: [],
}

