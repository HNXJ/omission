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

## 3. Network Construction: `net_eig` & Cell Subtypes
The `net_eig` model is a multi-population biophysical network featuring specifically tuned Hodgkin-Huxley compartments:
- **Pyramidal (Pyr)**: Multi-compartment (Soma + Distal Dendrite), high M-current adaptation.
- **Parvalbumin (PV)**: Fast-spiking (FS), low capacitance, targets E-soma for Gamma generation.
- **Somatostatin (SST)**: Low-threshold spiking (LTS), targets E-dendrites for Beta resonance.
- **Vasoactive Intestinal Polypeptide (VIP)**: Irregular/bursting, targets SST for disinhibition.

### Connection Dynamics
- **E -> All**: `GradedAMPA`.
- **PV -> E (Soma)**: `GradedGABAa` (Fast inhibition).
- **SST -> E (Dendrite)**: `GradedGABAb` (Slow inhibition) or `GradedGABAa`.
- **Standard Time Constants**: `tauDAMPA = 2.0ms`, `tauDGABAa = 5.0ms`, `tauDGABAb = 50.0ms`.

## 4. Float32 Physical Realisticity Barrier
When using Apple Silicon (Metal MPS) to accelerate JAX, the platform often prefers `float32`. This can cause stiffness and resulting `NaN` or `Inf` values in differential equations.
- **Implementation**: Protect custom channels and synapses (in `gsdr/models.py`) by wrapping the updated state in a dampening barrier:
  `new_val = jnp.where(jnp.isnan(new_val) | jnp.isinf(new_val), old_val, new_val)`
- **Concept**: This acts as a physical barrier. Nature does not have infinite voltages; if a computation explodes, physics simply dampens it, preserving the last stable state.

## 5. Modular Network Merging (Inter-Area Connectivity)
To simulate dysfunction (e.g., disrupted E/I balance) across multiple areas:
1. **Train Separately**: Build and train individual columns (e.g., `net_v1`, `net_pfc`) using GSDR/AGSDR. Save their optimal parameters (PyTrees).
2. **Merge Networks**: Instantiate a new "Super-Network" containing both populations (`all_cells = cells_v1 + cells_pfc; net = jx.Network(all_cells)`).
3. **Load Parameters**: Use `jax.tree.map` or dictionary merging logic to map the saved parameters of the individual areas back into the combined network's PyTree structure.
4. **Connect Areas**: Define specific inter-area synapses (e.g., V1 E -> PFC E) to study multi-area interactions.

## 6. Optimization: AGSDR
The **Adaptive Genetic Stochastic Delta Rule (AGSDR)** is used to tune synaptic conductances. AGSDR dynamically calculates the mixing parameter $\alpha$ as the inverse ratio of the variance of updates from supervised vs unsupervised pathways.

### Workflow
1. **Define Loss**: Targets include peak frequency power and Kappa minimization. Use axial current ($I_a = (V_d - V_s) / r_a$) as the MEG forward model.
2. **Optimizer**: Initialize `AGSDR` via `AAE.gsdr.optimizers.AGSDR`.
3. **Train**: Ensure `seed` randomization for the optimizer's `PRNGKey`.

## 7. Analysis Tools
- **Synchrony (Kappa)**: Measure population-level synchrony. Target asynchronous states (< 0.1) for biological validity.
- **MCDP**: Mutual-correlation dependent plasticity analysis.
- **Spectrograms**: Use `hot` or `magma` colormaps for PSD maps, desaturating for publication (`vmax=1.5`).

## Key Parameters
- **`gAMPA` / `gGABAa` / `gGABAb`**: Synaptic conductances.
- **`tau`**: Synaptic time constants (Decay/Rise).
- **Stimulus**: 120Hz AC current during the stimulus window (500-1000ms).
