---
name: jax-actions
---
# jax-actions

## Purpose
JAX/Jaxley biophysical modeling: multi-area E-I networks (NetEIG), GSDR optimization, GPU simulation, NaN barrier enforcement.

## Input
| Name | Type | Description |
|------|------|-------------|
| network_arch | dict | Population counts (E, IG, IL), connectivity, synaptic mechanisms |
| control_params | dict | Learning rates, metabolic penalties, stochastic floors |
| sim_window | int | Simulation duration (default: 1500ms) |

## Output
| Name | Type | Description |
|------|------|-------------|
| optimized_params | PyTree | JAX-compatible trained weights |
| state_traces | ndarray | Vm, gating variables, firing rates |
| ei_report | dict | E/I balance, asynchrony (Kappa), metabolic cost |

## Mandatory Rules
- Physical Realisticity: `Vm ∈ [-100, +50] mV`, NaN → `jnp.where(isnan, old, new)`
- Gradient clipping on all conductances
- `make_synapses_independent` for per-synapse learning

## Example
```python
import jax
import jaxley as jx
net = build_net_eig(seed=None)
make_synapses_independent(net, "gAMPA")
def update_step(params, state):
    grads = jax.grad(loss_fn)(params, state)
    return jax.tree.map(lambda p, g: jnp.clip(p - 1e-3*g, 0, 10), params, grads)
```

## Files
- [optimizers.py](file:///D:/drive/omission/src/biophys/optimizers.py) — AGSDR/GSDR
