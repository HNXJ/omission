# FIG_31: RNN-Based Modeling of State Trajectories

## 🎯 Intent
To determine if a recurrent neural network (RNN) can learn the hierarchical routing rules of the task and replicate the population trajectories observed in the cortex.

## 🔬 Methodology
- **Source**: `src/f031_rnn/train.py`
- **Architecture**: Reservoir Computing (Echo State Network) with 1000 hidden nodes.
- **Training**: Trained on sequences (AAAB, AXAB) using FORCE learning.
- **Metric**: Comparison of RNN population dynamics (PCA) vs. empirical data.

## 📊 Observations
- Predictive power: The RNN successfully replicates both the stimulus-locked trajectories and the omission-driven manifold "derailment."
- Hierarchical correspondence: RNN nodes with slow time constants effectively model PFC-like representation, while fast nodes replicate V1.

## 📝 Caption & Labels
**Figure 31. Recurrent Neural Network Modeling of Cortical Routing Rules.**
(A) PCA trajectories for RNN activity during standard and omission trials.
(B) Correlation matrix between RNN hidden state dynamics and empirical PFC population dynamics.

## 🗺️ Narrative Context
Concludes the manuscript by bridging the gap between empirical neurophysiology and computational theory.
