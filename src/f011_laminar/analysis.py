import numpy as np
from scipy.signal import butter, filtfilt, hilbert
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log

def get_high_gamma(data, fs=1000):
    nyq = 0.5 * fs
    b, a = butter(4, [35/nyq, 80/nyq], btype='band')
    filt = filtfilt(b, a, data, axis=-1)
    env = np.abs(hilbert(filt, axis=-1))
    return env**2

def align_to_layer4(hg_power, l4_idx, target_length=60):
    """
    hg_power: (channels, time)
    Aligns such that l4_idx is at the center (index target_length // 2).
    Pads with NaNs if necessary.
    """
    center = target_length // 2
    aligned = np.full((target_length, hg_power.shape[1]), np.nan)
    
    n_ch = hg_power.shape[0]
    
    # Calculate how much of hg_power we can fit into aligned
    start_in_aligned = center - l4_idx
    end_in_aligned = start_in_aligned + n_ch
    
    start_in_hg = 0
    end_in_hg = n_ch
    
    if start_in_aligned < 0:
        start_in_hg = -start_in_aligned
        start_in_aligned = 0
        
    if end_in_aligned > target_length:
        end_in_hg = n_ch - (end_in_aligned - target_length)
        end_in_aligned = target_length
        
    if start_in_aligned < end_in_aligned and start_in_hg < end_in_hg:
        aligned[start_in_aligned:end_in_aligned, :] = hg_power[start_in_hg:end_in_hg, :]
        
    return aligned

def analyze_laminar_routing():
    loader = DataLoader()
    areas = list(loader.area_map.keys())
    results = {}
    
    # Target grid size for alignment (e.g. 60 channels to handle typical 32-128 channel sections)
    target_ch = 60
    
    for area in areas:
        log.progress(f"Computing Laminar Mapping for {area}")
        lfp_list = loader.get_signal(mode="lfp", condition="AXAB", area=area, align_to="omission", pre_ms=2000, post_ms=2000)
        
        if not lfp_list: continue
        
        aligned_hgs = []
        for lfp_arr in lfp_list:
            if lfp_arr.shape[-1] < 4000: continue
            
            # 1. Compute trial-averaged High Gamma
            mean_lfp = np.mean(lfp_arr, axis=0) # (channels, time)
            hg = get_high_gamma(mean_lfp)
            
            # 2. Identify L4 sink proxy
            # P1 onset is at index 2000 - 1031 = 969. Let's use 969 to 1069 for peak.
            p1_win = slice(969, 1069)
            hg_p1 = np.mean(hg[:, p1_win], axis=1)
            l4_idx = np.argmax(hg_p1)
            
            # 3. Align
            aligned = align_to_layer4(hg, l4_idx, target_length=target_ch)
            
            # Z-score normalize the heatmap per session to equalize
            mean_hg = np.nanmean(aligned)
            std_hg = np.nanstd(aligned)
            if std_hg > 0:
                aligned = (aligned - mean_hg) / std_hg
                
            aligned_hgs.append(aligned)
            
        if aligned_hgs:
            # 3. STATISTICAL COMPARISON (Significance-Tier Standard)
            # Compare High-Gamma power in Omission window (2000:2500) vs Baseline (1500:2000) across sessions
            from scipy.stats import wilcoxon
            from src.analysis.stats.tiers import get_significance_tier
            
            # Extract power for each session in the two windows
            omit_vals = []
            base_vals = []
            for hg_map in aligned_hgs:
                omit_vals.append(np.nanmean(hg_map[:, 2000:2500]))
                base_vals.append(np.nanmean(hg_map[:, 1500:2000]))
            
            omit_vals = np.array(omit_vals)
            base_vals = np.array(base_vals)
            
            mask = ~np.isnan(omit_vals) & ~np.isnan(base_vals)
            o_clean, b_clean = omit_vals[mask], base_vals[mask]
            
            if len(o_clean) >= 5 and not np.all(o_clean == b_clean):
                stat, p_val = wilcoxon(o_clean, b_clean)
                tier, k, stars = get_significance_tier(p_val)
            else:
                p_val, tier, stars = 1.0, "Null", ""
                
            # Nanmean across sessions
            pop_hg = np.nanmean(np.array(aligned_hgs), axis=0)
            results[area] = {
                "heatmap": pop_hg,
                "stats": {"p": p_val, "tier": tier, "stars": stars, "test": "Wilcoxon Signed-Rank"}
            }
            print(f"[stats] Laminar Area {area} | {tier} ({p_val:.2e}) | {stars}")
            
    return results