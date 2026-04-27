import numpy as np
from src.analysis.lfp.lfp_pipeline import run_lfp_spectral_pipeline
from src.analysis.io.logger import log

def analyze_area_tfrs(areas: list, conditions=None):
    if conditions is None:
        conditions = ["AXAB", "AAAB"] 
        
    results = {}
    for cond in conditions:
        print(f"[action] Analyzing TFR family: {cond}")
        results[cond] = {}
        for area in areas:
            print(f"[action] Running LFP pipeline for {area} ({cond})")
            try:
                res = run_lfp_spectral_pipeline(area, cond)
                if res is not None:
                    results[cond][area] = res
            except Exception as e:
                print(f"[error] Failed {area} {cond}: {e}")

    # 3. STATISTICAL COMPARISON (Significance-Tier Standard)
    # Compare Omission (AXAB) vs Standard (AAAB) Gamma Power
    if "AXAB" in results and "AAAB" in results:
        from scipy.stats import ranksums
        from src.analysis.stats.tiers import get_significance_tier
        
        for area in areas:
            if area in results["AXAB"] and area in results["AAAB"]:
                # Extract trial-averaged gamma power in omission window (969-1500)
                # results[cond][area]['bands_full']['Gamma'] is (trials, channels, time)
                g_axab = results["AXAB"][area]["bands_full"]["Gamma"]
                g_aaab = results["AAAB"][area]["bands_full"]["Gamma"]
                
                # Window 969 to 1500 relative to p1 onset
                # Note: tfr times are already local (-2000 to +2000)
                # Omission is at 969.
                times = results["AXAB"][area]["times"]
                win_mask = (times >= 969) & (times <= 1500)
                
                # Average across channels and then across time window
                pow_axab = np.mean(g_axab[:, :, win_mask], axis=(1, 2))
                pow_aaab = np.mean(g_aaab[:, :, win_mask], axis=(1, 2))
                
                stat, p_val = ranksums(pow_axab, pow_aaab)
                tier, k, stars = get_significance_tier(p_val)
                
                # Store in results metadata
                if "stats" not in results: results["stats"] = {}
                results["stats"][area] = {
                    "p": p_val, "tier": tier, "stars": stars, "test": "Rank-Sum (Gamma)"
                }
                print(f"[stats] TFR Area {area} | {tier} ({p_val:.2e}) | {stars}")

    return results
