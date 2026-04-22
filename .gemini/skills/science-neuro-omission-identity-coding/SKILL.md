---
name: science-neuro-omission-identity-coding
description: Decoding framework for characterizing stimulus identity (A vs. B) and category (Standard vs. Omission) across the cortical hierarchy.
---
# skill: science-neuro-omission-identity-coding

## When to Use
Use this skill when performing population decoding or information-theoretic analysis of stimulus features. It is mandatory for:
- Calculating Percent Explained Variance (PEV) for stimulus identity ($A=45^\circ$, $B=135^\circ$).
- Implementing "Ternary Decoding" (A vs. B vs. Random) to assess categorical abstraction.
- Measuring the decay of identity information across the 531ms delay and omission windows.
- Comparing identity fidelity between Deep and Superficial layers (f034).

## What is Input
- **Single-Unit PSTHs**: Trial-aligned firing rates binned at high resolution (e.g., 10ms).
- **Trial Labels**: Condition metadata (Stimulus Identity, Sequence Position, Trial Type).
- **Laminar Labels**: Channel-to-layer mapping for depth-resolved decoding.

## What is Output
- **Decoding Accuracy Curves**: Time-resolved classification performance (e.g., SVM scores).
- **PEV Matrices**: Percentage of total variance explained by stimulus identity.
- **Identity Persistence**: The duration for which identity information remains above chance (33% for ternary, 50% for binary).

## Algorithm / Methodology
1. **Classifier Training**: Train a linear SVM on the population vector $X$ (Neurons $\times$ Time) using stimulus identity as the label $y$.
2. **Cross-Validation**: Use 5-fold or Leave-One-Out validation to ensure robust accuracy reporting.
3. **PEV Calculation**: Perform a sliding-window ANOVA to extract the variance explained by the identity factor.
4. **Hierarchy Comparison**: Quantify how abstract identity coding becomes more robust as signals move from V1 $\to$ V4 $\to$ PFC.
5. **Laminar Split**: Assess if feedback-related identity signals are stronger in Deep layers during the omission window.

## Placeholder Example
```python
from sklearn.svm import LinearSVC
import numpy as np

def run_sliding_decoder(data, labels, win_size=5):
    """
    Decodes stimulus identity using a sliding window.
    data: (trials, neurons, time)
    labels: (trials,)
    """
    clf = LinearSVC(dual=False)
    # Sliding window classification logic
    # Returns accuracy curve over time
    return accuracy_time_series
```

## Relevant Context / Files
- [neuro-analysis](file:///D:/drive/omission/.gemini/skills/neuro-analysis/skill.md) — For the fundamental population vector construction.
- [src/decoding/ternary_classifier.py](file:///D:/drive/omission/src/decoding/ternary_classifier.py) — The SVN implementation.
