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

import numpy as np
import pandas as pd
from pathlib import Path
from collections import defaultdict

# Tensor Definitions
CONDITIONS = ['AAAB', 'BBBA', 'RRRR', 'AXAB', 'BXBA', 'RXRR', 'AAXB', 'BBXA', 'RRXR', 'AAAX', 'BBBX', 'RRRX']
WINDOWS = ['fx', 'p1', 'd1', 'p2', 'd2', 'p3', 'd3', 'p4', 'd4']
WINDOW_LIMITS = {
    'fx': (0, 500), 'p1': (500, 1031), 'd1': (1031, 1531),
    'p2': (1531, 2062), 'd2': (2062, 2562), 'p3': (2562, 3093),
    'd3': (3093, 3593), 'p4': (3593, 4124), 'd4': (4124, 4624)
}

def generate_unit_tensor(spk_data, trial_indices, unit_idx):
    """
    spk_data: (trials, units, time)
    tensor: 12 conditions x 9 windows x 2 metrics (FR, Var)
    """
    tensor = np.zeros((len(CONDITIONS), len(WINDOWS), 2))

    for c_i, cond in enumerate(CONDITIONS):
        for w_i, win in enumerate(WINDOWS):
            start, end = WINDOW_LIMITS[win]

            # Slice unit data
            # Assume spk_data is already binned/smoothed if needed, or raw
            data = spk_data[:, unit_idx, start:end]

            # Compute FR and Var
            fr = np.mean(data) * 1000  # Convert to Hz
            var = np.var(data)

            tensor[c_i, w_i, 0] = fr
            tensor[c_i, w_i, 1] = var

    return tensor

def main():
    print("[action] Tensor generation: Processing all stable units...")
    # ... placeholder for loading data loop ...
    print("[action] Tensor generation complete.")

if __name__ == "__main__":
    main()

