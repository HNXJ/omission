---
name: surf-actions
description: Skill for systematic documentation analysis and skill-enrichment using web-crawling patterns.
---

# Surf Actions Skill

This skill guides the process of "surfing" technical documentation to expand and refine our existing skillset ecosystem.

## 1. Surfing Workflow
1. **Identify URLs**: Locate official documentation, advanced tutorials, or API references.
2. **Execute Surf**: Use the `AAE/utils/doc_surfer.py` grammar to structure the extraction.
3. **Analyze**: Identify core patterns, signatures, and biophysical relevance.
4. **Enrich**: Update existing skills (e.g., `jax-actions`) with new sub-sections or create specialized sub-skills.

## 2. Enrichment Rules
- **Modular First**: Extracted code snippets must follow the "Programming Grammar v1.0" (One file per class/function).
- **GPU Native**: Focus on JAX `jit`, `vmap`, and `metal` device optimization.
- **Reference Management**: Always include source URLs in the enriched skill for verification.

## 3. Systematic Grammar Discovery
Documentation surfing must target the extraction of "Programming Grammars"—high-level rules that ensure code speed, stability, and generalization.

### Extraction Protocol
1. **Stability Check**: Identify numerical limits (e.g., float32 vs float64 behavior) and safety checks (NaN/Inf handling).
2. **Standardization**: Identify core data structures (e.g., PyTrees in JAX) to enforce uniform parameter handling.
3. **Speed Identification**: Locate JIT-friendly vs JIT-unfriendly patterns (e.g., control flow, recursion).

## 4. Skill Reorganization
When a skill becomes too large:
- Split into `base-actions` and `advanced-actions`.
- Create `docs` subfolders within skills to store specific library references.
