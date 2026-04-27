import numpy as np
from scipy.signal import butter, filtfilt, hilbert
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log

def bandpass_filter(data, fs, lowcut, highcut, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, data, axis=-1)

def compute_continuous_sfc(spk, lfp_phase, win_size=200, step=50):
    """
    Computes PLV in a sliding window.
    spk: (trials, time)
    lfp_phase: (trials, time)
    """
    n_time = spk.shape[1]
    starts = np.arange(0, n_time - win_size + 1, step)
    plvs = []
    times = []
    
    for start in starts:
        end = start + win_size
        spk_win = spk[:, start:end]
        phase_win = lfp_phase[:, start:end]
        
        spike_indices = np.where(spk_win > 0)
        spike_phases = phase_win[spike_indices]
        
        if len(spike_phases) < 5:
            plvs.append(np.nan)
        else:
            complex_phases = np.exp(1j * spike_phases)
            plv = np.abs(np.mean(complex_phases))
            plvs.append(plv)
            
        times.append(start + win_size / 2 - 2000) # center of window relative to omission
        
    return np.array(times), np.array(plvs)

def analyze_sfc_delta():
    """
    Computes sliding-window Delta-band (2-4 Hz) SFC for all Stable-Plus units
    over the entire [-2000, 2000]ms window.
    """
    loader = DataLoader()
    areas = list(loader.area_map.keys())
    results = {}
    
    fs = 1000
    lowcut, highcut = 2.0, 4.0 # Delta
    
    for area in areas:
        log.progress(f"Computing Continuous Delta SFC for {area}")
        
        spk_axab = loader.get_signal("spk", "AXAB", area, "omission", pre_ms=2000, post_ms=2000)
        lfp_axab = loader.get_signal("lfp", "AXAB", area, "omission", pre_ms=2000, post_ms=2000)
        spk_aaab = loader.get_signal("spk", "AAAB", area, "omission", pre_ms=2000, post_ms=2000)
        lfp_aaab = loader.get_signal("lfp", "AAAB", area, "omission", pre_ms=2000, post_ms=2000)
        
        if not spk_axab or not lfp_axab or not spk_aaab or not lfp_aaab:
            continue
            
        all_sfc_ax = []
        all_sfc_aa = []
        time_vector = None
        
        area_entries = loader.area_map.get(area, [])
        for i, entry in enumerate(area_entries):
            ses = entry["session"]
            if ses in loader.BLACKLISTED_SESSIONS: continue
            
            try:
                ax_spk = spk_axab[i]
                ax_lfp = lfp_axab[i]
                aa_spk = spk_aaab[i]
                aa_lfp = lfp_aaab[i]
            except IndexError: continue
            
            if ax_spk.shape[-1] < 4000 or aa_spk.shape[-1] < 4000:
                continue
                
            min_trials = min(ax_spk.shape[0], ax_lfp.shape[0])
            ax_spk = ax_spk[:min_trials, :, :]
            ax_lfp = ax_lfp[:min_trials, :, :]
            
            min_trials_aa = min(aa_spk.shape[0], aa_lfp.shape[0])
            aa_spk = aa_spk[:min_trials_aa, :, :]
            aa_lfp = aa_lfp[:min_trials_aa, :, :]
            
            # Process LFP Phase
            ax_mean_lfp = np.mean(ax_lfp, axis=1) # (trials, time)
            aa_mean_lfp = np.mean(aa_lfp, axis=1)
            
            ax_filt = bandpass_filter(ax_mean_lfp, fs, lowcut, highcut)
            ax_phase = np.angle(hilbert(ax_filt, axis=-1))
            
            aa_filt = bandpass_filter(aa_mean_lfp, fs, lowcut, highcut)
            aa_phase = np.angle(hilbert(aa_filt, axis=-1))
            
            # Identify Stable-Plus units
            # We'll use 1 Hz as minimum firing rate in any of the relevant windows
            win_stim = slice(1000, 1500) # -1000 to -500 relative to omission (in 4000ms array, 1000 to 1500)
            win_omit = slice(2000, 2500) # 0 to +500
            
            for u in range(ax_spk.shape[1]):
                fr_stim = np.mean(ax_spk[:, u, win_stim]) * 1000
                fr_omit = np.mean(ax_spk[:, u, win_omit]) * 1000
                
                if max(fr_stim, fr_omit) < 1.0:
                    continue
                    
                times, plv_ax = compute_continuous_sfc(ax_spk[:, u, :], ax_phase)
                _, plv_aa = compute_continuous_sfc(aa_spk[:, u, :], aa_phase)
                
                if time_vector is None: time_vector = times
                
                all_sfc_ax.append(plv_ax)
                all_sfc_aa.append(plv_aa)
                
        if all_sfc_ax:
            # Average across all units
            sfc_ax = np.array(all_sfc_ax)
            sfc_aa = np.array(all_sfc_aa)
            
            results[area] = {
                "times": time_vector,
                "ax_mean": np.nanmean(sfc_ax, axis=0),
                "ax_sem": np.nanstd(sfc_ax, axis=0) / np.sqrt(np.maximum(1, np.sum(~np.isnan(sfc_ax), axis=0))),
                "aa_mean": np.nanmean(sfc_aa, axis=0),
                "aa_sem": np.nanstd(sfc_aa, axis=0) / np.sqrt(np.maximum(1, np.sum(~np.isnan(sfc_aa), axis=0))),
                "n_units": len(all_sfc_ax)
            }
            
            # 3. STATISTICAL COMPARISON (Significance-Tier Standard)
            # Compare AXAB vs AAAB Delta PLV in the Omission window (0 to 500ms)
            from scipy.stats import ranksums
            from src.analysis.stats.tiers import get_significance_tier
            
            # time_vector is centered on windows. Omission window is around 0.
            win_mask = (time_vector >= 0) & (time_vector <= 500)
            
            # Average PLV per unit in the window
            plv_ax_pop = np.nanmean(sfc_ax[:, win_mask], axis=1)
            plv_aa_pop = np.nanmean(sfc_aa[:, win_mask], axis=1)
            
            # Filter NaNs
            mask = ~np.isnan(plv_ax_pop) & ~np.isnan(plv_aa_pop)
            if np.sum(mask) >= 5:
                stat, p_val = ranksums(plv_ax_pop[mask], plv_aa_pop[mask])
                tier, k, stars = get_significance_tier(p_val)
                results[area]["stats"] = {
                    "p": p_val, "tier": tier, "stars": stars, "test": "Rank-Sum (Delta PLV)"
                }
                print(f"[stats] SFC-Delta Area {area} | {tier} ({p_val:.2e}) | {stars}")
            
    return results