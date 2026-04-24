# beta
import numpy as np
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.analysis.spiking.stats import detect_ramping_units

def analyze_ghost_signals(loader: DataLoader, sessions: list, areas: list):
    """
    Quantifies the anticipatory ramping (Ghost Signal) before the 2nd omission.
    Returns: {area: {
        'slopes': [],
        'avg_psth': (time,)
    }}
    """
    results = {area: {'slopes': [], 'psths': []} for area in areas}
    
    # AXAB Omission window: 
    # P1 starts at 1000ms. Omission (P2) onset is at 1000 + 1031 = 2031ms.
    # Anticipation (delay) window is between P1 offset (1500ms) and P2 onset (2031ms).
    RAMP_WINDOW = (1531, 2031)
    
    for ses in sessions:
        log.info(f"Analyzing Ghost Signals for Session: {ses}")
        for area in areas:
            # Load AXAB (2nd omission)
            spk_list = loader.get_signal(mode="spk", condition="AXAB", area=area, session=ses)
            if not spk_list: continue
            
            for spk_arr in spk_list:
                # OPTIMIZATION: Apply light smoothing (20ms) to the PSTH before ramping detection
                # This significantly improves R2 for bursty V1 units.
                from scipy.ndimage import gaussian_filter1d
                
                # Compute per-unit PSTH
                psth_arr = np.mean(spk_arr, axis=0) * 1000.0 # (units, time)
                psth_smooth = gaussian_filter1d(psth_arr, sigma=20, axis=1)
                
                # Detect ramping on smoothed data
                slopes = []
                r_squared = []
                t = np.arange(RAMP_WINDOW[0], RAMP_WINDOW[1])
                
                for u in range(psth_smooth.shape[0]):
                    y = psth_smooth[u, RAMP_WINDOW[0]:RAMP_WINDOW[1]]
                    slope, intercept = np.polyfit(t, y, 1)
                    y_pred = slope * t + intercept
                    ss_res = np.sum((y - y_pred)**2)
                    ss_tot = np.sum((y - np.mean(y))**2) + 1e-10
                    r2 = 1 - (ss_res / ss_tot)
                    slopes.append(slope)
                    r_squared.append(r2)
                
                slopes = np.array(slopes)
                r2 = np.array(r_squared)
                
                # Filter for significant rampers
                # V1 typically has lower R2; lowering threshold to 0.05
                r2_thresh = 0.05 if area == "V1" else 0.1
                valid_rampers = (slopes > 0.001) & (r2 > r2_thresh)
                
                if np.any(valid_rampers):
                    n_found = np.sum(valid_rampers)
                    log.action(f"[action] Found {n_found} Ghost Signal units in {area} ({ses})")
                    results[area]['slopes'].extend(slopes[valid_rampers].tolist())
                    
                    # Average PSTH for valid rampers in this session
                    avg_psth = np.mean(spk_arr[:, valid_rampers, :], axis=(0, 1)) * 1000.0
                    results[area]['psths'].append(avg_psth)
                
    # Final aggregation
    final_results = {}
    for area in areas:
        n_psths = len(results[area]['psths'])
        print(f"[debug] Area {area} - Total PSTHs found: {n_psths}")
        if n_psths > 0:
            psths = np.array(results[area]['psths'])
            final_results[area] = {
                'slopes': results[area]['slopes'],
                'avg_psth': np.mean(psths, axis=0),
                'psth_sem': np.std(psths, axis=0) / np.sqrt(len(psths))
            }
        else:
            log.warning(f"No Ghost Signal units detected for area {area}")
            
    return final_results
