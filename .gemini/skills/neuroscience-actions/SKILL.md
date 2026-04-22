---
name: neuroscience-actions
description: Comprehensive knowledge base for biophysical modeling (JAXley), laminar motifs, interneuron dynamics, and circuit-level neuroscience research.
---
# skill: neuroscience-actions

## When to Use
Use this skill when designing, building, or analyzing biophysical circuit models. It is mandatory for:
- Implementing PING/ING mechanisms for Gamma/Beta generation.
- Configuring EI balance (75% E, 25% I) and laminar-specific connectivity (Markov 2014 rules).
- Modeling synaptic dynamics (AMPA, NMDA, GABA) and Impulse Poisson (IP) noise.
- Managing literature pipelines (PDF-to-Markdown extraction).
- Applying the "Physical Realisticity Barrier" to prevent simulation instability.

## What is Input
- **Network Params**: Connectivity matrices, synaptic ratios, and cell counts.
- **Biophysical Constants**: Axial resistance $(R_a)$, capacitance $(C_m)$, and reversal potentials.
- **Experimental Data**: Target Power Spectral Densities (PSDs) or cross-area lead/lag peaks.

## What is Output
- **Model Architectures**: JAXley Network objects with properly inserted stochastic mechanisms.
- **Simulation Results**: Membrane potentials $(V_m)$, axial currents $(I_a)$, and synthetic LFP/MEG signals.
- **Literature Summaries**: Structured "Theory Evaluation Grids" (ScZ-40, EMO-36, TcGLO).

## Algorithm / Methodology
1. **EI Balance**: Standard 75% Excitatory (RS Pyramidal) vs. 25% Inhibitory (PV, SST, VIP).
2. **Laminar Motifs**: 
   - FF (V1 -> V2): Superficial -> L4/Soma. 
   - FB (V2 -> V1): Deep -> L1/Dendrites.
3. **Interneuron Roles**: PV cells drive **Gamma** (30-80Hz); SST cells modulate **Beta** (15-25Hz).
4. **Physical Realisticity Barrier**: $V_m$ must remain in $[-120, +60]$ mV; nan-handling via `jnp.where` is mandatory.
5. **PDF Extraction**: Use `AAE/utils/pdf_extractor.py` to organize papers into `/media/pdfs/txt/` and `/media/pdfs/img/`.

## Placeholder Example
```python
# 1. Define Axial Current Calculation
# Ia is the primary contributor to MEG source
ia = (v_distal - v_soma) / ra

# 2. Configure PING Mechanism
# E-cells drive PV-cells, which rhythmically inhibit E-cells
network.insert_mechanism(PING_Oscillator())
```

## Relevant Context / Files
- [jaxley-actions](file:///D:/drive/omission/.gemini/skills/jaxley-actions/skill.md) — For implementation specifics.
- [src/neuro/circuits.py](file:///D:/drive/omission/src/neuro/circuits.py) — Canonical circuit definitions for the 11-area model.
