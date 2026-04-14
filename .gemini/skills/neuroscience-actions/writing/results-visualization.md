# Neuroscience Writing: Publication Visualization (The Madelane Aesthetic)

Standards for generating high-resolution figures that meet journal requirements (SVG/PNG).

## 1. Aesthetic Consistency
- **Theme**: "Madelane Golden Dark" (Black background for presentations, White for publications).
- **Primary Color**: Vanderbilt Gold (`#CFB87C`) for data highlights.
- **Accents**: Cyan (`#00FFFF`) for trend lines and linear fits. White for trial-by-trial spectral peaks.

## 2. Layout & Composition
- **GridSpec**: Use vertically-stacked layouts for multi-panel temporal/spectral maps.
- **Subplots**: Row heights should reflect data importance (e.g., 6:6:3 ratio for PSDs and Stats Tables).
- **Heatmaps**: Use desaturated `hot` or `magma` colormaps. Set `vmax` (e.g., 1.5) to prevent color clipping while maintaining visibility of low-power regions.

## 3. Annotations
- **Units**: Always include units in axes labels (e.g., "Frequency (Hz)", "Trials", "Relative Power").
- **Markers**: Mark stimulus onsets and omissions with thin dashed white lines.
- **Statistics**: Embed key metrics (R², Slope, p-val) directly in the sub-panel title or adjacent table.
