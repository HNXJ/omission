# Visual QA Audit Report: Omission Dashboard

## Audit Summary
- **Date**: 2026-04-24
- **Auditor**: Antigravity
- **Scope**: Figures F001 - F045
- **Overall Status**: **FAIL** (Systemic issues in final block and aesthetic non-compliance in several core figures)

---

## Detailed Findings

### [PASS] Figure F001 - F003
*   **Status**: `[PASS]`
*   **Critique**: Perfectly compliant with "Madelane Golden Dark" aesthetics. Data projections are clear and informative.

### [FAIL] Figure F012: Csd Profiling
*   **Status**: `[FAIL]`
*   **Critique**: **Mandate Violation**. Background is BLACK; violates the "White background, black axis" rule. Title is also clipped by the top margin.
*   **Proposed Fix**: Update `src/f012_csd_profiling/plot.py` to set `template='plotly_white'` and `paper_bgcolor='#FFFFFF'`. Increase `margin=dict(t=100)`.

### [FAIL] Figure F018: Ghost Signals
*   **Status**: `[FAIL]`
*   **Critique**: **Color/Layout Violation**. Prohibited color (Cyan) detected in traces. Legend overlaps with the plot title.
*   **Proposed Fix**: Update `src/f018_ghost_signals/plot.py` to use the approved palette (Red, Blue, Brown, Green, Orange, Purple, Yellow). Move legend to `orientation='h'` at the top or bottom.

### [FAIL] Figure F019: Pac Analysis
*   **Status**: `[FAIL]`
*   **Critique**: **Color Violation**. Prohibited color (Cyan) used for FEF bars.
*   **Proposed Fix**: Replace `#00FFFF` / `cyan` in `src/f019_pac_analysis/plot.py` with an approved color from the project palette.

### [FAIL] Figure F023: Spectral Fingerprints
*   **Status**: `[FAIL]`
*   **Critique**: **Color Violation**. Prohibited color (Cyan) used for MST fingerprints.
*   **Proposed Fix**: Update `src/f023_spectral_fingerprints/plot.py` color mapping.

### [FAIL] Figure F027: Identity Decoding
*   **Status**: `[FAIL]`
*   **Critique**: **Color Violation**. Prohibited color (Cyan) used for FEF decoding trace.
*   **Proposed Fix**: Update `src/f027_identity_coding/plot.py` to use approved colors.

### [FAIL] Figure F031 – F045 (Block Failure)
*   **Status**: `[FAIL]`
*   **Critique**: **Empty Plots**. Methodology text renders, but the Plotly containers are empty. Likely due to missing or empty source data arrays in the `outputs/` directory.
*   **Proposed Fix**: Coordinate with `omission-core` to ensure Phase B scaling has correctly exported these figures. Check for file path mismatches in `script.py` vs `manifest.json`.

---

## Technical Debt & Aesthetic Cleanup
- [ ] **Global Background Fix**: Scan all `plot.py` files for `paper_bgcolor` and ensure they default to `#FFFFFF`.
- [ ] **Color Palette Enforcement**: Replace all instances of `cyan`, `teal`, and `aqua` with `Blue` or `Green` from the approved set.
- [ ] **Title Margin Check**: Standardize `margin=dict(t=100, b=80, l=80, r=40)` across all `OmissionPlotter` instances.

---
**Visual Proof**: Screenshots of failures are stored in the `Export_Staging/` directory for human review.
