import numpy as np
import scipy.signal
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.analysis.lfp.lfp_preproc import preprocess_lfp

def get_band_power(data, lowcut, highcut, fs=1000.0):
    nyq = 0.5 * fs
    b, a = scipy.signal.butter(4, [lowcut/nyq, highcut/nyq], btype='band')
    filtered = scipy.signal.filtfilt(b, a, data, axis=-1)
    env = np.abs(scipy.signal.hilbert(filtered, axis=-1))
    return env ** 2

def analyze_spectral_harmony(loader: DataLoader, areas: list, condition="AXAB"):
    """
    Computes cross-area envelope correlation matrices for Beta and Gamma bands.
    Uses trial-wise correlations within matched sessions to preserve structure.
    """
    n = len(areas)
    
    # Store correlation matrices per session
    session_mats = {
        "Beta_Baseline": [],
        "Beta_Omission": [],
        "Gamma_Baseline": [],
        "Gamma_Omission": []
    }
    
    sessions = loader.get_sessions()
    
    for ses in sessions:
        print(f"[action] Computing harmony for session {ses}")
        
        # Load and preprocess LFP for all areas in this session
        ses_envelopes = {}
        for area in areas:
            # get_signal returns list of arrays (one per probe)
            lfp_list = loader.get_signal(mode="lfp", condition=condition, area=area, align_to="omission", session=ses)
            if not lfp_list: continue
            
            # If multiple probes hit the same area in the same session, we average them or take the first
            # We'll concatenate channels across probes for the same area, then mean
            lfp_concat = np.concatenate(lfp_list, axis=1) # (trials, channels, time)
            if lfp_concat.size == 0: continue
            
            lfp_clean = preprocess_lfp(lfp_concat)
            area_lfp = np.mean(lfp_clean, axis=1) # (trials, time)
            
            ses_envelopes[area] = {
                "Beta": get_band_power(area_lfp, 13, 30),
                "Gamma": get_band_power(area_lfp, 35, 80)
            }
            
        # If less than 2 areas, can't correlate
        if len(ses_envelopes) < 2: continue
        
        # Windows (aligned to omission at 1000)
        windows = {
            "Baseline": (750, 950), # 250ms to 50ms pre-omission
            "Omission": (1000, 1500) # 0 to 500ms post-omission
        }
        
        for band in ["Beta", "Gamma"]:
            for win_name, win in windows.items():
                mat = np.full((n, n), np.nan)
                
                for i, a1 in enumerate(areas):
                    for j, a2 in enumerate(areas):
                        if a1 in ses_envelopes and a2 in ses_envelopes:
                            e1 = ses_envelopes[a1][band][:, win[0]:win[1]]
                            e2 = ses_envelopes[a2][band][:, win[0]:win[1]]
                            
                            # Make sure trial counts match
                            min_trials = min(e1.shape[0], e2.shape[0])
                            if min_trials == 0: continue
                            e1 = e1[:min_trials]
                            e2 = e2[:min_trials]
                            
                            corrs = []
                            for t in range(min_trials):
                                std1, std2 = np.std(e1[t]), np.std(e2[t])
                                if std1 > 1e-10 and std2 > 1e-10:
                                    corrs.append(np.corrcoef(e1[t], e2[t])[0, 1])
                                    
                            if corrs:
                                mat[i, j] = np.mean(corrs)
                                
                session_mats[f"{band}_{win_name}"].append(mat)
                
    # Average across sessions (nanmean handles missing pairs)
    results = {}
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        for key, mats in session_mats.items():
            if mats:
                avg_mat = np.nanmean(np.stack(mats), axis=0)
                # Fill remaining NaNs with 0 for plotting
                avg_mat = np.nan_to_num(avg_mat, nan=0.0)
                results[key] = avg_mat
            else:
                results[key] = np.zeros((n, n))
                
    print(f"[result] Computed Spectral Harmony across {len(sessions)} sessions.")
    return results
