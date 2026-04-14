"""
lfp_stats.py
Statistical testing for LFP Omission analysis (15-step pipeline).
Steps 12 + 13 implementations.
"""
from __future__ import annotations
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from scipy import stats


def mean_sem(x: np.ndarray, axis: int = 0) -> Tuple[np.ndarray, np.ndarray]:
    """
    NaN-safe mean and SEM along specified axis.
    Denominator = number of non-NaN observations per position.

    Parameters
    ----------
    x    : np.ndarray — input array (any shape)
    axis : int        — axis along which to compute

    Returns
    -------
    mean, sem  — both same shape as x with axis reduced
    """
    if x.size == 0:
        return np.array([]), np.array([])
    mean = np.nanmean(x, axis=axis)
    n    = np.sum(~np.isnan(x), axis=axis)
    sem  = np.nanstd(x, axis=axis) / np.sqrt(np.maximum(1, n))
    return mean, sem


def run_cluster_permutation(
    x: np.ndarray,
    y: np.ndarray,
    n_perm: int = 1000,
    threshold_p: float = 0.05,
    axis: int = -1,
) -> Dict[str, Any]:
    """
    1D cluster-based permutation test. Step 12 implementation.
    Tests H0: x and y have the same distribution at each time/freq point.

    Parameters
    ----------
    x, y         : np.ndarray, shape (..., n_times) — two conditions
    n_perm       : int   — number of permutations. Default 1000.
    threshold_p  : float — p-value threshold for initial cluster detection.
    axis         : int   — axis along which to run the test (-1 = last).

    Returns
    -------
    dict with keys:
        'mask'        : bool array, shape (n_times,) — True where cluster survives
        'cluster_p'   : float array, shape (n_clusters,)
        'tstat'       : float array, shape (n_times,) — t-statistic per point
        'n_clusters'  : int
        'n_perm'      : int
    """
    if x.size == 0 or y.size == 0:
        return {"mask": None, "cluster_p": np.array([]), "tstat": np.array([]),
                "n_clusters": 0, "n_perm": n_perm}

    # Move test axis to last
    x = np.moveaxis(x, axis, -1)
    y = np.moveaxis(y, axis, -1)
    n_times = x.shape[-1]

    # Per-point t-test
    tstat, pvals = stats.ttest_ind(x.reshape(-1, n_times),
                                   y.reshape(-1, n_times), axis=0)
    threshold_t = stats.t.ppf(1 - threshold_p / 2, df=x.shape[0] + y.shape[0] - 2)

    def _find_clusters(t_arr, thresh):
        """Returns list of (start, stop) index pairs for clusters above thresh."""
        above = np.abs(t_arr) >= thresh
        clusters = []
        in_c, start = False, 0
        for i, a in enumerate(above):
            if a and not in_c:
                start = i; in_c = True
            elif not a and in_c:
                clusters.append((start, i)); in_c = False
        if in_c:
            clusters.append((start, len(above)))
        return clusters

    def _cluster_mass(t_arr, clusters):
        return [np.sum(np.abs(t_arr[s:e])) for s, e in clusters]

    observed_clusters = _find_clusters(tstat, threshold_t)
    if not observed_clusters:
        return {"mask": np.zeros(n_times, dtype=bool), "cluster_p": np.array([]),
                "tstat": tstat, "n_clusters": 0, "n_perm": n_perm}

    observed_mass = _cluster_mass(tstat, observed_clusters)

    # Null distribution via permutation
    all_data = np.concatenate([x.reshape(-1, n_times), y.reshape(-1, n_times)], axis=0)
    nx = x.reshape(-1, n_times).shape[0]
    null_max_mass = np.zeros(n_perm)
    rng = np.random.default_rng(42)
    for i in range(n_perm):
        perm = rng.permutation(len(all_data))
        xp = all_data[perm[:nx]]
        yp = all_data[perm[nx:]]
        tp, _ = stats.ttest_ind(xp, yp, axis=0)
        nc = _find_clusters(tp, threshold_t)
        if nc:
            null_max_mass[i] = max(_cluster_mass(tp, nc))

    # Cluster p-values
    cluster_ps = np.array([
        np.mean(null_max_mass >= m) for m in observed_mass
    ])
    mask = np.zeros(n_times, dtype=bool)
    for (s, e), p in zip(observed_clusters, cluster_ps):
        if p < threshold_p:
            mask[s:e] = True

    return {
        "mask": mask,
        "cluster_p": cluster_ps,
        "tstat": tstat,
        "n_clusters": len(observed_clusters),
        "n_perm": n_perm,
    }


def run_tier_rank_sum(
    measures_by_area: Dict[str, np.ndarray],
    tier_a: List[str],
    tier_b: List[str],
) -> Dict[str, Any]:
    """
    Wilcoxon rank-sum test between two cortical tiers (Step 13).
    Tests whether tier_a and tier_b show different spectral measures.

    Parameters
    ----------
    measures_by_area : dict {area: array(n_values)}
    tier_a, tier_b   : list of area names defining the two tiers

    Returns
    -------
    dict: 'statistic', 'pvalue', 'tier_a_mean', 'tier_b_mean', 'effect_size'
    """
    vals_a = np.concatenate([measures_by_area[a].ravel()
                             for a in tier_a if a in measures_by_area])
    vals_b = np.concatenate([measures_by_area[b].ravel()
                             for b in tier_b if b in measures_by_area])
    if vals_a.size == 0 or vals_b.size == 0:
        return {"statistic": np.nan, "pvalue": np.nan,
                "tier_a_mean": np.nan, "tier_b_mean": np.nan,
                "effect_size": np.nan}
    stat, p = stats.ranksums(vals_a, vals_b)
    # rank-biserial correlation as effect size
    n1, n2  = len(vals_a), len(vals_b)
    r_effect = stat / np.sqrt(n1 + n2)
    return {
        "statistic":   float(stat),
        "pvalue":      float(p),
        "tier_a_mean": float(np.nanmean(vals_a)),
        "tier_b_mean": float(np.nanmean(vals_b)),
        "effect_size": float(r_effect),
    }


def compare_tiers(tier_a_data, tier_b_data) -> float:
    """Rank-sum comparison between hierarchy tiers. Returns p-value."""
    if len(tier_a_data) == 0 or len(tier_b_data) == 0:
        return np.nan
    return float(stats.ranksums(tier_a_data, tier_b_data).pvalue)


def summarize_by_area(results: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
    """Pass-through for area-keyed result dicts. Add aggregation logic as needed."""
    return results

def compute_phase_modulation_statistics(phase_bins, fr_by_phase):
    """
    Computes Rayleigh test for circular uniformity and modulation depth for phase-locked firing.
    """
    from scipy.stats import circmean, circvar
    
    # Simple modulation depth (max-min / max+min)
    mod_depth = (np.max(fr_by_phase) - np.min(fr_by_phase)) / (np.max(fr_by_phase) + np.min(fr_by_phase))
    
    # Circular mean (preferred phase)
    pref_phase = circmean(phase_bins, weights=fr_by_phase)
    
    return {'mod_depth': mod_depth, 'preferred_phase': pref_phase}
