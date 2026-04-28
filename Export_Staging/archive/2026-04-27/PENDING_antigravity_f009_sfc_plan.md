# Phase B Revision: Individual Unit Spike-Field Coherence (f009)
**Date**: 2026-04-25
**Target**: Omission Analytical Core (CLI)
**Status**: DRAFT (Awaiting User Approval)

## 1. Objective
Replace the existing `f009` module with a robust Pairwise Phase Consistency (PPC) and Spike-Field Coherence (SFC) analysis. The goal is to perfectly replicate the reference visual (`10.png`) while expanding the analysis to include explicitly defined functional classes and their corresponding Polar Phase distributions.

## 2. Population Refinement (N=80 Units)
Instead of a random sample, we will strictly extract the **top 20 responsive units** for each of the following four functional categories:
1. **O+ Units**: Omission-excited
2. **S+ Units**: Stimulus-excited
3. **S- Units**: Stimulus-suppressed
4. **Null Units**: Unresponsive controls
*(Note: 20 per class yields 80 total units. This guarantees high-SNR phase tracking).*

## 3. Analytical Methodology
- **Conditions**: Extract trials for **Standard** (AAAB), **Expected** (AXAB preceding Stimuli), and **Omission** (AXAB).
- **Frequency Bands**: 
  - Theta (4-8 Hz) - *Color: Red*
  - Beta (13-30 Hz) - *Color: Blue*
  - Gamma (30-80 Hz) - *Color: Brown/Golden*
- **Metric**: Calculate the Spike-Triggered Phase and compute the **Pairwise Phase Consistency (PPC)** to rigorously control for spike-count disparities across conditions. Normalize the PPC into a **Z-score** against a null distribution generated via 1,000 random spike-time shuffles.

## 4. Visualization & Output Matrix
The script will output two primary interactive HTML figures (with synchronized SVG backups) for each functional class into `outputs/oglo-8figs/f009-individual-sfc`:

### 4.1 Coherence Barplots (Replicating `10.png`)
- **Type**: Grouped bar chart with overlaid SEM error bars.
- **Axes**: X-axis = Condition (Omission, Expected, Standard). Y-axis = Coherence Z-score.
- **Aesthetic**: White background, high-contrast black axes, outward ticks.

### 4.2 Circular Polar Plots (New Requirement)
- **Type**: Polar histogram mapped to `[0, 2π]`.
- **Metrics**: Plot the phase density of spike occurrences relative to the LFP oscillation. 
- **Vectors**: Overlay the Mean Resultant Vector (MRV) arrow to highlight the preferred firing phase and its significance (Rayleigh Test).

## 5. Execution Directives for CLI Node
1. Completely overwrite `src/f009_individual_sfc/`.
2. Extract the 80 specific units using the 'Stable-Plus' metadata.
3. Compute the PPC and Circular Phase.
4. Export the HTML/SVG grid to the canonical `f009` output directory.
