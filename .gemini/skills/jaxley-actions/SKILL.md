---
name: jaxley-actions
description: Core API guide for JAXley-based biophysical simulations, handling structural classes, mechanisms, and independent parameter management.
---
# skill: jaxley-actions

## When to Use
Use this skill when defining the low-level biophysical properties of neural models. It is necessary for:
- Creating `jx.Compartment`, `jx.Branch`, and `jx.Cell` objects.
- Inserting custom ion channels (e.g., `HH`, `Kir`) and synaptic mechanisms (`IonotropicSynapse`).
- Implementing hierarchical parameter sharing vs. independent weight training.
- Merging pre-trained cortical columns (V1, PFC) into a unified multi-area hierarchy.

## What is Input
- **Morphology**: SWC files or manual branch definitions.
- **Biophysics**: Conductance values (`gAMPA`, `gGABA`), time constants, and ion concentrations.
- **Connectivity**: Adjacency matrices or `select()` rules for edge creation.

## What is Output
- **Simulation Objects**: Fully instantiated `jx.Network` structures ready for `jx.integrate()`.
- **Trainable Parameters**: Selection of specific variables for gradient-based optimization.
- **Biophysical Logs**: Records of membrane potential (`v`), gating variables, and ionic currents.

## Algorithm / Methodology
1. **Hierarchical Construction**: Builds networks from compartments -> branches -> cells -> areas.
2. **Independent Weight Pattern**: Mandates `net.select(edges="all").make_trainable("gAMPA")` to ensure every synapse learns its own weight, bypassing the default JAXley sharing logic.
3. **Synaptic Diversity**: Implements `GradedNMDA` with magnesium block logic for realistic excitatory recurrence.
4. **Decimation Protocol**: Downsamples voltage traces (e.g., 10x) for long simulations to prevent RAM exhaustion in interactive HTML reports.
5. **Cortical Hierarchy**: Wires areas using FF (L2/3 -> target L4) and FB (L5/6 -> target L1) projections based on Markov 2014 rules.

## Placeholder Example
```python
import jaxley as jx
from core.mechanisms.models import make_synapses_independent

# 1. Create Hierarchical Network
net = jx.Network([jx.Cell() for _ in range(100)])

# 2. Enforce Independent Parameters for Training
# Crucial for Phase 5 PAC/Functional Connectivity studies
net.select(edges="all").make_trainable("gAMPA")
make_synapses_independent(net, "gGABAa")
```

## Relevant Context / Files
- [jax-actions](file:///D:/drive/omission/.gemini/skills/jax-actions/skill.md) — For high-level GSDR optimization.
- [src/biophys/builder.py](file:///D:/drive/omission/src/biophys/builder.py) — Implementation of hierarchical column construction.
