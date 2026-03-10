# Neuroscience Writing: Biophysical Methods (Jaxley & gSDR)

Standard for documenting computational models to ensure peer-review rigor.

## 1. Model Specification
- **Morphology**: Formally state compartment counts (e.g., "Two-compartment Soma-Dendrite model") and dimensions ($radius$, $length$).
- **Equations**: List core channel conductances (Hodgkin-Huxley) and synaptic kinetics (Graded AMPA/GABA).
- **Parameters**: Provide a table of all static biophysical parameters (e.g., $C_m, E_{leak}, g_{Na}, g_{K}$).

## 2. Solver & Integration
- **Platform**: State the environment (e.g., "JAX/Jaxley backend on Apple Silicon Metal").
- **Integration**: Specify the numerical protocol (e.g., "Implicit Euler for voltages, Exponential Euler for gates").
- **Time Step**: State the $dt$ (e.g., "0.1ms") and justify stability checks performed (The Physical Realisticity Barrier).

## 3. Optimization Protocol (AGSDR)
- **Algorithm**: Describe the adaptive mixing of supervised gradients and stochastic noise.
- **Loss Function**: Formally define the target (e.g., "Power Spectral Density distance and Fleiss' Kappa synchrony").
- **Hyperparameters**: Document learning rate, EMA momentum, and the Alpha Floor ($0.1$).
