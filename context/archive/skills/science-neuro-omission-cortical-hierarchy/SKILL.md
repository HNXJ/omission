---
name: science-neuro-omission-cortical-hierarchy
---
# science-neuro-omission-cortical-hierarchy

## Purpose
Maps 11 brain areas into 3 functional tiers and defines directional (FF/FB) connectivity expectations for interpreting Granger causality and latency results.

## Input
| Name | Type | Description |
|------|------|-------------|
| area_labels | list[str] | Anatomical identifiers: V1, V2, V3d, V3a, V4, MT, MST, FST, TEO, FEF, PFC |
| response_latencies | dict[str, float] | Peak activation times (ms) per area for stimulus/omission |
| unit_metadata | DataFrame | Laminar positions (Deep/Sup) and response types (S+/O+) |

## Output
| Name | Type | Description |
|------|------|-------------|
| tier_map | dict[str, str] | Area → Tier assignment (Low/Mid/High) |
| latency_profile | DataFrame | Per-tier timing distributions for Standard vs Omission |
| directional_hypothesis | str | Predicted FB (High→Low) or FF (Low→High) signature |

## Tier Definitions
| Tier | Areas | Stimulus Latency | Role |
|------|-------|-------------------|------|
| 1 (Low) | V1, V2 | ~45ms | Sensory entry |
| 2 (Mid) | V4, MT, MST, TEO, FST | ~65ms | Feature/motion integration |
| 3 (High) | FEF, PFC | >80ms | Predictive model hub |

## Example
```python
TIER_MAP = {'V1': 'Low', 'V2': 'Low', 'V4': 'Mid', 'MT': 'Mid',
            'MST': 'Mid', 'TEO': 'Mid', 'FST': 'Mid',
            'FEF': 'High', 'PFC': 'High'}

# Omission signals propagate High→Low (FB), violating sensory hierarchy
onset_pfc = 25   # ms post-omission
onset_v1 = 120   # ms post-omission
print(f"""[result] PFC leads V1 by {onset_v1 - onset_pfc}ms → FB-dominant""")
```

## Files
- [hierarchy_map.py](file:///D:/drive/omission/src/utils/hierarchy_map.py) — 11-area dictionary
- [analysis-granger-convergence-debug](file:///D:/drive/omission/.gemini/skills/analysis-granger-convergence-debug/SKILL.md) — Granger diagnostics
