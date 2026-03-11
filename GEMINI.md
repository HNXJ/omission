## Gemini General Operating Mandates

- **Workspace**: Default root is `/Users/hamednejat/workspace`.
- **Navigation**: Provide an 8-word summary when entering any directory.
- **Workflow (AAE-First)**: Every new Python function or class MUST be modularized into the `AAE/` repository and pushed to GitHub immediately.
- **Execution**: All 'deep' tasks (GSDR training, NWB analysis sweeps, Wan-video gen) MUST be executed as background processes (`is_background=True`).

## Current Objectives (Active Working Set)
- **Objective mscz**: Complete the two-area (Low -> High Cortex) parameter sweep using `IPnoise`. Target: 5-15Hz AFR in high-order column.
- **Objective oxm**: Finalize cortical column map by cross-validating `vFLIP2` crossover points with MUAe sequence responses.
- **Objective mllm**: Perform multi-agent scoring of the ScZ literature batch using the **ScZ-40 Glossary**.
- **Objective GSDR01 Publication**: Finalize PLOS ONE rebuttal and biological comparison figures for 0818/0825.

## Programming Grammar (v1.0)
Rules for speed, stability, and generalization:
1. **Modular Granularity**: One file = One primary function or class. Use `__init__.py` for package-level exports.
2. **Stability Barrier**: All `float32` state updates must include: `new_val = jnp.where(jnp.isnan(new_val) | jnp.isinf(new_val), old_val, new_val)`.
3. **Pure JAX Logic**: No `numpy` calls inside simulation loops or `jit` segments. Use `jnp` and `jax.random` exclusively.
4. **PyTree Standard**: Parameters must be handled as PyTrees. Use `jax.tree.map` for scaling and updates.
5. **Auto-Seed**: All stochastic functions must default to `seed=None` and generate random seeds internally unless explicitly overridden.

**Refer to `/Users/hamednejat/.gemini/VMEMORY.md` for architectural details, project history, and research roadmap.**
