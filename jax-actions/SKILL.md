---
name: jax-actions
description: Comprehensive skill for biophysical neural network modeling using JAX and Jaxley. Includes building NetEIG architectures (E, IG, IL populations) and running high-performance simulations with voltage trace processing, spike matrix conversion, and synchrony analysis (Kappa, PSD).
---

# JAX Actions Skill

This skill guides the construction, simulation, and analysis of biophysical E-I networks in **Jaxley** and **JAX**.

## 1. Network Construction: `net_eig`
The `net_eig` model is a three-population biophysical network:
- **Ne (Excitatory)**: Primary signal-carrying neurons.
- **Nig (Global Inhibitory)**: Interneurons for global feedback (SST-like).
- **Nil (Local Inhibitory)**: Interneurons for local feedback (PV-like).

### Building Workflow
1. **Initialize Populations**: Use `jx.Soma(HH(), Leak())` for e_cells, ig_cells, and il_cells.
2. **Connectivity (AMPA & GABA)**:
   - **E -> E/I**: `GradedAMPA`.
   - **I -> E/I**: `GradedGABAa`.
3. **Sparse vs. Full Connection**: Use `jx.connect.sparse_connect` or `jx.connect.fully_connect`.

## 2. Simulation Workflow
- **Standard Parameters**: `dt_global = 0.1 ms`, `t_max = 1500 ms`.
- **Stimulus Window**: `t_on = 500 ms`, `t_dur = 500 ms`.

### Simulation Functions
- **`sw_simulate`**: Main simulation entry point. Setup noise current (`noise_current_ac`) and run `net.simulate()`.
- **Trace Processing**: Convert raw voltage recordings to binary spike matrices.

## 3. Analysis Tools
- **Synchrony (Kappa)**: Measure inter-neuron synchrony using Fleiss' Kappa.
- **Power Spectral Density (PSD)**: Analyze population-level oscillations and Beta/Gamma power shifts during stimulus.
- **Saving Traces**: Use `.pkl` or `.npy` format for raw voltage recordings.

## 4. Optimization Workflow (GSDR)
The `AAE.gsdr` package provides formal tools for evolutionary biophysical tuning.
- **Optimizers**: `GSDR` (Genetic-Stochastic Delta Rule) wrapped around `optax.adam`.
- **Targeting**: Optimize for specific PSD peaks (e.g., 38Hz Gamma) and minimize synchrony (Kappa) using custom multi-window loss functions.
- **MCDP (Mutual-correlation dependent plasticity)**: Synaptic parameters' activity (correlation between pre- and post-synaptic traces) shapes their changes across trials, acting as a biophysical weight-update scaling factor.

## Key Parameters
- **`gAMPA` / `gGABAa`**: Synaptic conductances.
- **`tau`**: Synaptic time constants.
- **Stimulus Parameters**: Amplitude and noise level for the simulated task.
- **GSDR Parameters**: `a_init` (self-supervision), `checkpoint_n`, and `kappa_weight`.
- **MCDP**: Ensures that synaptic changes are driven by the mutual-correlation of the neurons they connect.
