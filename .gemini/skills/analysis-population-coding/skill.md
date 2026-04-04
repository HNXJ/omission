---
name: analysis-population-coding
description: High-dimensional spiking dynamics (manifolds, SVM decoding, latency) and oculomotor behavioral proxies (DVA, pupil, microsaccades) for the omission hierarchy.
---

# skill: analysis-population-coding

## spiking dynamics & decoding
- **Manifolds**: PCA/t-SNE/UMAP on population activity — 3–5 PCs standard.
- **Decoding**: SVM (linear kernel), binary — Omit vs Delay, A vs B identity.
- **Metric**: Decoding accuracy (%) over sliding 50ms windows.
- **CV**: 5-fold, trial-balanced splits.
- **Factor Matrix**: 48 factors/neuron for omission factor extraction.
- **Surprise Latency**: Time-to-peak for omission response (PFC avg ~38ms lead over V1).

## oculomotor & pupil (behavioral proxies)
- **Eye source**: Raw `.mat` BHV files — `bhvUni.AnalogData.Eye`. Never use NWB eye channel directly.
- **Units**: Degrees of Visual Angle (DVA).
- **Alignment**: Code 101 (P1 onset = 0ms).
- **Pupil channel**: Channel index 2 in `.npy` behavioral files.
- **Precision metric**: XY variance within 1531ms omission window.
- **Saccades**: Velocity threshold >30°/s (Engbert & Kliegl).
- **Jitter**: High-frequency micro-oscillations within fixation window.

## standards
- Always `np.nan_to_num` before any PCA or SVM operation.
- Pupil: baseline-normalized dilation (arousal/surprise proxy).
- Test for precision-quenching (reduced variability) after omission in post-stimulus window.

## quick ref
```python
pca = PCA(n_components=3).fit_transform(trial_matrix)
clf = svm.SVC(kernel='linear').fit(X_train, y_train)
# Eye precision
total_var = np.var(eye_x) + np.var(eye_y)
# Saccade velocity
vel = np.sqrt(np.gradient(x)**2 + np.gradient(y)**2) * FS
```

## session-level decoding workflow
1. Load spike `.npy` arrays: `(n_trials, n_units, T)`.
2. Bin into 50ms sliding windows from -500ms to +4500ms re p1.
3. Extract condition labels (RRRR=0, RXRR=1, RRXR=2, RRRX=3).
4. For each window: `X=(n_trials, n_units)`, `y=labels` → SVM.fit → accuracy.
5. Average accuracy across 5-fold CV splits.
6. Plot accuracy timecourse with ±2SEM shade; mark p1/p2/p3/p4 onsets.

## manifold trajectory workflow
1. PCA on concatenated conditions (all trials × all units × T).
2. Project each condition separately onto PC1-PC3.
3. Compute Euclidean distance between RRRR and RXRR/RRXR/RRRX trajectories.
4. Find first time point where distance exceeds 2SD of baseline → surprise latency.
5. Rank areas by surprise latency → hierarchy index.

## cross-modal rsa link
→ See `analysis-rsa-cka` for comparing spike manifolds with LFP geometry.


---

## spike_lfp_coordination — full api
| Function | Signature | Purpose |
|---|---|---|
| `compute_ppc(phases)` | `array(n_spikes) → float` | Pairwise Phase Consistency (Vinck 2010) — bias-free spike-field coupling |
| `get_band_phase(lfp, band, fs)` | `array, tuple, int → array` | Bandpass filter + Hilbert → instantaneous phase for a band |
| `compute_spike_lfp_ppc_trace(spikes, lfp_phase, win_size, step)` | `(T,), (T,), int, int → array` | Time-resolved PPC over sliding windows (default 200ms/50ms) |
| `compute_spike_lfp_power_corr(spikes, lfp_power, win_size, step)` | `(T,), (T,), int, int → array` | Pearson r between firing rate and LFP power per window |

## usage
```python
from codes.functions.spike_lfp_coordination import (
    get_band_phase, compute_ppc, compute_spike_lfp_ppc_trace
)
phase = get_band_phase(lfp_trial, band=(15, 30), fs=1000)  # beta
ppc   = compute_ppc(phase[spike_idx])
trace = compute_spike_lfp_ppc_trace(spikes, phase, win_size=200, step=50)
```

## interpretation
- **PPC**: Use over PLV/coherence — invariant to spike count bias.
- **Power corr**: Test if omission neurons drive specific oscillatory bands.
- **Band definitions**: Theta 4–8Hz, Alpha 8–14Hz, Beta 15–30Hz, Low-γ 35–55Hz, High-γ 65–100Hz.
