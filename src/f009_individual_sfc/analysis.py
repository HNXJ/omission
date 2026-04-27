import numpy as np
from scipy.signal import butter, filtfilt, hilbert
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log

def compute_ppc(phases):
    """
    Computes Pairwise Phase Consistency (PPC) rigorously to control for spike count.
    PPC = [(sum cos)^2 + (sum sin)^2 - N] / [N(N-1)]
    """
    N = len(phases)
    if N < 2: return np.nan
    
    sum_cos = np.sum(np.cos(phases))
    sum_sin = np.sum(np.sin(phases))
    
    R2 = sum_cos**2 + sum_sin**2
    ppc = (R2 - N) / (N * (N - 1))
    return ppc

def bandpass_filter(data, fs, lowcut, highcut, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, data, axis=-1)

def calculate_ppc_zscore(spk_cond, lfp_cond, freqs, n_shuffles=1000):
    """
    spk_cond: (trials, time) binary spikes
    lfp_cond: (trials, channels, time) lfp data
    freqs: dict of {name: (low, high)}
    """
    fs = 1000 # 1kHz
    min_trials = min(spk_cond.shape[0], lfp_cond.shape[0])
    spk_cond = spk_cond[:min_trials, :]
    lfp_cond = lfp_cond[:min_trials, :, :]
    
    mean_lfp = np.mean(lfp_cond, axis=1) # (trials, time)
    
    res = {}
    for band, (low, high) in freqs.items():
        # Filter LFP and get phase
        filt_lfp = bandpass_filter(mean_lfp, fs, low, high)
        analytic_sig = hilbert(filt_lfp, axis=-1)
        inst_phase = np.angle(analytic_sig) # (trials, time)
        
        # Extract phases at spike times
        true_phases = []
        trials, times = np.nonzero(spk_cond)
        
        for tr, t in zip(trials, times):
            true_phases.append(inst_phase[tr, t])
            
        true_phases = np.array(true_phases)
        obs_ppc = compute_ppc(true_phases)
        
        if np.isnan(obs_ppc):
            res[band] = {"z": 0.0, "phases": []}
            continue
            
        # Shuffling: circularly shift spike trains
        null_ppcs = []
        n_times = spk_cond.shape[1]
        for _ in range(n_shuffles):
            shuffled_phases = []
            for tr, t in zip(trials, times):
                shift = np.random.randint(1, n_times)
                t_shift = (t + shift) % n_times
                shuffled_phases.append(inst_phase[tr, t_shift])
            null_ppcs.append(compute_ppc(shuffled_phases))
            
        null_ppcs = np.array(null_ppcs)
        null_mean = np.nanmean(null_ppcs)
        null_std = np.nanstd(null_ppcs)
        
        z = (obs_ppc - null_mean) / (null_std + 1e-9)
        res[band] = {"z": z, "phases": true_phases}
        
    return res

