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

## Integrated Robust MSCZ Pipeline (`jbiophys`)

For advanced biophysical modeling and hierarchical optimization, use the modular three-part pipeline in `jbiophys`:

### 1. The Constructor Pipeline (`systems.actions.constructor`)
- **Purpose:** Initialization and baseline tuning.
- **Actions:** 
    - `build_hierarchical_mscz()`: Constructs multi-area networks with 3D biophysics.
    - `run_pre_tuning_sweep()`: Verifies physiological baseline (1Hz - 100Hz).
    - **Independent Parameters:** Automatically ensures independent trainable synaptic conductances.

### 2. The Trainer Pipeline (`systems.actions.trainer`)
- **Purpose:** Robust and pausable optimization.
- **Actions:**
    - `run_pausable_training()`: Manages the optimization loop with per-epoch state saving.
    - **Stability Hardwires:** Implements internal voltage/parameter clipping and NaN-to-zero mapping.
    - **Checkups:** Performs a 10-trial pretraining check to validate stability.

### 3. The Visualizer Pipeline (`systems.actions.visualizer`)
- **Purpose:** High-fidelity reporting and visual analysis.
- **Actions:** 
    - `run_visualizer_pipeline()`: Generates a 10-figure interactive report saved as HTML files in the `mscz/figures/` directory.
    - **Interactive Reports:** Outputs include `simulation_summary.html` (Rasters/Spectrograms), `network_3d.html` (3D Architecture), and `biophysical_suite.html` (Vm, LFP, Weight distributions).
    - **Optional SVG:** Can optionally save static SVG versions of the dynamics summary.

```python
# Full Orchestration Example
from systems.actions.constructor import build_hierarchical_mscz
from systems.actions.trainer import run_pausable_training
from systems.actions.visualizer import run_visualizer_pipeline

net, info = build_hierarchical_mscz()
params = run_pausable_training(net, net.get_parameters(), epochs=200)
run_visualizer_pipeline(net, params, info['meta'], output_dir="figures")
```

### 4. The Cortical Column Pipeline (V1, V2, V4)
- **Purpose:** Building and pretraining realistic cortical areas.
- **Actions:**
    - `build_biophysical_cells()`: Generates 200 neurons per area with a 75% EI balance and bimodal Pyr distribution.
    - `apply_cortical_internal_connectivity()`: Wires columns with AMPA, NMDA (10% subset), and GABAa/b.
    - `build_v1_v2_v4_hierarchy()`: Merges areas and establishes hierarchical wiring (Markov 2014 rules).
- **Optimization Strategy:**
    1. Pretrain V1, V2, V4 columns separately to area-specific baselines (e.g., 10Hz, 8Hz).
    2. Merge into a 600-neuron hierarchy.
    3. Jointly optimize for global baseline stability (e.g., 7Hz).

### 5. Multi-Area Hierarchy Construction (V1, V2, V4)
- **Goal:** Connect multiple 200-neuron columns using anatomical rules.
- **Wiring Logic (Markov 2014):**
    - **FF:** Connect Superficial Pyramidal cells (L2/3) to target area L4/Soma.
    - **FB:** Connect Deep Pyramidal cells (L5/6) to target area L1/2 distal dendrites.
- **Synaptic Diversity:**
    - Include `GradedNMDA` with magnesium block for excitatory recurrence.
    - **Constraint:** NMDA output is restricted to a random 10% subset of excitatory neurons.

### 6. Memory-Efficient Large Network Optimization
When optimizing large networks (e.g., >200 neurons) for long durations (e.g., 10,000ms), use these patterns to prevent RAM exhaustion:

- **Neuron Subset Recording**: Instead of recording voltage from all neurons for the loss function, record from a representative subset (e.g., 100 neurons).
  ```python
  subset_indices = np.random.choice(num_neurons, size=100, replace=False).tolist()
  network.cell(subset_indices).branch(0).loc(0.0).record('v')
  ```
- **Temporal Decimation for Visualization**: For long simulations, downsample the voltage traces (e.g., 10x decimation) before generating interactive HTML reports to reduce figure size and RAM usage.
- **Gradient Checkpointing**: Trade computation for memory during the backward pass by wrapping the simulation logic in `jax.checkpoint`. (Note: Ensure JAXley compatibility with internal tracers).

## Best Practices for Gemini CLI Skills

When using JAXley, adhere to these practices:
*   **Modular Design:** Organize channels and synapses into separate modules.
*   **JAX Best Practices:** Utilize `jnp` and avoid side effects within `jit`-compiled code.
*   **Parameter PyTrees:** Leverage JAXley's PyTree parameters for compatibility with JAX's `tree_map`.

**Source URL:** https://jaxley.readthedocs.io/
