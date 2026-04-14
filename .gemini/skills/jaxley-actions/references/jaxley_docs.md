# JAXley Documentation Summary

This document summarizes the JAXley simulator based on its online documentation, intended for creating a Gemini CLI skill.

## 1. Core Features
*   **Differentiable:** Supports automatic differentiation (AD) via JAX, enabling gradient-based optimization of parameters.
*   **Hardware Agnostic:** Runs on CPU, GPU, and TPU without code changes.
*   **High Performance:** Utilizes JAX's `jit` compilation for speeds comparable to C++ simulators.
*   **Numerical Stability:** Employs a backward-Euler solver for stable simulation of multicompartment neurons.
*   **Flexibility:** Provides mechanisms for parameter sharing across compartments, branches, or cells.

## 2. API Structure & Key Classes
The API is hierarchical:
*   **Structural Classes:**
    *   `jx.Compartment`: Smallest simulation unit.
    *   `jx.Branch`: Collection of compartments.
    *   `jx.Cell`: Collection of branches (supports SWC import via `jx.read_swc`).
    *   `jx.Network`: Combines cells and synaptic connections.
*   **Mechanisms:**
    *   `jx.channels.Channel`: Base class for ion channels (e.g., `HH`).
    *   `jx.synapses.Synapse`: Base class for synaptic connections (e.g., `IonotropicSynapse`).
    *   `jx.pumps.Pump`: For ion dynamics.
*   **Simulation & Optimization:**
    *   `jx.integrate()`: Primary simulation function.
    *   `jx.connect()`: Functions for connectivity (`fully_connect`, `sparse_connect`).
    *   `jx.optimize.transforms`: Parameter constraint tools (e.g., `SigmoidTransform`).

## 3. Standard Usage Patterns
A typical workflow:
1.  Define the model (e.g., `cell = jx.Cell(); cell.insert(HH())`).
2.  Set up stimulation and recording (e.g., `cell.stimulate()`, `cell.record('v')`).
3.  Run simulation (e.g., `v = jx.integrate(cell)[1]`).
4.  Visualize results (e.g., using Matplotlib).

## 4. Advanced Capabilities
*   **Morphology Handling:** Supports `d_lambda` rule for compartment discretization and SWC editing.
*   **NMODL Integration:** Imports NEURON NMODL channels.
*   **Gradient-Based Fitting:** `jx.integrate` is JAX-compatible, allowing parameter fitting with `jax.grad` or `jax.value_and_grad` (e.g., using Optax).
*   **Ion Dynamics:** Built-in support for calcium buffering, diffusion, and pumps.

## 5. Best Practices for Gemini CLI Skills
*   **Modular Design:** Encourage separate modules for channels and synapses.
*   **JAX Best Practices:** Advise using `jnp` and avoiding side effects in `jit`-compiled code.
*   **Parameter PyTrees:** Emphasize JAXley's PyTree parameters, compatible with `jax.tree_map`.

**Source URL:** https://jaxley.readthedocs.io/