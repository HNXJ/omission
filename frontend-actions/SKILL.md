---
name: frontend-actions
description: Skill for publication-quality scientific plotting and managing neuroscience-focused web applications. Specializes in "Madelane Golden Dark" aesthetics and high-performance data dashboards.
---

# Frontend Actions Skill

This skill provides context and workflows for publication-quality scientific visualization and managing neuroscience-focused web applications.

## 1. Publication-Quality Plotting
Standards for generating figures for journals (e.g., PLOS ONE).

### Aesthetic Standards: "Madelane Golden Dark"
- **Primary Palette**: Vanderbilt Gold (`#CFB87C`) on Pure Black (`#000000`).
- **Trend Lines**: Use high-contrast **Cyan** dashed lines for linear fits.
- **Trial Peaks**: Use small **White** dots for trial-level spectral maxima.
- **Colormaps**: Prefer desaturated `hot` or `magma`. Use `vmax=1.5` to avoid clipping high-power peaks.

### Layout Logic: `matplotlib.gridspec`
For complex, multi-panel figures (e.g., PSD maps + Stats tables):
- **Proportions**: Use `height_ratios` to emphasize data (e.g., `[6, 6, 3]` for two maps and one table).
- **Consolidated Tables**: Use `ax.table` spanning the full figure width for statistical summaries.
- **Export**: Always save in **SVG** format for resolution-independent scaling.

## 2. Interactive Dashboards (Streamlit)
Building real-time analysis tools for biophysics and NWB data.

### Standard UI Components
- **Sidebar**: Simulation parameter control (`gAMPA`, `gGABAa`, `noise_amp`).
- **Main Panel**: Real-time raster plots and stimulus-aligned PSDs.
- **File Navigator**: Integrated local file system navigation for rapid NWB file selection.

## 3. Portfolio Management (hnxj.github.io)
Maintain the HNXJ portfolio by adding new projects and updating educational milestones.

### Common Workflows
- **Deployment**: Use `gh` (GitHub CLI) for all sync operations to `hnxj.github.io`.
- **Project Updates**: Ensure latest SVG figures from GSDR01/NWB analysis are featured.

## Key Resources
- **Portfolio**: `/Users/hamednejat/workspace/HNXJ/hnxj_gio`
- **Plotting Helpers**: `AAE.gsdr.analysis` (contains high-level plotting functions).
