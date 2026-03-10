---
name: jax-actions
description: Comprehensive skill for biophysical neural network modeling using JAX and Jaxley. Includes building NetEIG architectures (E, IG, IL populations), GSDR optimization, and high-performance simulations.
---

# JAX Actions Skill

This skill guides the construction, simulation, and optimization of biophysical E-I networks using **Jaxley**, **JAX**, and the modular **`gsdr`** package.

## 1. Modular Framework: `AAE.gsdr`
Always use the modular `gsdr` package for biophysical modeling.
- **`gsdr.models`**: `build_net_eig`, `Inoise`, `GradedAMPA`, `GradedGABAa`, `GradedGABAb`.
- **`gsdr.optimizers`**: `GSDR`, `SDR`, `ClampTransform`.
- **`gsdr.simulation`**: `noise_current`, `noise_current_ac`, `step_current`.
- **`gsdr.analysis`**: `compute_kappa`, `compute_psd`, `calculate_firing_rates`, `calculate_mcdp`.
- **`gsdr.pipeline`**: `train_net`, `get_loss_fn`.

## 2. Mandatory Randomization (Stochasticity)
To ensure independent realizations, **never use constant seeds** in production simulations or training loops.
- **Dynamic Seeds**: All `build_net_eig` and noise functions now default to `seed=None`. They generate a high-entropy integer internally if no seed is provided.
- **Realization Handling**: When running multiple trials, pass a unique seed (e.g., `base_seed + trial_index`) to ensure distinct network wiring and noise states.

## 3. Network Construction: `net_eig`
The `net_eig` model is a three-population biophysical network:
- **Ne (Excitatory)**: Primary signal-carrying neurons.
- **Nig (Global Inhibitory)**: Slow interneurons for global feedback (SST-like).
- **Nil (Local Inhibitory)**: Fast interneurons for local feedback (PV-like).

### Connection Dynamics
- **E -> All**: `GradedAMPA`.
- **IG -> All**: `GradedGABAa` (Fast inhibition).
- **IL -> Subset**: `GradedGABAb` (Slow inhibition) or `GradedGABAa`.
- **Standard Time Constants**: `tauDAMPA = 2.0ms`, `tauDGABAa = 5.0ms`.

## 4. Optimization: GSDR
The **Genetic Stochastic Delta Rule (GSDR)** is used to tune synaptic conductances to target specific spectral motifs (e.g., 38Hz Gamma) while minimizing synchrony (Kappa < 0.1).

### Workflow
1. **Define Loss**: Targets include peak frequency power and Kappa minimization.
2. **Transform**: Use `ClampTransform` to keep conductances within biophysical bounds.
3. **Train**: Use `train_net` from the pipeline, ensuring `seed` randomization for the optimizer's `PRNGKey`.

## 5. Analysis Tools
- **Synchrony (Kappa)**: Measure population-level synchrony. Target asynchronous states (< 0.1) for biological validity.
- **MCDP**: Mutual-correlation dependent plasticity analysis.
- **Spectrograms**: Use `hot` or `magma` colormaps for PSD maps, desaturating for publication (`vmax=1.5`).

## Key Parameters
- **`gAMPA` / `gGABAa` / `gGABAb`**: Synaptic conductances.
- **`tau`**: Synaptic time constants (Decay/Rise).
- **Stimulus**: 120Hz AC current during the stimulus window (500-1000ms).
