---
name: jaxley-actions
description: Provides tools for building, simulating, and optimizing biophysical neural network models using JAXley. Use when working with JAXley for differentiable neural simulations, parameter fitting, and hardware-accelerated computation.
---

# JAXley Actions Skill

This skill empowers you to build, simulate, and optimize biophysical neural network models using JAXley. It leverages JAX for differentiability and high performance across hardware (CPU, GPU, TPU).

## Core Features

-   **Differentiable Simulation:** Enables gradient-based optimization of biophysical parameters through JAX's automatic differentiation.
-   **Hardware Agnostic:** Seamlessly runs on CPU, GPU, and TPU without code modifications.
-   **High Performance:** Achieves speeds comparable to C++ simulators via JAX's `jit` compilation.
-   **Numerical Stability:** Employs backward-Euler solvers for robust simulation of complex neuron models.
-   **Flexibility:** Supports parameter sharing and handles diverse neural components (channels, synapses, pumps).

## API Structure & Key Classes

JAXley's API is structured hierarchically for building neural models:

### Structural Classes
*   `jx.Compartment`: The fundamental unit for simulation.
*   `jx.Branch`: Groups compartments.
*   `jx.Cell`: Groups branches, supporting SWC morphology import.
*   `jx.Network`: Combines cells and synaptic connections.

### Mechanisms
*   `jx.channels.Channel`: Base class for ion channels (e.g., `HH`).
*   `jx.synapses.Synapse`: Base class for synaptic connections (e.g., `IonotropicSynapse`).
*   `jx.pumps.Pump`: For ion dynamics and concentration changes.

## Standard Usage Patterns

A typical JAXley workflow involves:

1.  **Model Definition:** Define cells and their mechanisms (e.g., `cell = jx.Cell(); cell.insert(HH())`).
2.  **Stimulation & Recording:** Set up stimuli and specify which variables to record (e.g., `cell.stimulate()`, `cell.record('v')`).
3.  **Simulation:** Run the simulation using `jx.integrate()`.
4.  **Visualization:** Analyze results using standard plotting libraries (e.g., Matplotlib).

## Advanced Capabilities

*   **Morphology Handling:** Supports `d_lambda` rule for compartment discretization and SWC editing.
*   **NMODL Integration:** Allows importing existing NEURON NMODL channel models.
*   **Gradient-Based Fitting:** `jx.integrate` is JAX-compatible, facilitating parameter fitting using libraries like Optax.
*   **Ion Dynamics:** Includes built-in support for calcium buffering, diffusion, and pumps.

## Best Practices for Gemini CLI Skills

When using JAXley, adhere to these practices:
*   **Modular Design:** Organize channels and synapses into separate modules.
*   **JAX Best Practices:** Utilize `jnp` and avoid side effects within `jit`-compiled code.
*   **Parameter PyTrees:** Leverage JAXley's PyTree parameters for compatibility with JAX's `tree_map`.

**Source URL:** https://jaxley.readthedocs.io/
