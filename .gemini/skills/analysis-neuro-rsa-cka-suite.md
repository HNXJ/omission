---
name: analysis-neuro-rsa-cka-suite
description: "Implementation of Representational Similarity Analysis (RSA) using RDMs and Centered Kernel Alignment (CKA)."
version: 2.0
---

## ## Context
Standardizes the protocol for comparing neural representations between heterogeneous datasets (e.g., Experimental Spikes vs. LFP, V1 vs PFC, or Model vs Brain).

## ## Rules
- **The Core RSA Workflow**: Feature Extraction -> RDM Construction -> Second-Order Comparison (CKA).
- **Delta-Only Principle**: Focus on relationships (dissimilarity) rather than raw activity levels.
- **RDM Items**: Define 'Items' as [Condition x TimeWindow] pairs. Ensure Item-alignment between modalities.
- **CKA Standard**: Default to **Linear CKA** for second-order similarity. Use because it is invariant to orthogonal transformations and scaling across different dimensionalities (e.g., 1000 neurons vs 128 LFP channels).
- **Cross-Modal Alignment**: When comparing Spiking vs LFP, align items precisely in time. Local modality alignment (within area) should be higher than cross-area alignment.
- **Hierarchical Decay**: Expect representational similarity to decay as functional distance increases (e.g., CKA(V1, V2) > CKA(V1, PFC)).
- **Visualization (2026 Standard)**:
    - **Upsampling**: Use `zsmooth='best'` (bicubic) in Plotly heatmaps for publication-quality gradients.
    - **Aesthetic**: Madelane Golden Dark palette (Black -> Violet -> Gold).
    - **Formats**: Save every figure as both interactive **HTML** and vector **SVG**.
- **Performance**: Use JAX `vmap` or `numpy` vectorization for 11x11 Area-to-Area batch processing to avoid nested loop overhead.
- **Safety**: Never save a similarity matrix that is all 0 or NaN. Issue a warning.

## ## Examples
```python
# CKA Score Calculation
cka_score = linear_cka(feature_matrix_A, feature_matrix_B)
# Plotly Standard for RSA
fig = go.Figure(data=go.Heatmap(z=cka_matrix, zsmooth='best'))
```

# # Keywords:
# RSA, RDM, CKA, Centered Kernel Alignment, Similarity Matrix, Cross-Modal, Spiking-LFP, Cortical Hierarchy, Representational Geometry, CKA Score.
