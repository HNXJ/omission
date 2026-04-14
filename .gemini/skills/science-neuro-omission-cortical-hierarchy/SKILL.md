---
name: science-neuro-omission-cortical-hierarchy
description: "Omission analysis skill focusing on science neuro omission cortical hierarchy."
---

# 11-Area Cortical Hierarchy Map

Our research utilizes a 11-area map across three functional tiers to track the propagation of visual and surprise information. The hierarchy is defined by anatomical connectivity and functional response latencies.

Hierarchy Tiers:
1. Low-Order Visual: V1, V2. Primary entry points for retinal input.
2. Mid-Order Visual: V4, MT, MST, TEO, FST. Responsible for feature integration and motion processing.
3. High-Order / Executive: FEF, PFC (dlPFC/vlPFC). Hubs for internal models, attention, and decision making.

Information Propagation:
During stimulus presentations, activity flows bottom-up (V1 -> V4 -> PFC). However, during omissions, the surprise signal often appears first in High-Order areas or Mid-Order areas like MT/FEF before being detected in V1. This suggests that the internal model residing in the frontal-parietal network detects the violation of expectation and sends feedback to the sensory cortex.

Functional Tier Definitions:
- Low-Tier: Latencies < 50ms for stimulus onset. Minimal omission response.
- Mid-Tier: Latencies 50-80ms. Significant identity encoding (A vs B).
- High-Tier: Latencies > 80ms for stimulus, but often < 40ms for omission-specific transients (surprise).

Technical Mapping:
```python
area_tiers = {
    'V1': 'Low', 'V2': 'Low',
    'V4': 'Mid', 'MT': 'Mid', 'MST': 'Mid', 
    'TEO': 'Mid', 'FST': 'Mid',
    'FEF': 'High', 'PFC': 'High'
}

def get_tier_latency(area):
    # Example logic based on project data
    if area_tiers[area] == 'Low': return 45.0
    if area_tiers[area] == 'Mid': return 65.0
    return 85.0
```

References:
1. Felleman, D. J., & Van Essen, D. C. (1991). Distributed hierarchical processing in the primate cerebral cortex. Cerebral Cortex.
2. Markov, N. T., et al. (2014). A Weighted and Directed Interareal Connectivity Matrix for Macaque Cerebral Cortex. Cerebral Cortex.
