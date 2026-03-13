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

## Advanced Parameter Management

### Independent vs. Shared Parameters

By default, JAXley parameters can be either shared globally across a network or assigned individually to each component.

- **Global Sharing:** Calling `net.make_trainable("param")` on the entire network often results in a single shared parameter for all instances of that component.
- **Independent Parameters:** To make every instance (e.g., every synapse) independently trainable, use `select()` before `make_trainable()`:
  ```python
  # Every synapse has its own trainable conductance
  net.select(edges="all").make_trainable("gAMPA")
  ```
- **Custom Sharing (Group-based):** Use the `controlled_by_param` column in the `.edges` or `.nodes` DataFrames to group components that should share a parameter value.
  ```python
  # Share conductances based on presynaptic cell index
  net.copy_node_property_to_edges("global_cell_index")
  net.edges["controlled_by_param"] = net.edges["pre_global_cell_index"]
  net.select(edges="all").make_trainable("gAMPA")
  ```

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

## Standardized Robust Pipeline (`jbiophys`)

For complex biophysical models, use the `robust_pipeline` in `jbiophys` to automate the following 7-step process:

1. **Initialize Network:** Builds the `jx.Network` and enforces parameter independence (e.g., individual synapse conductances).
2. **Plausibility Sweep:** A coarse loop to find initial parameters yielding stable firing rates (1Hz - 100Hz).
3. **Training Setup:** Configures the loss function with metabolic cost (quadratic parameter penalty) and stability hardwires.
4. **Pretraining Checkup:** A 10-epoch dry run to validate learning rate and update stability.
5. **Stability Hardwires:** Internal voltage clipping ([-100, 100]mV) and NaN-to-zero mapping.
6. **64-bit precision:** Automatic or forced switch to `jax_enable_x64` for numerical robustness.
7. **Visualization:** Generates a standardized suite of 7-8 figures (rasters, Vm, Kappa).

```python
from systems.actions.robust_pipeline import execute_robust_training
execute_robust_training(net, epochs=200, lr=1e-3, target_fr=15.0, force_x64=True)
```

## Best Practices for Gemini CLI Skills

When using JAXley, adhere to these practices:
*   **Modular Design:** Organize channels and synapses into separate modules.
*   **JAX Best Practices:** Utilize `jnp` and avoid side effects within `jit`-compiled code.
*   **Parameter PyTrees:** Leverage JAXley's PyTree parameters for compatibility with JAX's `tree_map`.

**Source URL:** https://jaxley.readthedocs.io/
