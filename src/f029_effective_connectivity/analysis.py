import numpy as np
from statsmodels.tsa.stattools import grangercausalitytests
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log

def analyze_granger_causality(areas: list, maxlag=20):
    """
    Computes Granger Causality across the hierarchy (comparing each area against V1 as a baseline).
    Tests for V1 -> Area (Feedforward) and Area -> V1 (Feedback).
    Focuses on Stimulus Window (1000-1500) and Omission Window (2000-2500).
    """
    loader = DataLoader()
    results = {}
    
    if "V1" not in areas:
        log.warning("V1 must be in areas for baseline comparison.")
        return results
        
    # Get V1 LFP
    lfp_v1_axab = loader.get_signal(mode="lfp", condition="AXAB", area="V1", align_to="omission")
    if not lfp_v1_axab:
        log.error("V1 AXAB LFP not found.")
        return results
        
    min_trials = min([arr.shape[0] for arr in lfp_v1_axab])
    v1_data = np.concatenate([arr[:min_trials] for arr in lfp_v1_axab], axis=0) # (trials, channels, time)
    # Average across channels
    v1_mean = np.mean(v1_data, axis=1) # (trials, time)
    
    # We define windows based on standard alignment:
    # 0ms omission is at 2000ms.
    # Stimulus: 1000-1500 (1000ms to 500ms before omission)
    # Omission: 2000-2500 (0ms to 500ms after omission)
    win_stim = slice(1000, 1500)
    win_omit = slice(2000, 2500)
    
    for area in areas:
        if area == "V1": continue
        log.progress(f"Computing Granger Causality: V1 <-> {area}")
        
        lfp_area = loader.get_signal(mode="lfp", condition="AXAB", area=area, align_to="omission")
        if not lfp_area: continue
        
        area_data = np.concatenate([arr[:min_trials] for arr in lfp_area], axis=0)
        area_mean = np.mean(area_data, axis=1) # (trials, time)
        
        # We average the GC F-statistic over trials to get a robust estimate
        # To speed up, we can average the signals or sample trials. Let's sample top 20 trials.
        sample_trials = min(20, v1_mean.shape[0])
        
        gc_stim_v1_to_area = []
        gc_stim_area_to_v1 = []
        gc_omit_v1_to_area = []
        gc_omit_area_to_v1 = []
        
        for i in range(sample_trials):
            v1_s = v1_mean[i, win_stim]
            area_s = area_mean[i, win_stim]
            
            v1_o = v1_mean[i, win_omit]
            area_o = area_mean[i, win_omit]
            
            # Grangercausalitytests tests if col 2 causes col 1.
            # To test X -> Y, we pass [Y, X]
            
            # Stimulus
            res_v1_to_area_s = grangercausalitytests(np.column_stack([area_s, v1_s]), maxlag=maxlag, verbose=False)
            res_area_to_v1_s = grangercausalitytests(np.column_stack([v1_s, area_s]), maxlag=maxlag, verbose=False)
            
            # Omission
            res_v1_to_area_o = grangercausalitytests(np.column_stack([area_o, v1_o]), maxlag=maxlag, verbose=False)
            res_area_to_v1_o = grangercausalitytests(np.column_stack([v1_o, area_o]), maxlag=maxlag, verbose=False)
            
            # Extract F-statistic for the maxlag
            gc_stim_v1_to_area.append(res_v1_to_area_s[maxlag][0]['ssr_ftest'][0])
            gc_stim_area_to_v1.append(res_area_to_v1_s[maxlag][0]['ssr_ftest'][0])
            
            gc_omit_v1_to_area.append(res_v1_to_area_o[maxlag][0]['ssr_ftest'][0])
            gc_omit_area_to_v1.append(res_area_to_v1_o[maxlag][0]['ssr_ftest'][0])
            
        results[area] = {
            "stim": {
                "ff": np.mean(gc_stim_v1_to_area), # Feedforward (V1 -> Area)
                "fb": np.mean(gc_stim_area_to_v1)  # Feedback (Area -> V1)
            },
            "omit": {
                "ff": np.mean(gc_omit_v1_to_area),
                "fb": np.mean(gc_omit_area_to_v1)
            }
        }
        log.info(f"  {area} Stim FF/FB: {results[area]['stim']['ff']:.2f} / {results[area]['stim']['fb']:.2f}")
        log.info(f"  {area} Omit FF/FB: {results[area]['omit']['ff']:.2f} / {results[area]['omit']['fb']:.2f}")

    return results
