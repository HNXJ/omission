---
name: jaxley-actions
---
# jaxley-actions

## Purpose
JAXley API for biophysical neural models: compartment/branch/cell hierarchy, ion channel insertion, independent parameter management, cortical column merging.

## Input
| Name | Type | Description |
|------|------|-------------|
| morphology | SWC / manual | Branch definitions |
| biophysics | dict | `{gAMPA, gGABA, tau_m, E_rev}` |
| connectivity | ndarray / rules | Adjacency or `select()` edge rules |

## Output
| Name | Type | Description |
|------|------|-------------|
| network | jx.Network | Ready for `jx.integrate()` |
| trainable_params | list | Selected variables for gradient optimization |

## Key Patterns
- Independent weights: `net.select(edges="all").make_trainable("gAMPA")`
- FF wiring: L2/3 → target L4/Soma
- FB wiring: L5/6 → target L1/Dendrites
- Decimation: downsample 10× for long sims

## Example
```python
import jaxley as jx
from core.mechanisms.models import make_synapses_independent
net = jx.Network([jx.Cell() for _ in range(100)])
net.select(edges="all").make_trainable("gAMPA")
make_synapses_independent(net, "gGABAa")
```

## Files
- [builder.py](file:///D:/drive/omission/src/biophys/builder.py) — Hierarchical column construction
