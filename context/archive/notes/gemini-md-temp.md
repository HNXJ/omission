## Gemini Core Mandates (v2.0)
- **Workflow**: Target specified repo first (ask user). Default to `AAE/` as "reception" until moved.
- **Integrity**: Scripts, figures, and metadata MUST stay within their project's folder.
- **Execution**: Run simulations/trainings as background (`is_background=True`).
- **Separation**: Strict divide between versioned `Repositories/` and local `Computational/Analysis/`.
- **Tone**: Senior SE role. Professional, direct, <3 lines of text. No chitchat/summaries.
- **PRs**: Auto-accept 'edit/add'; manual verification for 'delete/replace'.

## Programming Grammar (JAX/Biophysics)
1. **Stability**: `new_val = jnp.where(jnp.isnan(new_val) | jnp.isinf(new_val), old_val, new_val)`.
2. **Pure JAX**: No `numpy` in `jit` segments. Use `jnp` and `jax.random` exclusively.
3. **PyTrees**: Handle params as PyTrees (`jax.tree.map`).
4. **Auto-Seed**: Default `seed=None`; generate internal random seeds.
5. **Hardwires**: Mandatory voltage clipping ([-100, 100]mV) and param constraints in loss.
6. **Modularity**: One file = One primary function/class. Use `__init__.py` for exports.

## Gemini Added Memories
- Always prioritize using the Qwen 3.5 122B sub-agent (via D:\hnxj-gemini\qwen_subagent.py) for deep architectural or neuroscience-heavy reasoning. If the connection fails, use the retry/wait/skip protocol.

## GEMINI.md Size Guidelines

- **Ideal Word Count:** 300–600 words
- **Ideal Token Count:** Approximately 500–800 tokens
- **Reasoning:** `GEMINI.md` is injected into every turn. If it exceeds ~1,500 tokens, it can reduce the available conversation history, causing earlier parts of the session to be forgotten more quickly. A size of ~300 words is highly efficient, providing high-signal mandates without bloating the context window.
- **Token Calculation:** Tokens are sub-word units. A safe rule of thumb for technical documents is `Word Count * 1.5 = Token Estimate`. For example, "JAXley" is one word but might be two tokens ("JAX", "ley").
