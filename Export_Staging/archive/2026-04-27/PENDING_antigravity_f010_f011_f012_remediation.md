# Comprehensive Improvement Plan: f010, f011, f012
**Date**: 2026-04-25
**Agent**: Antigravity (QA/Planning)
**Target**: Omission Analytical Core (CLI)

## 1. Objective
Following the recent aesthetic audit, we are expanding the remediation of **f010, f011, and f012** into a full-scale analytical improvement. The primary mandate is **"Include ALL OF THE DATA"**. We will move away from isolated session-level plots and compute robust, population-level visualizations spanning the full 11-area hierarchy and the complete 4-second temporal window.

---

## 2. f010: Delta Spike-Field Coherence (SFC)
### **Current Limitations**: 
Lacks full temporal resolution and does not aggregate across the entire unit population effectively.
### **Improvement Strategy**:
- **Include All Data**: Extract LFP and Spike data for **every 'Stable-Plus' unit** across all 11 hierarchical areas.
- **Continuous Temporal SFC**: Instead of a single static metric, compute the Delta-band (2-4 Hz) SFC over the full `[-2000, 2000]ms` continuous window using a sliding window approach.
- **Visualization**: Plot the population-averaged Delta SFC trajectory over time for each area, overlaid on the same axis (or as a multi-panel grid).
- **Aesthetics**: Madelane Golden Dark palette, white background, black axes, and SVG export enabled.

---

## 3. f011: Laminar Cortical Mapping
### **Current Limitations**: 
Aesthetic failures (blue background, old naming conventions) and likely under-utilizing the full spatial density of the probes.
### **Improvement Strategy**:
- **Include All Data**: Iterate through **all valid sessions and all probes**. For every cortical area, extract the raw channel-depth mapping.
- **Laminar Alignment**: Align the channels computationally by identifying the Layer 4 (L4) sink. Standardize the Y-axis to represent cortical depth relative to L4 (e.g., Superficial vs. Deep).
- **Visualization**: Generate a spatial depth-profile heatmap of Multi-Unit Activity (MUA) or High-Gamma power across the full `[-2000, 2000]ms` window. 
- **Aesthetics**: Standardize to pure `#FFFFFF` backgrounds, black axes, and `f011_laminar_{area}` naming convention.

---

## 4. f012: Current Source Density (CSD) Profiling
### **Current Limitations**: 
Utilizes a non-compliant `RdBu` colormap and lacks interactive SVG export.
### **Improvement Strategy**:
- **Include All Data**: Compute the spatial second derivative of the trial-averaged LFP across **all continuous channels** for the aligned probes in each area. Average the CSD maps across all sessions for a given area to produce a highly robust, noise-free population CSD profile.
- **Spatiotemporal Heatmap**: Plot Depth (Y-axis) vs. Time `[-2000, 2000]ms` (X-axis).
- **Aesthetics**: Enforce the custom **Madelane Divergent Colormap**:
  - Sources (Positive): `#9400D3` (Dark Violet)
  - Zero: `#FFFFFF` (White)
  - Sinks (Negative): `#CFB87C` (Madelane Gold)
- **Interactivity**: Add the `toImage` SVG export configuration to the modebar.

## 5. Execution Directives for CLI Node
1. Completely refactor the data loaders in `f010`, `f011`, and `f012` to ensure `n_jobs` or batching is utilized to process **all sessions/trials** without Memory Exceptions.
2. Apply the specific Plotly layout updates to fix the background colors and ensure SVG export.
3. Save all outputs directly to `D:\drive\outputs\oglo-8figs\` conforming to the strict `fxxx-keyword-keyword` directory naming.
