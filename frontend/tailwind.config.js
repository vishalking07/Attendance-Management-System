/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        heading: ['"Outfit"', '"Plus Jakarta Sans"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
      },
      colors: {
        // Exact color theory matching reference
        canvas: '#ECE6F8',       // Soft warm lavender outer canvas
        surface: '#FFFFFF',      // Pure crisp white card surface
        panel: '#FAF8FE',        // Very soft tinted panel
        brand: {
          light: '#A78BFA',
          DEFAULT: '#7C3AED',    // Vibrant violet
          dark: '#6D28D9',       // Deep rich purple
          deep: '#5B21B6',
          gradientStart: '#8B5CF6',
          gradientEnd: '#6D28D9',
        },
        ink: {
          heading: '#0F172A',    // Highest contrast dark slate for headings
          body: '#334155',       // High readability slate-700 body text
          muted: '#64748B',      // Balanced secondary slate-500
          subtle: '#94A3B8',
        }
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.5rem',
        '4xl': '2rem',
        '5xl': '2.5rem',
      },
      boxShadow: {
        'card-subtle': '0 4px 20px -2px rgba(124, 58, 237, 0.05), 0 2px 6px -1px rgba(0, 0, 0, 0.02)',
        'card-hover': '0 12px 28px -4px rgba(124, 58, 237, 0.12), 0 4px 10px -2px rgba(0, 0, 0, 0.04)',
        'highlight-active': '0 0 0 2px #7C3AED, 0 10px 25px -4px rgba(124, 58, 237, 0.18)',
        'banner': '0 14px 30px -5px rgba(109, 40, 217, 0.3)',
        'sidebar': '0 16px 35px -8px rgba(109, 40, 217, 0.32)',
      }
    },
  },
  plugins: [],
}
