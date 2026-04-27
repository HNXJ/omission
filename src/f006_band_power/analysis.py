import numpy as np
from src.analysis.lfp.lfp_pipeline import run_lfp_spectral_pipeline
from src.analysis.io.logger import log

def analyze_band_dynamics(areas: list, conditions=None):
    if conditions is None:
        conditions = ["AXAB", "AAAB"]
        
    results = {}
    for cond in conditions:
        results[cond] = {}
        for area in areas:
            print(f"[action] Running Band pipeline for {area} ({cond})")
            try:
                res = run_lfp_spectral_pipeline(area, cond)
                if res is not None:
                    results[cond][area] = res
            except Exception as e:
                print(f"[error] Failed {area} {cond}: {e}")

    # 3. STATISTICAL COMPARISON (Significance-Tier Standard)
    if "AXAB" in results and "AAAB" in results:
        from scipy.stats import ranksums
        from src.analysis.stats.tiers import get_significance_tier
        
        results["stats"] = {}
        for area in areas:
            if area in results["AXAB"] and area in results["AAAB"]:
                results["stats"][area] = {}
                bands = results["AXAB"][area]["bands_full"].keys()
                
                times = results["AXAB"][area]["times"]
                win_mask = (times >= 969) & (times <= 1500)
                
                for band in bands:
                    pow_axab = np.mean(results["AXAB"][area]["bands_full"][band][:, :, win_mask], axis=(1, 2))
                    pow_aaab = np.mean(results["AAAB"][area]["bands_full"][band][:, :, win_mask], axis=(1, 2))
                    
                    stat, p_val = ranksums(pow_axab, pow_aaab)
                    tier, k, stars = get_significance_tier(p_val)
                    
                    results["stats"][area][band] = {
                        "p": p_val, "tier": tier, "stars": stars
                    }
                    print(f"[stats] Area {area} | Band {band} | {tier} ({p_val:.2e})")

    return results
