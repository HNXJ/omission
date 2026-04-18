# beta
import numpy as np
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
import nitime.analysis as nta
import nitime.timeseries as ts

def analyze_effective_connectivity(loader: DataLoader, sessions: list, area_pairs: list, condition="AXAB"):
    """
    Computes Effective Connectivity (Granger Causality) between area pairs.
    Focuses on the omission window.
    """
    results = {f"{a1}->{a2}": [] for a1, a2 in area_pairs}
    
    for ses in sessions:
        log.info(f"Analyzing Effective Connectivity for Session: {ses}")
        for a1, a2 in area_pairs:
            lfp1 = loader.get_signal(mode="lfp", condition=condition, area=a1, session=ses)
            lfp2 = loader.get_signal(mode="lfp", condition=condition, area=a2, session=ses)
            
            if not lfp1 or not lfp2: continue
            
            # Omission window: 1031 to 1562
            # Average across channels for area-level connectivity
            s1 = np.mean(lfp1[0][:, :, 1031:1562], axis=(0, 1))
            s2 = np.mean(lfp2[0][:, :, 1031:1562], axis=(0, 1))
            
            # nitime Granger Analysis
            data = np.vstack([s1, s2])
            time_series = ts.TimeSeries(data, sampling_rate=1000.0)
            granger = nta.GrangerAnalyzer(time_series, order=10) # Order 10 (10ms lag)
            
            # Granger causality is frequency-dependent
            # granger.causality_xy shape is (2, 2, n_freqs)
            f_idx = (granger.frequencies >= 4) & (granger.frequencies <= 80)
            
            gc_12 = np.mean(granger.causality_xy[0, 1, f_idx])
            gc_21 = np.mean(granger.causality_xy[1, 0, f_idx])
            
            results[f"{a1}->{a2}"].append(gc_12)
            results[f"{a2}->{a1}"] = results.get(f"{a2}->{a1}", [])
            results[f"{a2}->{a1}"].append(gc_21)
            
    return results
