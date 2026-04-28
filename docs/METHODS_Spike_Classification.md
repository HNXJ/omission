## Methods: Spike Sorting and Functional Unit Classification

Raw electrophysiological signals were digitized at 30 kHz and processed using Kilosort 2.5 for spike detection and clustering. Following automated clustering, units were subjected to rigorous manual refinement using the phy interface to ensure template stability and avoid multi-unit contamination.

### Functional Unit Classification
To systematically characterize neural sensitivity to the task structure, single units were categorized into functional response classes based on within-unit contrasts:

- **Stimulus-Positive (S+) / Stimulus-Negative (S-)**: Units showing significant firing rate modulation during the stimulus presentation window compared to the pre-trial baseline (Wilcoxon rank-sum, p < 0.01).
- **Omission-Positive (O+) / Omission-Negative (O-)**: Units showing significant firing rate modulation during the omission window compared to the pre-trial baseline.
- **X-Neurons (Omission-Linked)**: A subset of O+ units that exhibited a specific firing rate increase during omission trials where `FR(omission) > FR(stimulus)` and `FR(omission) > FR(baseline)`. These neurons represent the explicit omission-error signal.
- **Null Units**: Units that did not demonstrate significant modulation in either the stimulus or omission windows at the specified alpha levels.

This classification schema allows us to separate general sensory-evoked activity from context-specific prediction-error signaling.
