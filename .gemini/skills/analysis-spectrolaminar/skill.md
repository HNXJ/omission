---
name: analysis-spectrolaminar
description: Spectrolaminar profiling of linear-probe LFP data. Computes depth-resolved Alpha/Beta vs Gamma power and identifies the crossover depth for laminar assignment.
source: codes/functions/vflip2_mapping.py
---

# skill: analysis-spectrolaminar

## When to Use
Use this skill when you need to map the laminar organization of cortical columns (e.g., V1 or PFC) using linear probe LFP data. It is specifically used to identify the Layer 4 (L4) boundary via the spectrolaminar crossover method, where Alpha/Beta power dominates deep layers and Gamma power dominates superficial layers.

## What is Input
- `lfp_data`: `numpy.ndarray` (n_channels, n_time_points) - Raw or preprocessed LFP signals.
- `fs`: `float` - Sampling frequency in Hz (default: 1000.0).
- `probes`: `list` of `int` - Indices of probes to process in a session.
- `bands`: (Implicit) Alpha/Beta: 8-30 Hz, Gamma: 35-80 Hz.

## What is Output
- `profiles`: `dict` containing:
    - `alpha_beta`: `numpy.ndarray` - Depth-resolved power profile for low frequencies.
    - `gamma`: `numpy.ndarray` - Depth-resolved power profile for high frequencies.
- `l4_channel`: `int` - The estimated channel index corresponding to the Layer 4 boundary (the crossover point).

## Algorithm / Methodology
1. **Filtering**: Bandpass filter each channel into Alpha/Beta (8–30Hz) and Gamma (35–80Hz) bands.
2. **Power Computation**: Compute the RMS power for each band over the defined stimulus or trial window.
3. **Normalization**: Normalize both Alpha/Beta and Gamma profiles to their respective maximum values (max=1) to ensure comparable scales.
4. **Crossover Detection**: Scan the normalized profiles from deep to superficial channels. The `l4_channel` is defined as the first channel where normalized Gamma power exceeds normalized Alpha/Beta power.

## Placeholder Example
```python
from codes.functions.vflip2_mapping import compute_spectrolaminar_profiles, find_crossover

# 1. Load your LFP data (e.g., from NWB)
# lfp_data.shape = (32, 10000)

# 2. Compute profiles
profiles = compute_spectrolaminar_profiles(lfp_data, fs=1000.0)

# 3. Find Layer 4 crossover
l4_channel = find_crossover(profiles)
print(f"[analysis-spectrolaminar] Identified L4 at channel: {l4_channel}")
```

## Relevant Context / Files
- [vflip2_mapping.py](file:///D:/drive/omission/codes/functions/vflip2_mapping.py) — Core implementation.
- [predictive-routing](file:///D:/drive/omission/.gemini/skills/predictive-routing/skill.md) — Complementary CSD-based mapping.
