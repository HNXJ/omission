---
name: design-neuro-omission-branding-theme
description: Specification for the project's visual identity, typography, and color systems (Madelane Golden Dark).
---
# skill: design-neuro-omission-branding-theme

## When to Use
Use this skill when designing any user-facing component, including:
- Dashboard UI elements (buttons, sidebars, cards).
- Figure trace color assignments.
- PDF/Markdown report styling.
- Establishing the "Visual Single Source of Truth" for multi-agent collaboration.

## What is Input
- **CSS Variables**: Global tokens for colors and spacing.
- **Brand Assets**: Logos or SVG icons.
- **Palette Definitions**: Hex codes for primary and secondary accents.

## What is Output
- **Styled Components**: UI elements that adhere to the Madelane aesthetic.
- **Consistent Visuals**: Figures that are immediately recognizable as belonging to the Omission project.
- **Themed Documentation**: Markdown files with stylized headers and alerts.

## Algorithm / Methodology
1. **Color Tokenization**: Defines a core set of semantic variables:
   - `--brand-gold`: `#CFB87C` (Primary Accent / Stimulus).
   - `--brand-purple`: `#9400D3` (Secondary Accent / Omission).
   - `--brand-dark`: `#1A1A1A` (Main Background).
   - `--brand-text`: `#E0E0E0` (Primary Text).
2. **Typography Enforcement**: Standardizes on 'Inter' or 'Roboto' for high readability in dense data environments.
3. **Glassmorphism**: Applies `backdrop-filter: blur(10px)` to dashboard overlays to create a "Premium" feel.
4. **Transition Logic**: Mandates `0.3s ease-in-out` for all hover states and component appearances.
5. **Aesthetic Motivation**: The "Madelane Golden Dark" palette is designed to evoke high-precision engineering and "Vanderbilt Prestige."

## Placeholder Example
```css
/* 1. Global CSS Variables */
:root {
  --madelane-gold: #CFB87C;
  --madelane-dark: #1A1A1A;
}

/* 2. Primary Button Component */
.btn-madelane {
  background-color: var(--madelane-gold);
  color: var(--madelane-dark);
  font-weight: 600;
  border-radius: 8px;
}
```

## Relevant Context / Files
- [design-neuro-omission-advanced-plotting](file:///D:/drive/omission/.gemini/skills/design-neuro-omission-advanced-plotting/skill.md) — For figure implementation.
- [dashboard/index.css](file:///D:/drive/omission/dashboard/index.css) — The live implementation of the theme.
