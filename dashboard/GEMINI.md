# Omission Terminal
Professional React/Vite command center (Bloomberg for Neuro) for high-density visualization and analytical interrogation.

## Terminal Workflow
- **Launch Command Center**:
  1. Navigate to `D:\drive\omission\dashboard`.
  2. Run `npm run dev` to serve the terminal.
- **Data Ingestion**:
  1. Analytical Core saves figures/data to `outputs/oglo-8figs/fxxx-.../`.
  2. Run `npm run sync` (triggers `sync_manifest.py`) to register new assets in the Terminal Ticker.

## Bloomberg Mandates
1. **High-Density Ticker**: All modules must contribute at least one "High-Signal" scalar metric to the terminal header.
2. **Area Interconnectivity**: Users should be able to drill down into specific hierarchical areas (e.g., clicking 'V1' triggers a global filter across all synced figures).
3. **Madelane Aesthetic**: Pure Madelane Golden Dark theme (#CFB87C / #9400D3) on pure white backgrounds.

## Documentation Mandate
All terminal components must explicitly define:
- **Inputs**: Metadata keys, data sources (manifest.json).
- **Outputs**: Rendered interactive layers, exported SVG/PDF assets.


