---
name: jax-actions
description: Comprehensive skill for biophysical neural network modeling using JAX and Jaxley. Includes building NetEIG architectures (E, IG, IL populations), GSDR optimization, and high-performance simulations.
---

# JAX Actions Skill

This skill guides the construction, simulation, and optimization of biophysical E-I networks using **Jaxley**, **JAX**, and the modular **`gsdr`** package.

## 1. Official Documentation Modules
For deep technical API details and best practices, refer to:
- [JAX Core Documentation](./docs/jax-core.md)
- [Jaxley Advanced Documentation](./docs/jaxley-advanced.md)
- [Biophysical Stability & Synchrony](./biophys-facts.md)

## 2. Modular Framework: `jbiophys`
The `jbiophys` repository is our production engine for granular biophysical modeling.
- **`core/`**: `optimizers`, `mechanisms` (Inoise, IPnoise, GradedAMPA), `neurons`.
- **`systems/`**: `networks` (LaminarColumn, InterArea), `visualizers`, `actions`.

### Experimental Workflows
When writing temporary scripts or performing new optimizations (e.g., baseline parameter tuning):
- Write scripts inside `systems/actions/`.
- Commit these changes to a `dev` branch to keep the `main` branch clean and purely functional.

## 3. Network Construction: `net_eig` & Cell Subtypes
To ensure independent realizations, **never use constant seeds** in production simulations or training loops.
- **Dynamic Seeds**: All `build_net_eig` and noise functions now default to `seed=None`. They generate a high-entropy integer internally if no seed is provided.
- **Realization Handling**: When running multiple trials, pass a unique seed (e.g., `base_seed + trial_index`) to ensure distinct network wiring and noise states.
- **Independent Synapses:** To make every synapse independently trainable (crucial for large networks), use the following pattern before optimization:
  ```python
  net.select(edges="all").make_trainable("gAMPA")
  # Or use jbiophys utility
  from core.mechanisms.models import make_synapses_independent
  make_synapses_independent(net, "gAMPA")
  ```

## 4. Robust 7-Step Modeling Pipeline (`jbiophys`)
For production-grade biophysical models, use the `robust_pipeline` actions:
1. **Initialize:** Build network and enforce parameter independence.
2. **Sweep:** Verify baseline firing (1Hz - 100Hz).
3. **Setup:** Quadratic metabolic penalty + stability hardwires.
4. **Checkup:** 10-epoch dry run for LR/update stability.
5. **Stability:** Clip voltage [-100, 100] and map NaN to 0.
6. **Precision:** Force 64-bit precision via `jax_enable_x64`.
7. **Visualize:** Standard 7-8 figure automated report.

```python
from systems.actions.robust_pipeline import execute_robust_training
params = execute_robust_training(net, epochs=200, lr=1e-3, force_x64=True)
```

## 5. Float32 Physical Realisticity Barrier
- **Stability Protocol**: Always use `jnp.where(jnp.isnan(v) | jnp.isinf(v), old_v, v)` in state updates.

## 5. Numerical Stability & Deadlock Prevention (Optimizer)
- **Cold-Start Fix**: Initialize EMA variances to **1.0** (not 0.0) to ensure a balanced starting alpha ($\alpha=0.5$).
- **Stochastic Floor**: Enforce `alpha_min = 0.1`. This ensures the network always retains a baseline level of stochastic exploration, preventing deadlocks during gradient plateaus.
- **Efficient Reset**: Return `(params_opt - current_params) + optimized_step` during resets to maintain forward momentum.

## 5. Modular Network Merging (Inter-Area Connectivity)
To simulate dysfunction (e.g., disrupted E/I balance) across multiple areas:
1. **Train Separately**: Build and train individual columns (e.g., `net_v1`, `net_pfc`) using GSDR/AGSDR. Save their optimal parameters (PyTrees).
2. **Merge Networks**: Instantiate a new "Super-Network" containing both populations (`all_cells = cells_v1 + cells_pfc; net = jx.Network(all_cells)`).
3. **Load Parameters**: Use `jax.tree.map` or dictionary merging logic to map the saved parameters of the individual areas back into the combined network's PyTree structure.
4. **Connect Areas**: Define specific inter-area synapses (e.g., V1 E -> PFC E) to study multi-area interactions.

## 6. Optimization: AGSDR v2 & Efficient Reset
The **Adaptive Genetic Stochastic Delta Rule (AGSDR)** has been upgraded for enhanced stability, recovery speed, and real-time observability.

### Adaptive Mixing (AGSDR v2)
- **EMA Variance**: Alpha ($\alpha$) is now determined by the **Exponential Moving Average (EMA)** of the supervised vs. unsupervised update variances. This prevents high-variance batches from causing jittery convergence.
- **Dampening**: Adaptive weights are protected by the `float32` realisticity barrier to prevent NaN/Inf propagation.

### Efficient Reset ('Reset + Step')
When a model hits a deselection threshold or checkpoint timeout:
- **Logic**: The update returns `(params_opt - current_params) + optimized_step`.
- **Outcome**: The network doesn't just jump back to the best state; it immediately attempts a new optimized step from that position, ensuring continuous forward motion during recovery.

### Verbose Status Monitoring
Optimizers now include real-time warnings via `jax.debug.print` to aid in debugging "stuck" networks:
- **Stuck Warning**: Triggers when the model hasn't improved for `checkpoint_n` epochs. Indicates a need for increased exploration.
- **Alpha Floor Warning**: Triggers in AGSDR when the supervised gradient variance is too low, causing the mixer to lock at the stochastic floor ($\alpha_{min}=0.1$).
- **Numerical Warning**: Always check logs for "analysis returned nans/zeros" or "network is off" reports during the analysis phase.

## 7. Biophysical Validation Standards
To ensure simulations remain biologically and numerically plausible:
- **Firing Rate Lower Bound**: All neurons should maintain a firing rate of at least **0.5 spikes/sec**. This prevents unrealistic charge accumulation in the dendrites and ensures active steady states.
- **Physiological Voltage**: Membrane potential must stay within **-100mV to +50mV**. Values outside this range should trigger the *Physical Realisticity Barrier*.
- **Synchrony Target**: Production-level models should target **Kappa < 0.1** during stimulation to match observed physiological asynchrony.

## 8. Analysis Tools
- **Synchrony (Kappa)**: Measure population-level synchrony. Target asynchronous states (< 0.1) for biological validity.
- **MCDP**: Mutual-correlation dependent plasticity analysis.
- **Spectrograms**: Use `hot` or `magma` colormaps for PSD maps, desaturating for publication (`vmax=1.5`).

## Key Parameters
- **`gAMPA` / `gGABAa` / `gGABAb`**: Synaptic conductances.
- **`tau`**: Synaptic time constants (Decay/Rise).
- **Stimulus**: 120Hz AC current during the stimulus window (500-1000ms).
