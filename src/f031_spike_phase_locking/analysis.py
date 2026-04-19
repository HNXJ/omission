# beta
import numpy as np
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.analysis.lfp.sfc import calculate_plv, get_matched_sfc_data

def analyze_spike_phase_locking(loader: DataLoader, areas: list, condition="AXAB"):
    """
    Computes Spike-Field Phase Locking Value (PLV) spectrum for each area.
    Aggregates across all units in the area.
    """
    results = {}
    freqs = np.logspace(np.log10(4), np.log10(80), 12) # Theta to Gamma
    
    for area in areas:
        log.info(f"Computing PLV Spectrum for {area} in {condition}")
        # Get all units for this area
        area_units = []
        for entry in loader.area_map.get(area, []):
            ses = entry["session"]; p = entry["probe"]; u_idx = entry["local_idx"]
            # We need to find unit indices. Let's assume selection of top units for efficiency.
            from src.analysis.lfp.sfc import select_top_units
            units = select_top_units(loader, area, mode="omission", top_n=5)
            area_units.extend(units)
            
        area_plv = []
        for unit in area_units:
            lfp, spk = get_matched_sfc_data(loader, unit)
            if lfp is None: continue
            
            unit_spectrum = []
            for f in freqs:
                bw = max(2.0, f * 0.2)
                plv, _ = calculate_plv(lfp, spk, fs=1000, freq_band=(f-bw/2, f+bw/2))
                unit_spectrum.append(plv)
            area_plv.append(unit_spectrum)
            
        if area_plv:
            results[area] = {
                "freqs": freqs,
                "plv_mean": np.mean(area_plv, axis=0),
                "plv_sem": np.std(area_plv, axis=0) / np.sqrt(len(area_plv))
            }
            
    return results
