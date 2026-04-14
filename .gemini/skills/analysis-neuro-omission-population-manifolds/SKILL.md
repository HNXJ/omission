# analysis-neuro-omission-population-manifolds

## Overview
Analyzes neural population manifolds and dimensionality during stimulus omission tasks.

## Usage
Activate via ctivate_skill('analysis-neuro-omission-population-manifolds'). 
Then use specialized functions to project trial-aligned activity into lower-dimensional spaces (PCA/GPFA).

## Inputs
- **session_id**: Identifier for NWB session to analyze.
- **area_list**: Subset of the 11-area hierarchy to include in the manifold.

## Outputs
- **manifold_trajectories**: 3D trajectories for conditions (Stimulus vs Omission).
- **divergence_metrics**: Mahalanobis distance scores comparing state spaces.

## Omission Repo Integration
- **Canonical Module**: codes/scripts/analysis/run-manifold-suite-comprehensive.py
- **Relevance**: Directly supports the Predictive Routing analysis plan by identifying distinct population attractors for omission-related neural dynamics.
