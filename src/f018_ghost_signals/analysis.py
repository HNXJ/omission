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
    
    for ses in sessions:
        log.info(f"Analyzing Ghost Signals for Session: {ses}")
        for area in areas:
            # Load AXAB (2nd omission)
            spk_omit = loader.get_signal(mode="spk", condition="AXAB", area=area, session=ses)
            if not spk_omit: continue
            
            # Detect ramping in d1 (531 to 1031) - wait, p2 starts at 1031.
            # So d1 is 531 to 1031.
            # Ramping usually starts in the delay period before the expected event.
            slopes, r2 = detect_ramping_units(spk_omit[0], window=(531, 1031))
            
            # Filter for significant rampers (slope > 0.005 Hz/ms and R2 > 0.5)
            # 0.005 Hz/ms = 5 Hz/sec
            valid_rampers = (slopes > 0.005) & (r2 > 0.3)
            
            if np.any(valid_rampers):
                log.info(f"Found {np.sum(valid_rampers)} Ghost Signal units in {area} ({ses})")
                results[area]['slopes'].extend(slopes[valid_rampers].tolist())
                
                # Average PSTH for valid rampers
                avg_psth = np.mean(spk_omit[0][:, valid_rampers, :], axis=(0, 1)) * 1000.0
                results[area]['psths'].append(avg_psth)
                
    # Final aggregation
    final_results = {}
    for area in areas:
        if results[area]['psths']:
            final_results[area] = {
                'slopes': results[area]['slopes'],
                'avg_psth': np.mean(results[area]['psths'], axis=0)
            }
            
    return final_results
