# beta
import numpy as np
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.analysis.lfp.sfc import select_top_units, get_matched_sfc_data

def analyze_spike_triggered_average(loader: DataLoader, areas: list, win_ms=100, condition="AXAB"):
    """
    Computes Spike-Triggered Average (STA) of LFP for each area.
    """
    results = {}
    
    for area in areas:
        log.info(f"Computing STA for {area} in {condition}")
        units = select_top_units(loader, area, mode="omission", top_n=10)
        
        all_stas = []
        for unit in units:
            lfp, spk = get_matched_sfc_data(loader, unit)
            if lfp is None: continue
            
            # Find spikes in binary matrix (trials, time)
            tr, ti = np.where(spk > 0)
            
            # Extract LFP snippets around spike times
            snippets = []
            for t, i in zip(tr, ti):
                if i - win_ms >= 0 and i + win_ms < lfp.shape[1]:
                    snippets.append(lfp[t, i - win_ms : i + win_ms])
            
            if snippets:
                all_stas.append(np.mean(snippets, axis=0))
                
        if all_stas:
            results[area] = {
                "t": np.linspace(-win_ms, win_ms, 2 * win_ms),
                "sta_mean": np.mean(all_stas, axis=0),
                "sta_sem": np.std(all_stas, axis=0) / np.sqrt(len(all_stas))
            }
            
    return results
