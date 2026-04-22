---
name: jax-actions
description: High-performance biophysical modeling suite using JAX and Jaxley for large-scale E-I network simulations (NetEIG).
---
# skill: jax-actions

## When to Use
Use this skill for all "Phase 5" predictive modeling tasks. It is mandatory for:
- Building multi-area biophysical networks (e.g., V1 + PFC).
- Optimizing synaptic weights using GSDR (Genetic Stochastic Delta Rule).
- Running high-throughput simulations on GPU/TPU.
- Implementing "Physical Realisticity Barriers" to prevent NaN/Inf propagation in ODE solvers.

## What is Input
- **Network Architecture**: Population counts (E, IG, IL), connectivity kernels, and synaptic mechanisms (AMPA, GABA).
- **Control Params**: Learning rates, metabolic penalties, and stochastic floors for optimization.
- **Simulation Window**: Usually 1500ms (500ms baseline, 500ms stimulus, 500ms post).

## What is Output
- **Optimized PyTrees**: JAX-compatible parameter structures containing trained weights.
- **State Trajectories**: Voltage traces, synaptic gating variables, and firing rates.
- **Biophysical Reports**: Metrics for E/I balance, asynchrony (Kappa), and metabolic efficiency.

## Algorithm / Methodology
1. **Dynamic Seeding**: Generates high-entropy seeds for every simulation trial to ensure independent realizations.
2. **Gradient Clipping**: Enforces `jnp.where(jnp.isnan(v), old_v, v)` and clips membrane potential to [-100mV, +50mV].
3. **AGSDR v2**: Employs Adaptive Mixing where the ratio of supervised vs. unsupervised updates is determined by their relative EMA variances.
4. **Independent Synapses**: Uses `make_synapses_independent` to decouple weights, allowing for granular learning in 100k+ synapse networks.
5. **Robust Pipeline**: A 7-step sequence (Sweep -> Setup -> Checkup -> Stability -> Precision -> Visualize) for production-grade model validation.

## Placeholder Example
```python
import jax
import jaxley as jx
from core.mechanisms.models import make_synapses_independent

# 1. Build and Prepare
net = build_net_eig(seed=None) 
make_synapses_independent(net, "gAMPA")

# 2. Optimized Step with Stability Barrier
def update_step(params, state):
    grads = jax.grad(loss_fn)(params, state)
    params = jax.tree.map(lambda p, g: p - 1e-3 * g, params, grads)
    return jax.tree.map(lambda p: jnp.clip(p, 0.0, 10.0), params)
```

## Relevant Context / Files
- [jaxley-advanced](file:///D:/drive/omission/.gemini/skills/jax-actions/docs/jaxley-advanced.md) — For low-level API details.
- [src/biophys/optimizers.py](file:///D:/drive/omission/src/biophys/optimizers.py) — The implementation of AGSDR and GSDR.
