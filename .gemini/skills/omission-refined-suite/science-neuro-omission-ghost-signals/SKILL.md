# Neural Ghost: Contextual Persistence

The 'Neural Ghost' refers to the contextual persistence of neuronal activity during the physical absence of a stimulus. In our sequential task, the screen is identical (gray) during delays and omissions. However, the brain maintains a representation of the expected stimulus (e.g., Identity A or B). This top-down prior generates activity in V1/PFC even when input is null.

Mechanism:
Top-down feedback from high-order areas (PFC/FEF) targets the deep layers of lower visual areas (V1/V2). During an omission, these priors fail to be 'canceled' by bottom-up sensory input, resulting in a residual or 'ghost' signal. This activity is not merely noise; it carries information about the identity of the expected but missing stimulus.

Scientific Context:
Studies have shown that V1 can represent the identity of omitted stimuli, suggesting that primary sensory cortex serves as a 'blackboard' for high-level expectations. In our dataset, we observe that the population trajectory in PCA space for an omission (X) often mimics the initial phase of the expected stimulus trajectory (A or B) before diverging into a surprise state.

Technical Implementation:
```python
# Analyzing persistence in V1 units during omission windows
import numpy as np
def detect_ghost_signal(psth_omit, psth_stim, window=(0, 500)):
    # Correlation between omission PSTH and stimulus PSTH
    corr = np.corrcoef(psth_omit[window[0]:window[1]], 
                       psth_stim[window[0]:window[1]])[0, 1]
    return corr

# High correlation indicates strong contextual persistence (The Ghost)
```

References:
1. Muckli, L., et al. (2015). Contextual Feedback to Superficial Layers of V1. Current Biology.
2. Kok, P., et al. (2012). Less Is More: Expectation Sharpens Representations in the Visual Cortex. Neuron.
3. Ekman, M., et al. (2017). Time-compressed preplay of anticipated events in human primary visual cortex. Nature Communications.
