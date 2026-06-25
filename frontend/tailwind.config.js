/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './components/**/*.{vue,js,ts}',
    './layouts/**/*.vue',
    './pages/**/*.vue',
    './plugins/**/*.{js,ts}',
    './app.vue',
    './error.vue'
  ],
  theme: {
    extend: {
      colors: {
        "surface-container-highest": "#333535",
        "secondary-container": "#7701d0",
        "on-surface": "#e2e2e2",
        "primary-fixed": "#ffdad5",
        "tertiary": "#c8c6c5",
        "on-error-container": "#ffdad6",
        "surface": "#121414",
        "glass-stroke": "rgba(255, 255, 255, 0.1)",
        "surface-container-lowest": "#0d0f0f",
        "surface-container-low": "#1a1c1c",
        "inverse-primary": "#c0000c",
        "primary-fixed-dim": "#ffb4aa",
        "error-container": "#93000a",
        "on-secondary-fixed-variant": "#6700b5",
        "secondary-fixed": "#efdbff",
        "on-secondary-container": "#dcb7ff",
        "background": "#121414",
        "secondary": "#dcb8ff",
        "on-tertiary-container": "#fbf8f8",
        "on-secondary-fixed": "#2c0051",
        "tertiary-fixed-dim": "#c8c6c5",
        "surface-variant": "#333535",
        "primary-container": "#e50914",
        "tertiary-fixed": "#e5e2e1",
        "surface-container": "#1e2020",
        "outline": "#af8782",
        "on-primary-container": "#ffffff",
        "on-tertiary-fixed": "#1b1b1c",
        "on-primary": "#690003",
        "inverse-on-surface": "#2f3131",
        "inverse-surface": "#e2e2e2",
        "surface-dim": "#121414",
        "on-error": "#690005",
        "error": "#ffb4ab",
        "on-primary-fixed": "#410001",
        "tertiary-container": "#737272",
        "on-background": "#e2e2e2",
        "surface-container-high": "#282a2a",
        "on-tertiary-fixed-variant": "#474746",
        "secondary-fixed-dim": "#dcb8ff",
        "primary": "#ffb4aa",
        "on-primary-fixed-variant": "#930007",
        "on-tertiary": "#303030",
        "surface-tint": "#ffb4aa",
        "on-surface-variant": "#b3b3b3",
        "surface-bright": "#383939",
        "ai-accent": "#8a2be2",
        "on-secondary": "#480081",
        "outline-variant": "#5e3f3b"
      },
      borderRadius: {
        "DEFAULT": "0.25rem",
        "lg": "0.5rem",
        "xl": "0.75rem",
        "full": "9999px"
      },
      spacing: {
        "margin-desktop": "48px",
        "gutter": "24px",
        "margin-mobile": "16px",
        "section-padding": "96px",
        "unit": "8px",
        "container-max": "1280px"
      },
      fontFamily: {
        "body-lg": ["Inter", "sans-serif"],
        "body-md": ["Inter", "sans-serif"],
        "headline-lg": ["Montserrat", "sans-serif"],
        "headline-md": ["Montserrat", "sans-serif"],
        "label-md": ["Inter", "sans-serif"],
        "label-sm": ["Inter", "sans-serif"],
        "headline-xl": ["Montserrat", "sans-serif"],
        "headline-xl-mobile": ["Montserrat", "sans-serif"]
      },
      fontSize: {
        "body-lg": ["18px", {"lineHeight": "28px", "fontWeight": "400"}],
        "body-md": ["16px", {"lineHeight": "24px", "fontWeight": "400"}],
        "headline-lg": ["32px", {"lineHeight": "40px", "letterSpacing": "-0.01em", "fontWeight": "700"}],
        "headline-md": ["24px", {"lineHeight": "32px", "fontWeight": "600"}],
        "label-md": ["14px", {"lineHeight": "20px", "letterSpacing": "0.05em", "fontWeight": "600"}],
        "label-sm": ["12px", {"lineHeight": "16px", "fontWeight": "500"}],
        "headline-xl": ["48px", {"lineHeight": "56px", "letterSpacing": "-0.02em", "fontWeight": "700"}],
        "headline-xl-mobile": ["36px", {"lineHeight": "44px", "fontWeight": "700"}]
      }
    }
  },
  plugins: [
    require('@tailwindcss/forms')
  ]
}
