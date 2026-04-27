import numpy as np

def get_significance_tier(p_value):
    """
    Assigns a Significance Tier (S_k) based on logarithmic resolution.
    
    Tiers:
    - Null: p >= 0.5
    - Insignificant: 0.5 > p >= 0.05
    - Sig-1: 0.05 > p >= 0.01 (*)
    - Sig-k: 10^-k > p >= 10^-(k+1) (k*)
    """
    if p_value >= 0.5:
        return "Null", 0, ""
    if p_value >= 0.05:
        return "Insignificant", 0, "n.s."
    
    if p_value < 1e-10: # Cap at Sig-10 for sanity
        return "Sig-10+", 10, "**********"
        
    k = int(np.floor(-np.log10(p_value)))
    if k == 1:
        return "Sig-1", 1, "*"
    
    return f"Sig-{k}", k, "*" * k

def format_stats_proof(test_name, p_value, n_sessions, n_units):
    """
    Generates a high-density statistical proof string for plot titles/legends.
    """
    tier_name, k, stars = get_significance_tier(p_value)
    proof = f"[{test_name}] p={p_value:.2e} ({tier_name}) | N={n_sessions}S/{n_units}U"
    return proof, stars
