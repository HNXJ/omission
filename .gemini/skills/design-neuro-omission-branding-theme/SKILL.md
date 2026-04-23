---
name: design-neuro-omission-branding-theme
---
# design-neuro-omission-branding-theme

## Purpose
Visual identity specification: Madelane Golden Dark palette, typography, glassmorphism, transition rules for dashboard and figures.

## Color Tokens
| Token | Hex | Usage |
|-------|-----|-------|
| `--brand-gold` | `#CFB87C` | Primary accent / Stimulus / FF |
| `--brand-purple` | `#9400D3` | Secondary accent / Omission / FB |
| `--brand-dark` | `#1A1A1A` | Main background |
| `--brand-text` | `#E0E0E0` | Primary text |
| `--brand-pink` | `#FF1493` | Omission window shading (α=0.2) |

## Typography
- Font: `Inter` or `Roboto` (Google Fonts)
- All hover transitions: `0.3s ease-in-out`

## Example
```css
:root {
  --madelane-gold: #CFB87C;
  --madelane-dark: #1A1A1A;
}
.btn-madelane {
  background-color: var(--madelane-gold);
  color: var(--madelane-dark);
  border-radius: 8px;
}
```

## Files
- [index.css](file:///D:/drive/omission/dashboard/index.css) — Live theme implementation
