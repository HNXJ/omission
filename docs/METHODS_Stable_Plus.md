## Methods: Stable-Plus Population Criteria

To ensure the reliability and interpretability of population dynamics, all subsequent connectivity, decoding, and spectral analyses were restricted to the 'Stable-Plus' unit population. This population represents high-confidence, physiologically active units that satisfy the following strictly enforced criteria:

1. **Firing Rate (FR) Constraint**: Units must exhibit a mean firing rate >1 Hz across the entire session. This excludes low-signal, non-active, or poorly isolated channels.
2. **Signal-to-Noise Ratio (SNR)**: A minimum waveform SNR threshold of 0.8 is required. SNR is calculated as the ratio of the peak-to-peak amplitude of the mean waveform to the standard deviation of the residual noise (calculated in the baseline period).
3. **Trial Presence**: Units must demonstrate 100% trial presence. A unit is discarded if it exhibits significant instability or loss of isolation over the course of the session, as determined by waveform shape drift metrics and inter-spike interval (ISI) violation checks (ISI violation rate < 0.5%).
4. **Recording Fidelity**: Units are verified to be well-isolated using Kilosort 2.5 metrics (e.g., refractory period violations, silhouette scores). 

These strict inclusion thresholds ensure that observed population-level responses are driven by legitimate neural modulation rather than recording artifacts or low-fidelity unit isolation.