def analyze_individual_sfc():
    """
    Extracts top 20 units for O+, S+, S-, Null and computes their PPC Z-scores
    across 3 conditions: Omission, Expected, Standard.
    """
    loader = DataLoader()
    
    areas = list(loader.area_map.keys())
    all_units = []
    
    log.progress("Scanning 'Stable-Plus' units for O+, S+, S-, Null classification...")
    
    for area in areas:
        spk_axab = loader.get_signal("spk", "AXAB", area, "omission")
        spk_aaab = loader.get_signal("spk", "AAAB", area, "omission")
        lfp_axab = loader.get_signal("lfp", "AXAB", area, "omission")
        lfp_aaab = loader.get_signal("lfp", "AAAB", area, "omission")
        
        if not spk_axab or not spk_aaab or not lfp_axab or not lfp_aaab:
            continue
            
        area_entries = loader.area_map.get(area, [])
        for i, entry in enumerate(area_entries):
            ses = entry["session"]
            if ses in loader.BLACKLISTED_SESSIONS: continue
            
            try:
                arr_ax = spk_axab[i]
                arr_aa = spk_aaab[i]
                lfp_ax = lfp_axab[i]
                lfp_aa = lfp_aaab[i]
            except IndexError: continue
            
            # Align to omission: length=2000 (pre=1000, post=1000)
            win_p1 = slice(0, 500)      # Expected / Stimulus 1 (-1000 to -500)
            win_omit = slice(1000, 1500) # Omission or Standard (0 to +500)
            
            for u in range(arr_ax.shape[1]):
                u_ax = arr_ax[:, u, :]
                u_aa = arr_aa[:, u, :]
                
                fr_p1_ax = np.mean(u_ax[:, win_p1]) * 1000
                fr_omit_ax = np.mean(u_ax[:, win_omit]) * 1000
                fr_omit_aa = np.mean(u_aa[:, win_omit]) * 1000
                
                # Baseline pre-trial is tricky in omission aligned, let's use the 500-1000 ms window as pre-omission baseline (fixation)
                win_fix = slice(500, 1000) 
                fr_fix = np.mean(u_ax[:, win_fix]) * 1000
                
                max_fr = max(fr_p1_ax, fr_omit_ax, fr_omit_aa, fr_fix)
                if max_fr < 1.0: continue # Stable-Plus
                
                # Ratios
                s_ratio = (fr_p1_ax - fr_fix) / (fr_p1_ax + fr_fix + 1e-6)
                o_ratio = (fr_omit_ax - fr_fix) / (fr_omit_ax + fr_fix + 1e-6)
                null_score = abs(s_ratio) + abs(o_ratio) # lower is better for null
                
                all_units.append({
                    "id": f"{area}_{ses}_u{u}",
                    "area": area,
                    "ses": ses,
                    "u_idx": u,
                    "s_ratio": s_ratio,
                    "o_ratio": o_ratio,
                    "null_score": null_score,
                    "spk_ax": u_ax,
                    "spk_aa": u_aa,
                    "lfp_ax": lfp_ax,
                    "lfp_aa": lfp_aa
                })

    log.info(f"Total valid Stable-Plus units: {len(all_units)}")
    
    # Sort into categories (Top 20 each)
    o_plus = sorted(all_units, key=lambda x: x["o_ratio"], reverse=True)[:20]
    s_plus = sorted(all_units, key=lambda x: x["s_ratio"], reverse=True)[:20]
    s_minus = sorted(all_units, key=lambda x: x["s_ratio"], reverse=False)[:20]
    null = sorted(all_units, key=lambda x: x["null_score"], reverse=False)[:20]
    
    classes = {
        "O+": o_plus,
        "S+": s_plus,
        "S-": s_minus,
        "Null": null
    }
    
    freqs = {
        "Theta": (4, 8),
        "Beta": (13, 30),
        "Gamma": (30, 80)
    }
    
    results = {}
    
    for cls_name, units in classes.items():
        log.progress(f"Computing PPC Z-scores for {cls_name} (N={len(units)})")
        
        cls_res = {
            "Omission": {band: {"z": [], "phases": []} for band in freqs},
            "Expected": {band: {"z": [], "phases": []} for band in freqs},
            "Standard": {band: {"z": [], "phases": []} for band in freqs}
        }
        
        for u in units:
            win_exp = slice(0, 500)
            win_omt = slice(1000, 1500)
            
            # Omission: AXAB [1000:1500]
            spk_omit = u["spk_ax"][:, win_omt]
            lfp_omit = u["lfp_ax"][:, :, win_omt]
            res_omit = calculate_ppc_zscore(spk_omit, lfp_omit, freqs)
            
            # Expected: AXAB [0:500]
            spk_exp = u["spk_ax"][:, win_exp]
            lfp_exp = u["lfp_ax"][:, :, win_exp]
            res_exp = calculate_ppc_zscore(spk_exp, lfp_exp, freqs)
            
            # Standard: AAAB [1000:1500]
            spk_std = u["spk_aa"][:, win_omt]
            lfp_std = u["lfp_aa"][:, :, win_omt]
            res_std = calculate_ppc_zscore(spk_std, lfp_std, freqs)
            
            for b in freqs:
                cls_res["Omission"][b]["z"].append(res_omit[b]["z"])
                cls_res["Omission"][b]["phases"].extend(res_omit[b]["phases"])
                
                cls_res["Expected"][b]["z"].append(res_exp[b]["z"])
                cls_res["Expected"][b]["phases"].extend(res_exp[b]["phases"])
                
                cls_res["Standard"][b]["z"].append(res_std[b]["z"])
                cls_res["Standard"][b]["phases"].extend(res_std[b]["phases"])
                
        results[cls_name] = cls_res

    # 3. STATISTICAL COMPARISON (Significance-Tier Standard)
    # Compare Omission vs Standard Z-scores for each class and band
    from scipy.stats import ranksums
    from src.analysis.stats.tiers import get_significance_tier
    
    results["stats"] = {}
    for cls_name in classes:
        results["stats"][cls_name] = {}
        for b in freqs:
            z_omit = results[cls_name]["Omission"][b]["z"]
            z_std = results[cls_name]["Standard"][b]["z"]
            
            if len(z_omit) > 0 and len(z_std) > 0:
                stat, p_val = ranksums(z_omit, z_std)
                tier, k, stars = get_significance_tier(p_val)
                results["stats"][cls_name][b] = {
                    "p": p_val, "tier": tier, "stars": stars, "test": "Rank-Sum (PPC-Z)"
                }
                print(f"[stats] {cls_name} | {b} | {tier} ({p_val:.2e}) | {stars}")

    return results