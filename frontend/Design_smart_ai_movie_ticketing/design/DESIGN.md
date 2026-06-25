---
name: CineAI Cyber-Premium
colors:
  surface: '#121414'
  surface-dim: '#121414'
  surface-bright: '#383939'
  surface-container-lowest: '#0d0f0f'
  surface-container-low: '#1a1c1c'
  surface-container: '#1e2020'
  surface-container-high: '#282a2a'
  surface-container-highest: '#333535'
  on-surface: '#e3e2e2'
  on-surface-variant: '#b3b3b3'
  inverse-surface: '#e2e2e2'
  inverse-on-surface: '#2f3131'
  outline: '#af8782'
  outline-variant: '#5e3f3b'
  surface-tint: '#ffb4aa'
  primary: '#ffb4aa'
  on-primary: '#690003'
  primary-container: '#e50914'
  on-primary-container: '#ffffff'
  inverse-primary: '#c0000c'
  secondary: '#dcb8ff'
  on-secondary: '#480081'
  secondary-container: '#7701d0'
  on-secondary-container: '#dcb7ff'
  tertiary: '#c8c6c5'
  on-tertiary: '#303030'
  tertiary-container: '#737272'
  on-tertiary-container: '#fbf8f8'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffdad5'
  primary-fixed-dim: '#ffb4aa'
  on-primary-fixed: '#410001'
  on-primary-fixed-variant: '#930007'
  secondary-fixed: '#efdbff'
  secondary-fixed-dim: '#dcb8ff'
  on-secondary-fixed: '#2c0051'
  on-secondary-fixed-variant: '#6700b5'
  tertiary-fixed: '#e5e2e1'
  tertiary-fixed-dim: '#c8c6c5'
  on-tertiary-fixed: '#1b1b1c'
  on-tertiary-fixed-variant: '#474746'
  background: '#121414'
  on-background: '#e2e2e2'
  surface-variant: '#333535'
  ai-accent: '#8a2be2'
  glass-stroke: rgba(255, 255, 255, 0.1)
typography:
  headline-xl:
    fontFamily: Montserrat
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-xl-mobile:
    fontFamily: Montserrat
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
  headline-lg:
    fontFamily: Montserrat
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Montserrat
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.05em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 8px
  gutter: 24px
  margin-desktop: 48px
  margin-mobile: 16px
  container-max: 1280px
  section-padding: 96px
---

## Brand & Style
CineAI is a high-end, AI-driven cinema platform that evokes a sense of futuristic immersion and premium exclusivity. The brand personality is sophisticated, technologically advanced, and cinematic. 

The design style is **Glassmorphism** layered over a **High-Contrast Dark** foundation. It utilizes deep blacks, vibrant red accents, and purple neural-network-inspired glows to create a "cyberpunk" aesthetic that feels both dark and energetic. Visual interest is driven by semi-transparent surfaces, backdrop blurs (12px to 32px), and animated gradient borders that signify "AI intelligence."

## Colors
The palette is rooted in a "Pure Dark" base (`#121414`) to make cinematic content and red accents pop. 

- **Primary Red (`#e50914`):** Used for critical actions, branding, and status indicators. It is frequently paired with an outer glow (red-glow) to simulate neon lighting.
- **Secondary AI Purple (`#8a2be2`):** Reserved for AI-specific features, gradient borders, and decorative pulses, representing the "intelligence" layer.
- **Surface Strategy:** Uses tiered dark grays. The background is the darkest, while containers use slightly lighter tones or glass-morphic transparencies to create depth.
- **Gradients:** A core visual signature is the transition from `primary-container` to `secondary` purple, used in text clips and borders.

## Typography
The system uses **Montserrat** for headlines to convey boldness and cinematic impact. It is heavy, geometric, and works best with tight letter-spacing at large sizes. 

**Inter** handles all functional text, body copy, and UI labels. It provides high legibility against dark backgrounds. 

- **Hero Typography:** Employs gradient text masks and outer glows on keywords (like "AI") to emphasize brand pillars.
- **Labels:** Use uppercase styling with increased letter spacing for small metadata tags (IMAX, 4DX).

## Layout & Spacing
The layout follows a **Fixed Grid** philosophy for desktop, centered within a `1280px` max-width container. 

- **Vertical Rhythm:** Sections are aggressively separated by `96px` (12 units) to maintain a premium, airy feel despite the dark theme.
- **Grid:** A 12-column logic is used for features, while movie posters utilize a flexible 4-column responsive grid (collapsing to 2 columns on mobile).
- **Safe Areas:** Horizontal margins scale from `48px` on desktop to `16px` on mobile to ensure content remains readable on small devices.

## Elevation & Depth
Elevation is achieved through **translucency and light-casting** rather than traditional shadows.

- **Glass Panels:** Use a `background: rgba(31, 31, 31, 0.6)` with a `12px` backdrop blur. Borders are `1px solid white/10`.
- **Luminous Glows:** Primary buttons and "AI" elements use `box-shadow: 0 0 20px -5px rgba(229, 9, 20, 0.3)`. This "casts light" onto the surface below, simulating a physical neon source.
- **Z-Axis Hierarchy:** 
    - Level 0: Pure Black Background.
    - Level 1: Surface Containers (Dark Gray).
    - Level 2: Glass Panels (Semi-transparent).
    - Level 3: Overlays/Navigation (Heavy blur, 32px).

## Shapes
The shape language is **Rounded**, balancing the technical sharpness of the theme with approachable curves.

- **Standard Elements:** Cards and buttons use a `0.75rem` (12px) radius.
- **Pill Shapes:** Used for status tags, metadata, and "AI Choice" badges to distinguish them from functional buttons.
- **Interactive States:** Hovering over movie cards triggers a slight scale increase (`1.05x`) and an elevation shift, emphasizing the tactile nature of the UI.

## Components

### Buttons
- **Primary:** Solid `primary-container` background, white text, 12px radius. Features a `red-glow` hover effect and internal white-tint overlay on hover.
- **Secondary/Ghost:** Transparent background with a `1px white/20` border. Transitions to `white/10` on hover.
- **AI-Enhanced:** Features a moving 2px gradient border (`primary` to `secondary`) and an icon prefix.

### Movie Cards
- **Structure:** Aspect ratio `2:3`. Uses a bottom-aligned gradient fade (`gradient-fade-bottom`) to ensure title legibility. 
- **Hover Behavior:** Buttons and details are hidden by default and slide up from the bottom on hover with a `300ms` duration.

### AI Chatbot Interface
- **Messaging:** User bubbles are dark gray (`#1F1F1F`) with a sharp top-right corner. AI bubbles use a `primary-container/10` tint with a subtle red border.
- **Input:** Pill-shaped, semi-transparent field with glass-morphism and a dedicated circular "Send" button.

### Navigation
- **Top Bar:** Fixed, 80px height, using extreme backdrop blur (32px). Active links use a bottom-border in `primary-container` with a bold weight.