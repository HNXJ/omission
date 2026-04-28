# PENDING TASK
Target Agent: `antigravity`
Author Agent: `omission-core`
Date: 2026-04-22

## Task: Master Execution Plan: Heavy Placeholder Replacement (Phase 2/3 & Phase 4)

Hello `antigravity`. We are advancing to the most computationally demanding stage of the project. Your task is to systematically replace the remaining 11 placeholder directories (`f012`-`f015` and `f034`-`f040`) with publication-grade analytical suites derived directly from our canonical predictive-routing and sequence-deviance literature (Westerberg et al. 2025; Bastos et al. 2020).

### 1. Mandatory Biomechanical & Statistical Constraints

#### 1.1 Spike-Field Coherence (SFC) & Phase Logic (CRITICAL)
For all coherence, phase-locking, or phase-amplitude coupling analyses (specifically `f014`, `f015`, `f038`, `f039`), you MUST utilize the canonical "jbiophysics" style logic outlined below:
- **Subsampling Mandate**: Coherence (PLV) is heavily biased by firing rate. You MUST subsample spikes to equate the count between conditions (e.g., predictable vs. omission) before calculating PLV. Failure to do so will confound "Neural Surprise" (firing rate jumps) with true phase-locking.
- **Phase Extraction**: Use 1000Hz aligned arrays. Bandpass filter (SciPy `butter` + `filtfilt`), apply the `hilbert` transform, extract `np.angle`, and index the phase array at the exact spike millisecond. 
- **Mean Resultant Vector**: Compute PLV as `abs(mean(exp(1j * phases)))`.
- **Validation**: Generate a Spike-Triggered Average (STA) of the LFP as an internal validity check. A clear oscillatory trough confirms the SFC calculation is not picking up noise.

#### 1.2 Data Infrastructure
- **Population**: Restricted to the 5,416 'Stable-Plus' units.
- **Loading**: Strict `mmap_mode='r'` for all 6000ms `.npy` arrays.
- **Timing**: Baseline (-250ms to -50ms) must be locked to the dynamic omission indices (p2=1031, p3=2062, p4=3093).

---

### 2. Phase 2/3 Replacement Suite (f012 - f015)

* ~~**`f012`: Current Source Density (CSD) Profiling**~~ [COMPLETED]
  * **Method**: Compute the 2nd spatial derivative of the LFP across the linear probe (`CSD(t,c) = -sigma * (V(t,c-2) - 2V(t,c) + V(t,c+2)) / (2*s^2)`).
  * **Goal**: Isolate the exact synaptic input layers (Granular vs. Extragranular) activated during the "Ghost" window.

* ~~**`f013`: Trial-by-Trial Rhythmic Evolution**~~ [COMPLETED]
  * **Method**: Track Gamma vs. Alpha/Beta LFP power across consecutive predictable trials.
  * **Goal**: Visualize the adaptation (quenching) of Gamma and the plateauing of Beta as the "internal model" strengthens.

* ~~**`f014`: Spiking Nonparametric Granger Causality**~~ [COMPLETED]
  * **Method**: Compute Fourier-domain Granger Causality on population-level spiking time series (200ms sliding windows).
  * **Goal**: Test if omissions drive a sudden surge of feedforward (V1 → PFC) directed information flow relative to baseline.

* ~~**`f015`: Spectral LFP Granger Causality**~~ [COMPLETED]
  * **Method**: Compute directed spectral GC between all 11-area pairs.
  * **Goal**: Validate the Predictive Routing hypothesis: Unpredicted events flow forward in Gamma; Predictions flow backward in Alpha/Beta.

---

### 3. Phase 4 Replacement Suite (f034 - f040)

* ~~**`f034`: Percent Explained Variance (PEV) / Omega-squared**~~ [COMPLETED]
  * **Method**: Compute $\omega^2$ to quantify how much spike-rate variance is explained by sequence identity over time.
  * **Goal**: Track the "information fidelity" of the absent stimulus in Deep vs. Superficial layers.

* ~~**`f035`: Deviance-Scaling Response Analysis**~~ [COMPLETED]
  * **Method**: Compare omission response magnitudes across probability contexts (e.g., Rare vs. Frequent).
  * **Goal**: Test if the neural surprise signal scales proportionally with statistical improbability (true prediction error).

* ~~**`f036`: Inhibitory Interneuron Subpopulation Dynamics**~~ [COMPLETED]
  * **Method**: Isolate putative Inhibitory neurons (spike duration < 400µs).
  * **Goal**: Test if interneurons show a *release* of subtractive inhibition during omissions.

* **`f037`: Stimulus Selectivity Index**
  * **Method**: Compute `(Pref - NonPref) / (Pref + NonPref)` for each unit.
  * **Goal**: Prove that predictability effects act selectively on the *expected* stimulus pathway, not general arousal.

* **`f038`: Layer-Specific Directed Granger Causality**
  * **Method**: Compute directed GC explicitly between layer pairs (e.g., V1 Superficial → PFC Deep).
  * **Goal**: Confirm superficial origin of feedforward error and deep origin of top-down predictions.

* **`f039`: Rhythmic GLM Coupling**
  * **Method**: Fit a General Linear Model linking trial-by-trial PFC Alpha/Beta fluctuations to V1 Gamma and spiking.
  * **Goal**: Provide statistical evidence that top-down rhythms actively *inhibit* bottom-up sensory processing.

* **`f040`: Onset-Latency Hierarchical Mapping**
  * **Method**: Calculate time-to-first-significant-cluster for the omission response across all 11 areas.
  * **Goal**: Map the temporal flow of surprise (V1-first vs. PFC-first).

---

### 4. Routing & Execution
1. **Batch Processing**: Because this list is massive, you may execute these in logical batches (e.g., 2-3 figures per cycle).
2. **Replacement & Documentation Mandate**: For each completed figure, rename the corresponding placeholder folder (e.g., `f012-placeholder` -> `f012-csd-profiling`) and generate the HTML plot. You MUST write a `README.md` for each figure that strictly adheres to the new I/O mandate: it must explicitly contain 'What is Input' and 'What is Output' sections detailing the data shapes and files used/generated.
3. **Visual QA**: Visually verify the plots to ensure they are not empty, lack NaN anomalies, display meaningful biology rather than pure noise, and adhere to the Madelane Golden Dark theme.
4. **VCS MANDATE**: You MUST execute `git add . ; git commit -m "feat: implement <figures>" ; git pull --rebase ; git push` after every successful batch.
5. Update this payload document, crossing out completed figures, and save it back to `Export_Staging/PENDING_antigravity_heavy_placeholder_replacement.md`.
