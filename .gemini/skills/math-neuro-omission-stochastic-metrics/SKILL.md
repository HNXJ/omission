---
name: math-neuro-omission-stochastic-metrics
description: Quantitative formalisms for neural variability and information theory, including Fano Factor (FF), Mutual Information (MI), and KL-Divergence.
---
# skill: math-neuro-omission-stochastic-metrics

## When to Use
Use this skill when analyzing the information-theoretic properties of neural signals. It is mandatory for:
- Quantifying spike count variability using the Fano Factor (FF).
- Measuring stimulus-related information content via Mutual Information (MI).
- Assessing the "Surprise Magnitude" using KL-Divergence between predicted and actual states.
- Testing the hypothesis that surprise "quenches" neural variability.

## What is Input
- **Spike Counts**: Discrete counts per trial for specific bins (e.g., 50ms).
- **Probability Distributions**: $P(X)$ and $Q(X)$ representing stimulus priors and neural posteriors.
- **Ensemble States**: Population vectors for multi-unit information estimates.

## What is Output
- **Variability Indices**: Fano Factor curves showing temporal changes in regularity.
- **Information Bitrates**: Bits per second (or bits per spike) for specific areas.
- **Surprise Metrics**: KL-Divergence values indicating the "Information Gain" during omissions.

## Algorithm / Methodology
1. **Fano Factor (FF)**: Calculated as $FF = \sigma^2 / \mu$. $FF < 1$ indicates regularity; $FF > 1$ indicates burstiness. We look for a decrease in FF following O+ events.
2. **Mutual Information (MI)**: $MI(X; Y) = H(X) - H(X|Y)$, measuring how much stimulus uncertainty is reduced by neural response $Y$.
3. **KL-Divergence**: $D_{KL}(P||Q) = \sum P(i) \log(P(i)/Q(i))$. Measures the "Distance" between expected and observed neural distributions.
4. **Variability Quenching**: A key prediction of our project where stimulus-driven input (or surprise) collapses the high-variance spontaneous state into a low-variance task state.

## Placeholder Example
```python
import numpy as np

def calculate_fano_factor(spike_counts):
    # spike_counts: (trials, ) array of counts in a window
    return np.var(spike_counts) / (np.mean(spike_counts) + 1e-12)

def calculate_kl_div(p, q):
    # p, q must be normalized distributions
    p = np.array(p) + 1e-12
    q = np.array(q) + 1e-12
    return np.sum(p * np.log2(p / q))
```

## Relevant Context / Files
- [neuro-analysis](file:///D:/drive/omission/.gemini/skills/neuro-analysis/skill.md) — For downstream population decoding.
- [src/math/information.py](file:///D:/drive/omission/src/math/information.py) — Validated implementations of Shannon metrics.
