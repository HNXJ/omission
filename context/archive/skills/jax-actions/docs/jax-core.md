# JAX Core Documentation (Enriched March 2026)

Foundational rules for high-performance biophysical modeling in JAX.

## 1. Core Transformations
- **`jax.jit`**: Compiles Python functions into XLA for CPU/GPU/Metal speed. **Rule**: Avoid Python side-effects (like `print` or `list.append`) inside JIT.
- **`jax.vmap`**: Vectorizes functions. Use this to simulate multiple trials or diverse parameter sets in a single parallel call.
- **`jax.grad`**: Computes gradients. Use `jax.value_and_grad` to get both the loss and the gradients simultaneously for GSDR/AGSDR.

## 2. Control Flow (Stable Grammar)
- **Problem**: Python `if` and `for` loops are often unrolled or cause recompilation issues in JIT.
- **Solution**: 
    - Use `jax.lax.cond` for conditional logic (e.g., triggering a reset).
    - Use `jax.lax.scan` for time-stepping loops. This keeps the loop compiled and significantly reduces memory usage.

## 3. PyTree Standard
- Every JAX object (Network parameters, Optimizer states) is a **PyTree**.
- **Transformation**: Use `jax.tree.map(lambda x: ..., tree)` to apply operations across all parameters (e.g., synaptic scaling).
- **Structure**: Always ensure your custom state classes (like `GSDRState`) are registered as PyTrees using `@flax.struct.dataclass` or `jax.tree_util.register_pytree_node_class`.
