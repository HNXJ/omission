---
name: analysis-neuro-omission-pac-analysis
description: Computes Phase-Amplitude Coupling (PAC) using the Modulation Index (MI). Quantifies how low-frequency phases (Theta) modulate high-frequency amplitudes (Gamma).
---
# skill: analysis-neuro-omission-pac-analysis

## When to Use
Use this skill to investigate cross-frequency coordination. It is the primary tool for:
- Testing if the "temporal framework" of the omission response is organized by Theta oscillations.
- Comparing Theta-Gamma coupling strength in PFC vs. V1.
- Quantifying the coordination of fast neural updates within slow periodic cycles.

## What is Input
- **LFP Signal**: Raw or broadband LFP trace.
- **Frequency Bands**: Low-frequency range (Phase, e.g., 4-12Hz) and High-frequency range (Amplitude, e.g., 30-100Hz).
- **Trial Windows**: Specific epochs (e.g., Stimulus onset or Omission window).

## What is Output
- **Modulation Index (MI)**: A single scalar value representing the strength of coupling.
- **Comodulogram**: A 2D heatmap showing MI values across a range of phase and amplitude frequencies.
- **Phase-Amplitude Distribution**: A polar or bar plot showing mean amplitude across phase bins.

## Algorithm / Methodology
1. **Filtering**: Band-pass filters the signal for both the phase and amplitude components.
2. **Phase/Amplitude Extraction**: Uses the Hilbert transform to extract the instantaneous phase of the slow signal and the amplitude envelope of the fast signal.
3. **Binning**: Divides the phase cycle (0-360°) into equal bins (default=18).
4. **Mean Amplitude Distribution**: Calculates the average high-frequency amplitude within each phase bin.
5. **MI Calculation**: Uses the Tort method, which applies KL-divergence to measure the deviation of the amplitude distribution from a uniform distribution.

## Placeholder Example
```python
from src.analysis.pac import calculate_modulation_index

# 1. Prepare data
lfp_trace = get_lfp_session(session_id)

# 2. Compute PAC for Theta (4-8Hz) and Gamma (40-80Hz)
mi_value = calculate_modulation_index(
    lfp_trace, 
    f_phase=(4, 8), 
    f_amp=(40, 80),
    n_bins=18
)

print(f"Modulation Index: {mi_value:.6f}")
```

## Relevant Context / Files
- [analysis-lfp-pipeline](file:///D:/drive/omission/.gemini/skills/analysis-lfp-pipeline/skill.md) — For band-passing and Hilbert logic.
- [src/analysis/pac.py](file:///D:/drive/omission/src/analysis/pac.py) — Core implementation.
