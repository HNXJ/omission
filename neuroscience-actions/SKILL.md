---
name: neuroscience-actions
description: Comprehensive skill for neuroscience research, paper analysis, and biophysical modeling. Includes knowledge on interneurons, laminar motifs, and paper management pipelines.
---

# Neuroscience Actions Skill

This skill guides the intersection of biological neuroscience research and computational modeling.

## 1. Biophysical Constants & Formulas
- **Axial Current ($I_a$)**: $\frac{V_d - V_s}{r_a}$. Primary contributor to MEG/EEG source.
- **Impulse Poisson (IP) Noise**: Event-driven stochastic current.
    - `pulse_width`: Standard 0.1ms.
    - `poisson_l`: Mean interval (20ms - 500ms).
    - `pulse_amp`: Magnitude (0.01nA - 10nA).
- **Stochastic Implementation Lessons**:
    - **Vectorization**: Custom stochastic mechanisms must handle batched seeds using `jax.vmap(jax.random.PRNGKey)` within `update_states` to support multi-neuron networks.
    - **Mechanism Insertion**: In modular networks, mechanisms must be inserted *after* combining cells into the final `jx.Network` to ensure global visibility across all view attributes.
- **PING (Pyramidal Interneuron Network Gamma)**: Mechanism where E-cells drive I-cells (PV), which in turn provide rhythmic feedback inhibition.
- **ING (Interneuron Network Gamma)**: Reciprocal inhibition between I-cells driving gamma.

## 2. Laminar Architecture & Interneurons
- **Parvalbumin (PV)**: Fast-spiking, perisomatic target. Essential for **Gamma** (30-80 Hz).
- **Somatostatin (SST/CB)**: Low-threshold spiking, targets distal dendrites. Modulates **Beta** (15-25 Hz).
- **VIP**: Disinhibitory interneurons targeting SST cells.
- **Spectrolaminar Motif**: The spectral crossover between Alpha/Beta (Deep) and Gamma (Superficial) layers.

## 3. Study Summaries (March 2026 Batch)
- **Scz_AM2025_ing**: Investigates cellular basis of ScZ. Key finding: $\downarrow$ PV density $\rightarrow$ Weak Gamma; $\uparrow$ CB density $\rightarrow$ Enhanced Beta.
- **Lichtenfeld2024N**: Advanced laminar mapping protocols.
- **jaxley_paper_2025_nn**: Differentiable biophysical simulations at scale.

## 4. Signal Processing & Variability
- **Neural Variability Quenching**: The significant reduction in cross-trial variance observed immediately after stimulus onset. High quenching is often a signature of robust sensory processing.
- **Lead/Lag Analysis (Cross-Correlation)**: 
    - Used to study temporal precedence between areas (e.g., V1 leads PFC during feedforward visual processing).
    - **Formula**: $R_{xy}(\tau) = \sum x(t) y(t+\tau)$. Peak at $\tau > 0$ implies $x$ leads $y$.

## 5. Paper Management Pipeline (PDF to MD/Media)
Use the automated extraction tool to separate text and images for analysis.
- **Path**: `AAE/utils/pdf_extractor.py`
- **Output**: 
  - Markdown organized by section: `/media/pdfs/txt/`
  - Extracted figures: `/media/pdfs/img/`

## 5. Paper Writing & Reference Skills
- **DOI Mapping**: Use `google_web_search` to find missing DOIs.
- **Publication Aesthetic**: "Madelane Golden Dark" theme for all figures.
- **Validation**: Always verify models against biological Kappa and PSD motifs.
