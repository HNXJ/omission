---
name: frontend-dashboard
---
# frontend-dashboard

## Purpose
React-based Omission Dashboard: figure hosting, iframe scaling, gallery view, and asset discovery from `outputs/`.

## Input
| Name | Type | Description |
|------|------|-------------|
| figure_dir | str | `outputs/oglo-8figs/` HTML figures + READMEs |
| port | int | Dev server port (default: 5173) |

## Output
| Name | Type | Description |
|------|------|-------------|
| live_url | str | `http://localhost:5173/` |
| ui_state | str | Interactive gallery with maximize/minimize |

## Commands
```bash
cd D:/drive/omission/dashboard
npm run dev
```

## Files
- [App.jsx](file:///D:/drive/omission/dashboard/src/App.jsx) — Main dashboard logic
