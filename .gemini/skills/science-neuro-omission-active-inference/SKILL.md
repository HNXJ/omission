---
name: science-neuro-omission-active-inference
description: Theoretical framework for interpreting visual omissions through the lens of Active Inference and Free-Energy minimization.
---
# skill: science-neuro-omission-active-inference

## When to Use
Use this skill when interpreting neural results in the context of predictive coding theory. It is mandatory for:
- Mapping neural transients to variational free energy (F) minimization.
- Calculating information-theoretic surprisal ($I(o) = -\log p(o)$) for different trial types.
- Analyzing top-down prediction updates ($q(s)$) during AXAB sequences.
- Dissociating complexity vs. accuracy components of the free-energy bound.

## What is Input
- **Trial Probabilities**: The experimental block design (70% standard, 10% omission, etc.).
- **Response Latencies**: Timing of neural peaks across the hierarchy (PFC vs. V1).
- **Surprisal Values**: Calculated bits of information per event type.

## What is Output
- **Theoretical Interpretations**: Justifications for why high-order areas (PFC/FEF) lead sensory areas during omissions.
- **Surprisal Reports**: Quantitative comparisons of standard vs. rare event information content.
- **Model Predictions**: Hypothesized changes in synaptic gain or precision based on trial history.

## Algorithm / Methodology
1. **Generative Modeling**: The brain maintains an internal state $p(s|o)$ predicting the next stimulus in a sequence (e.g., AAAB).
2. **Prediction Error**: Omissions (AXAB) create a mismatch between expectation and the gray-screen input.
3. **Free-Energy Minimization**: The resulting transient signal is the manifestation of the brain updating its posterior $q(s)$ to account for the surprise.
4. **Information Fidelity**: Surprisal magnitude is directly proportional to the statistical rarity of the event ($10\% \implies 3.32$ bits; $70\% \implies 0.51$ bits).

## Placeholder Example
```python
import numpy as np

def get_surprisal_bits(p):
    """Calculates surprisal in bits for an event with probability p."""
    return -np.log2(p)

# Comparison: Frequent Standard vs. Rare Omission
print(f"Standard (70%): {get_surprisal_bits(0.7):.2f} bits")
print(f"Omission (10%): {get_surprisal_bits(0.1):.2f} bits")
```

## Relevant Context / Files
- [predictive-routing](file:///D:/drive/omission/.gemini/skills/predictive-routing/skill.md) — For the LFP manifestation of these signals.
- [src/math/information_theory.py](file:///D:/drive/omission/src/math/information_theory.py) — Canonical surprisal and entropy implementations.
