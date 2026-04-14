---
name: science-neuro-omission-active-inference
description: "Omission analysis skill focusing on science neuro omission active inference."
---

# Active Inference in Visual Omission

Active Inference, as formulated by Karl Friston (2010, DOI: 10.1038/nrn2787), posits that the brain is a generative model that minimizes variational free energy through action and perception. In the context of visual omissions, the brain does not merely respond to stimulus absence; it actively predicts stimulus presence based on learned temporal sequences (e.g., AAAB). When a stimulus is omitted (e.g., AXAB), a prediction error is generated because the internal generative model's expectation (p_theta) diverges from the sensory input (gray screen).

The variational free energy (F) can be decomposed into complexity and accuracy:
F = D_KL[q(s)||p(s|o)] - log p(o).
During an omission, accuracy is low because the expected stimulus is missing, driving the update of the posterior q(s). This update manifests as a transient surprise signal, often observed in high-order areas like the PFC and FEF before Sensory-Driven areas.

Scientific Context:
Surprisal theory suggests that the magnitude of the neural response is proportional to the information content of the event: I(o) = -log p(o). In our 70/10/10/10 block design, an omission has significantly higher surprisal than a standard presentation, triggering a cascade of hierarchical updates.

Technical Implementation:
```python
def calculate_surprisal(probability):
    import numpy as np
    return -np.log2(probability)

# Surprisal for frequent (70%) vs rare (10%) events
freq_s = calculate_surprisal(0.7)
rare_s = calculate_surprisal(0.1)
print(f'Surprisal Delta: {rare_s - freq_s:.2f} bits')
```

References:
1. Friston, K. (2010). The free-energy principle: a rough guide to the brain? Nature Reviews Neuroscience.
2. Bastos, A. M., et al. (2012). Canonical Microcircuits for Predictive Coding. Neuron.
3. Rao, R. P., & Ballard, D. H. (1999). Predictive coding in the visual cortex. Nature Neuroscience.
