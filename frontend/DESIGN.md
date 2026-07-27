---
name: Cinematic AI
colors:
  surface: '#121414'
  surface-dim: '#121414'
  surface-bright: '#38393a'
  surface-container-lowest: '#0d0e0f'
  surface-container-low: '#1a1c1c'
  surface-container: '#1e2020'
  surface-container-high: '#292a2a'
  surface-container-highest: '#343535'
  on-surface: '#e3e2e2'
  on-surface-variant: '#e9bcb6'
  inverse-surface: '#e3e2e2'
  inverse-on-surface: '#2f3131'
  outline: '#af8782'
  outline-variant: '#5e3f3b'
  surface-tint: '#ffb4aa'
  primary: '#ffb4aa'
  on-primary: '#690003'
  primary-container: '#e50914'
  on-primary-container: '#fff7f6'
  inverse-primary: '#c0000c'
  secondary: '#c8c6c5'
  on-secondary: '#313030'
  secondary-container: '#4a4949'
  on-secondary-container: '#bab8b7'
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
  secondary-fixed: '#e5e2e1'
  secondary-fixed-dim: '#c8c6c5'
  on-secondary-fixed: '#1c1b1b'
  on-secondary-fixed-variant: '#474646'
  tertiary-fixed: '#e5e2e1'
  tertiary-fixed-dim: '#c8c6c5'
  on-tertiary-fixed: '#1b1b1c'
  on-tertiary-fixed-variant: '#474746'
  background: '#121414'
  on-background: '#e3e2e2'
  surface-variant: '#343535'
typography:
  headline-xl:
    fontFamily: Montserrat
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Montserrat
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Montserrat
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
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
  container-max: 1280px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 48px
---

## Brand & Style

The design system is engineered to evoke the high-stakes, immersive atmosphere of a premium cinema lobby. The brand personality is bold, sophisticated, and technologically advanced, bridging the gap between traditional film aesthetics and future-forward AI discovery. 

The visual style employs a **Dark Mode Cinematic** approach, utilizing high-contrast accents against abyssal backgrounds. It leverages **Glassmorphism** and **Subtle Glows** to simulate the effect of neon theater signage and back-lit digital kiosks. Surfaces feel like polished obsidian—glossy yet functional—providing a luxury stage for vibrant film artwork.

## Colors

This design system is anchored in a true-black environment to maximize the "pop" of movie posters and red interactive elements. 

- **Primary (Cinematic Red):** Used exclusively for high-priority calls to action, active states, and critical information. It should be treated as a light source.
- **Backgrounds:** Pure black (#000000) is the base canvas. Dark Gray (#121212) is used for secondary sections to provide subtle structure.
- **Surfaces:** Darker Slate (#1F1F1F) acts as the foundation for cards and inputs, providing enough contrast against the background to define depth without needing heavy borders.
- **Typography:** Pure White for headlines to ensure maximum readability; Light Gray for secondary metadata to maintain visual hierarchy.

## Typography

The typographic system balances the editorial impact of **Montserrat** with the functional precision of **Inter**.

- **Headlines:** Set in Montserrat with tight letter-spacing to mimic movie title treatments. Use Bold (700) for primary headers to command attention.
- **Body:** Inter provides neutral, highly legible reading for synopses and showtimes.
- **Labels:** Small caps or uppercase transformations are encouraged for category labels (e.g., GENRE, RATING) to create a structured, "data-rich" look familiar to AI interfaces.

## Layout & Spacing

The layout follows a 12-column fluid grid on desktop, transitioning to a single-column stacked view on mobile. 

- **Breathing Room:** Use generous vertical padding (64px+) between sections to maintain a premium, cinematic feel.
- **Aspect Ratios:** Movie posters should strictly follow a 2:3 ratio, while hero banners use a wide 21:9 or 16:9 ratio to mimic theatrical screens.
- **AI Feed:** Discovery feeds should use an asymmetrical masonry or staggered grid to suggest dynamic, AI-generated curation rather than a static list.

## Elevation & Depth

Depth is communicated through **Glassmorphism** and **Luminescence** rather than traditional drop shadows.

- **Level 1 (Base):** Pure black background.
- **Level 2 (Cards):** #1F1F1F with a subtle 1px inner border (white at 10% opacity) to simulate a glass edge.
- **Level 3 (Modals/Overlays):** Semi-transparent background blur (32px) with a dark tint, allowing the movie artwork underneath to bleed through.
- **Luminescence:** Interactive elements use a "Red Glow" effect—a soft, primary-colored outer shadow (blur: 20px, spread: -5px, opacity: 0.3) to suggest the element is emitting light.

## Shapes

The shape language is "Soft-Modern." All primary containers, buttons, and posters utilize a **12px to 16px corner radius**. This softens the high-contrast color palette, making the interface feel approachable and high-end rather than aggressive or industrial. 

- **Posters:** 12px radius.
- **Buttons:** 12px radius for standard, 32px (pill) for secondary tags.
- **Inputs:** 12px radius.

## Components

### Buttons
- **Primary:** Cinematic Red background, white text. On hover: Scale 1.05x and add a red glow effect.
- **Secondary:** Transparent with a 1.5px white border. On hover: Background becomes white at 10% opacity.

### Cards (Movie/Showtime)
- Surfaces should have a glossy finish. Use a subtle gradient transition from bottom (black) to top (transparent) over movie posters to ensure text overlay readability.

### Chips & Tags
- Used for genres (e.g., "Sci-Fi", "IMAX"). Pill-shaped with a Darker Slate (#1F1F1F) background and Light Gray text.

### Inputs
- Background: #121212. Border: 1px #1F1F1F. On focus: Border changes to Cinematic Red with a faint red glow.

### AI Recommendations
- Special "AI Choice" cards should feature a subtle, animated gradient border using a mix of Cinematic Red and a deep violet to distinguish them from standard listings.

### Lists
- For showtimes, use a horizontal scrolling row of "Time Chips." Active time chips should be Cinematic Red; inactive chips should be outlined.

