---
name: frontend-dashboard
description: Management suite for the React-based Omission Dashboard, handling figure hosting, scrolling, and layout controls.
---
# skill: frontend-dashboard

## When to Use
Use this skill when managing the project's visual portal. Specifically for:
- Starting the local dev server (`npm run dev`).
- Debugging figure visibility and iframe scaling issues.
- Adding new analytical categories (e.g., Phase 5) to the UI.
- Verifying that figures are not "force-fitted" and allow proper panning/zooming.

## What is Input
- **Source Files**: HTML figures and README.md files in `outputs/oglo-8figs/`.
- **Config**: Dashboard routing and manifest files.
- **State**: The local port status (default: `5173`).

## What is Output
- **Live URL**: `http://localhost:5173/`.
- **UI State**: An interactive gallery where users can maximize/minimize individual figures.
- **Console Logs**: Feedback on file loading or rendering errors.

## Algorithm / Methodology
1. **Gallery Logic**: Replaces static iframes with a dynamic grid where clicking a figure expands it into a "Gallery View."
2. **Scroll Enforcement**: Applies `overflow-y: auto` to all figure containers to ensure markdown descriptions are readable.
3. **Responsive Scaling**: Sets a minimum height of 600px for expanded views to ensure visual clarity.
4. **Dev Server Orchestration**: Uses `npm run dev` in a background terminal to maintain persistent access.
5. **Asset Discovery**: Automatically crawls the `outputs/` directory to populate the dashboard sidebar.

## Placeholder Example
```bash
# 1. Navigate to dashboard root
cd D:/drive/omission/dashboard

# 2. Start the dev server
npm run dev

# 3. Verify on browser (Localhost 5173)
```

## Relevant Context / Files
- [design-neuro-omission-branding-theme](file:///D:/drive/omission/.gemini/skills/design-neuro-omission-branding-theme/skill.md) — For UI styling.
- [dashboard/src/App.jsx](file:///D:/drive/omission/dashboard/src/App.jsx) — The main dashboard logic.
