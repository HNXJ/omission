---
name: analysis-spectrolaminar
description: Spectrolaminar profiling of linear-probe LFP data. Computes depth-resolved Alpha/Beta vs Gamma power and identifies the crossover depth for laminar assignment.
source: codes/functions/vflip2_mapping.py
---

# skill: analysis-spectrolaminar

## purpose
Maps the laminar organization of cortical columns using the spectrolaminar method:
low-frequency (Alpha/Beta) power peaks in deep layers; Gamma peaks superficially.
The crossover between the two profiles identifies Layer 4.

## core functions (vflip2_mapping.py)
| Function | Signature | Purpose |
|---|---|---|
| `compute_spectrolaminar_profiles(lfp_data, fs)` | `(n_ch, T), float → dict` | Computes depth-resolved power for Alpha/Beta band and Gamma band per channel |
| `find_crossover(profiles)` | `dict → int` | Returns channel index where Gamma first exceeds Alpha/Beta — Layer 4 estimate |
| `process_session(session_id, probes)` | `str, list → dict` | Orchestrates profiling + crossover for all probes in a session |

## algorithm
1. Bandpass filter each channel: Alpha/Beta (8–30Hz) and Gamma (35–80Hz).
2. Compute RMS power per channel over the stimulus window.
3. Normalize each profile to max=1.
4. `find_crossover`: scan from deep → superficial; return first channel where γ > α/β.

## interpretation
- **Deep layers (below crossover)**: Alpha/Beta dominant — prediction/feedback.
- **Superficial layers (above crossover)**: Gamma dominant — feedforward/error.
- Crossover = Layer 4 proxy; use for laminar split in spike classification.

## output
```python
profiles = compute_spectrolaminar_profiles(lfp_data, fs=1000.0)
# profiles = {'alpha_beta': array(n_ch), 'gamma': array(n_ch)}
l4_channel = find_crossover(profiles)
```

## cross-ref
→ `predictive-routing` for CSD-based Layer 4 identification (complementary method).
→ `analysis-lfp-pipeline` for preprocessing (bipolar ref) before profiling.

## parameters & defaults
| Parameter | Default | Notes |
|---|---|---|
| `fs` | 1000.0 Hz | Sampling rate of LFP |
| Alpha/Beta band | 8–30 Hz | Low-frequency prediction band |
| Gamma band | 35–80 Hz | High-frequency error band |
| Normalization | max=1 per profile | Ensures fair crossover detection across sessions |

## session loop example
```python
from codes.functions.vflip2_mapping import process_session
results = process_session("230629", probes=[0, 1])
# results[probe_id] = {'l4_channel': int, 'profiles': dict}
```
