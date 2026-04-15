#!/usr/bin/env python3
"""
Omission Tensor Generator (12x9x2)
Computes firing rate and variance tensor per unit.
"""
import numpy as np
import pandas as pd
from pathlib import Path

# Tensor Dimensions
# 12 conditions (RRRR, RXRR, RRXR, RRRX * 3 permutations)
# 9 windows (fx, p1, d1, p2, d2, p3, d3, p4, d4)
# 2 metrics (Firing Rate, Variance)

def generate_unit_tensor(spk_data, trial_indices, window_limits):
    """
    spk_data: (trials, time)
    trial_indices: list of trial indices for each condition/window
    window_limits: dict mapping label to (start, end) indices
    """
    n_cond = 12
    n_win = 9
    tensor = np.zeros((n_cond, n_win, 2))
    
    # Implementation logic for aggregation
    # ...
    return tensor

def main():
    print("[action] Tensor generation initialized.")
    # Load stable unit metadata
    # Load session data
    # Loop over units -> generate 12x9x2 tensor -> store
    pass

if __name__ == "__main__":
    main()
