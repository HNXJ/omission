# Jaxley Advanced Documentation (Enriched March 2026)

Advanced patterns for large-scale differentiable biophysics.

## 1. Modular Connectivity
- **`sparse_connect`**: The standard for large microcircuits. Signature: `sparse_connect(pre, post, synapse_type, p=prob)`.
- **`fully_connect`**: Automatic indexing for all-to-all projections. **Lesson**: Prevents the "Length mismatch" error in `.edges` DataFrames.

## 2. Trainable Parameters
- **`make_trainable`**: Must be called on the high-level `jx.Network` object. 
- **Parameter PyTree**: `net.get_parameters()` returns the exact structure required by `optax` optimizers. 
- **Dictionary Access**: Access synaptic view parameters via `net.edges.gAMPA` or similar attribute accessors on the view.

## 3. Simulation & Integration
- **`jx.integrate`**: The primary solver. Pass `params=...` to override defaults with optimized weights.
- **Numerical Stability**: 
    - **Voltage**: Uses Implicit Euler.
    - **Gating**: Uses Exponential Euler.
    - **Stability Barrier**: Maintain biological validity using `jnp.where` checks within custom channel `update_states` methods.

## 4. Multi-Compartment Management
- **Parents**: When building cells with more than 1 compartment, always specify the `parents` list to define the cable topology.
- **Views**: Use `.branch(i).loc(x)` to target specific synaptic locations (e.g., Soma at 0.5, Distal Dendrite at 1.0).
