"""
lfp_stats.py
Statistical testing for LFP Omission (Steps 12-13).
"""
import numpy as np
from scipy import stats

def cluster_permutation_1d(data_a, data_b, n_perm=1000):
    """
    1D Cluster-based permutation test (Step 12).
    data: (trials, time)
    """
    # Placeholder for cluster implementation
    t_obs, p_val = stats.ttest_ind(data_a, data_b, axis=0)
    return t_obs, p_val

def compare_tiers(tier_a_data, tier_b_data):
    """
    Rank-sum comparison between hierarchy tiers (Step 13).
    """
    res = stats.ranksums(tier_a_data, tier_b_data)
    return res.pvalue
