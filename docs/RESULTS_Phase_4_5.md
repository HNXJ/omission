# Results: Phase 4-5 - Decoding & Computational Synthesis

## 📊 High-Dimensional Decoding of Predicted Absence
To investigate the robustness of neural representations, we employed SVM-based state-space decoding on the Stable-Plus population (FIG_25). We found that omission trials could be classified from standard stimulus trials with >90% accuracy in high-order areas like PFC and FEF. This robust decoding performance, generalizing across sessions, indicates that the brain maintains a discrete and reproducible neural state to represent the "prediction of absence."

## 📊 RNN Modeling of Hierarchical Dynamics
Finally, we bridged empirical findings with computational theory using a Reservoir Computing RNN (FIG_31). The network, trained on the rhythmic stimulus sequences, successfully replicated the manifold dynamics observed in the empirical data—specifically the "derailment" of neural trajectories during omissions. By mapping slow-timescale RNN nodes to PFC representations and fast-timescale nodes to primary sensory regions, the model demonstrates that hierarchical predictive routing is a parsimonious solution for real-time sensory anticipation and error correction.
