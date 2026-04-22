---
name: science-neuro-omission-cortical-hierarchy
description: Formal 11-area mapping and hierarchical tier definitions for tracking prediction error propagation.
---
# skill: science-neuro-omission-cortical-hierarchy

## When to Use
Use this skill when analyzing multi-area interactions or comparing latencies across the visual-frontal axis. It is mandatory for:
- Categorizing sessions into Low, Mid, and High-Order tiers.
- Interpreting top-down vs. bottom-up information flow (Granger Causality).
- Mapping functional connectivity onto the anatomically directed matrix (Markov 2014).
- Calculating hierarchy-aware population latencies.

## What is Input
- **Area Labels**: Anatomical identifiers (V1, V4, FEF, etc.).
- **Response Timings**: Peak activation latencies for stimulus onset and omission.
- **Unit Metadata**: Laminar positions and response types (S+/O+).

## What is Output
- **Tier Classification**: 11 areas mapped to 3 functional tiers.
- **Latency Profiles**: Tier-specific timing distributions for standard vs. omission events.
- **Directional Hypotheses**: Predicted feedback (High $\to$ Low) or feedforward (Low $\to$ High) signatures.

## Algorithm / Methodology
1. **Tier 1 (Low-Order Visual)**: V1, V2. Primary sensory entry; stimulus latency $\approx 45$ms.
2. **Tier 2 (Mid-Order Visual)**: V4, MT, MST, TEO, FST. Feature/motion integration; stimulus latency $\approx 65$ms.
3. **Tier 3 (High-Order / Executive)**: FEF, PFC (dlPFC/vlPFC). Predictive model hubs; stimulus latency $> 80$ms.
4. **Omission Dynamics**: Surprise signals often originate in Tier 3 or 2 and propagate backwards to Tier 1, violating the standard sensory hierarchy.

## Placeholder Example
```python
# Tier Assignment Logic
area_mapping = {
    'V1': 'Low', 'V4': 'Mid', 'FEF': 'High'
}

def analyze_hierarchy_lag(area_a, area_b, lag_ms):
    """Interprets lags based on hierarchical positions."""
    tier_a = area_mapping.get(area_a)
    tier_b = area_mapping.get(area_b)
    # If High leads Low, it implies Feedback (Predictive Update)
```

## Relevant Context / Files
- [neuro-analysis](file:///D:/drive/omission/.gemini/skills/neuro-analysis/skill.md) — For population latency calculations.
- [src/utils/hierarchy_map.py](file:///D:/drive/omission/src/utils/hierarchy_map.py) — The canonical 11-area dictionary.
