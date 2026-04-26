import numpy as np
import scipy.stats as stats
from scipy.ndimage import gaussian_filter1d
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log

def test_hpc_hypotheses():
    loader = DataLoader()
    areas = loader.CANONICAL_AREAS
    
    print("=== HPC Hypotheses Testing ===")
    
    results_area = {}
    
    for area in areas:
        spk_list = loader.get_signal("spk", "AXAB", area, "omission", pre_ms=1000, post_ms=1000)
        if not spk_list:
            continue
            
        area_units = []
        
        for spk in spk_list: # spk is (trials, units, time)
            if spk.shape[-1] < 2000:
                continue
                
            n_trials, n_units, n_time = spk.shape
            
            for u in range(n_units):
                # Baseline: -500 to 0 (indices 500 to 1000)
                # Omission: 0 to 500 (indices 1000 to 1500)
                base_rates = np.mean(spk[:, u, 500:1000], axis=1) * 1000
                omit_rates = np.mean(spk[:, u, 1000:1500], axis=1) * 1000
                
                # Filter out silent units
                if np.mean(base_rates) < 1.0 and np.mean(omit_rates) < 1.0:
                    continue
                    
                # H1: Suppression vs Disinhibition
                # Wilcoxon signed-rank test
                try:
                    stat, p_val = stats.wilcoxon(base_rates, omit_rates)
                except ValueError: # all zero differences
                    p_val = 1.0
                    
                is_sig = p_val < 0.05
                is_disinhibited = np.mean(omit_rates) > np.mean(base_rates)
                is_suppressed = np.mean(omit_rates) < np.mean(base_rates)
                
                # H2: Latency (Time to Peak)
                psth = np.mean(spk[:, u, :], axis=0) * 1000
                psth_smooth = gaussian_filter1d(psth, sigma=20)
                
                # Find peak in the omission window (0 to +500ms)
                omit_win_psth = psth_smooth[1000:1500]
                peak_idx = np.argmax(omit_win_psth)
                peak_latency = peak_idx # in ms after omission
                
                area_units.append({
                    "base_fr": np.mean(base_rates),
                    "omit_fr": np.mean(omit_rates),
                    "sig": is_sig,
                    "disinhibited": is_sig and is_disinhibited,
                    "suppressed": is_sig and is_suppressed,
                    "latency": peak_latency
                })
                
        if len(area_units) == 0:
            continue
            
        n_total = len(area_units)
        n_sig = sum(1 for u in area_units if u["sig"])
        n_dis = sum(1 for u in area_units if u["disinhibited"])
        n_sup = sum(1 for u in area_units if u["suppressed"])
        
        # Latency of significant disinhibited units
        sig_latencies = [u["latency"] for u in area_units if u["disinhibited"]]
        median_lat = np.median(sig_latencies) if sig_latencies else np.nan
        
        results_area[area] = {
            "n_total": n_total,
            "n_sig": n_sig,
            "pct_sig": (n_sig / n_total) * 100,
            "n_dis": n_dis,
            "pct_dis": (n_dis / n_total) * 100,
            "n_sup": n_sup,
            "pct_sup": (n_sup / n_total) * 100,
            "median_latency": median_lat,
            "latencies": sig_latencies
        }
        
    print("\n--- H1 & H3: Suppression/Disinhibition & Ubiquity/Sparsity ---")
    print(f"{'Area':<5} | {'Total':<6} | {'Sig(Ubiquity)':<15} | {'Disinhibited':<15} | {'Suppressed':<15}")
    for area, res in results_area.items():
        print(f"{area:<5} | {res['n_total']:<6} | {res['n_sig']:<4} ({res['pct_sig']:>5.1f}%) | {res['n_dis']:<4} ({res['pct_dis']:>5.1f}%) | {res['n_sup']:<4} ({res['pct_sup']:>5.1f}%)")
        
    print("\n--- H2: Feedforward vs Feedback (Latency) ---")
    print("Median latency of disinhibited (omission-responsive) units:")
    
    valid_areas = []
    lat_medians = []
    
    for area, res in results_area.items():
        if not np.isnan(res["median_latency"]):
            print(f"{area:<5} : {res['median_latency']:.1f} ms")
            valid_areas.append(area)
            lat_medians.append(res['median_latency'])
            
    # Test for hierarchical correlation (assuming canonical order represents hierarchy)
    hierarchy_ranks = {a: i for i, a in enumerate(loader.CANONICAL_AREAS)}
    ranks = [hierarchy_ranks[a] for a in valid_areas]
    
    corr, p = stats.spearmanr(ranks, lat_medians)
    print(f"\nSpearman correlation between hierarchy rank and median latency: r = {corr:.3f}, p = {p:.4f}")
    if corr > 0 and p < 0.05:
        print("-> Positive correlation: Feedforward (Lower areas respond earlier than higher areas)")
    elif corr < 0 and p < 0.05:
        print("-> Negative correlation: Feedback (Higher areas respond earlier than lower areas)")
    else:
        print("-> No significant correlation or simultaneous activation.")
        
    # Global Ubiquity Stats
    total_neurons = sum(r['n_total'] for r in results_area.values())
    total_sig = sum(r['n_sig'] for r in results_area.values())
    print(f"\nGlobal proportion of omission-responsive units: {total_sig}/{total_neurons} ({total_sig/total_neurons*100:.1f}%)")

if __name__ == "__main__":
    test_hpc_hypotheses()
