# Jaxley Connectivity Grammar

Documentation of lessons learned regarding indexing and broadcasting during microcircuit construction.

## 1. `fully_connect` vs `connect`
- **Error**: `ValueError: Length of values (8) does not match length of index (10)`.
- **Lesson**: When connecting populations of different sizes (e.g., 8 Excitatory to 10 All-cells), `jx.connect` requires manual index broadcasting.
- **Protocol**: Prefer `jaxley.connect.fully_connect(pre, post, synapse)` for all-to-all projections. It handles the indexing internally, preventing shape mismatches in the `.edges` DataFrame.

## 2. Parameter Registration
- **Discovery**: Synaptic parameters like `gAMPA` are NOT trainable by default.
- **Protocol**: Explicitly call `net.make_trainable("param_name")` on the top-level `Network` object. Calling it on `.edges` directly (the DataFrame) will fail.

## 3. Position vs. Keyword Arguments
- **Signature Note**: In `sparse_connect`, the `synapse_type` must be passed as a **positional** argument, while `p` (probability) is a keyword argument.
  - `sparse_connect(pre, post, GradedAMPA(), p=0.5)` ✅
  - `sparse_connect(pre, post, p=0.5, synapse=GradedAMPA())` ❌
