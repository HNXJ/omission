# core
import numpy as np
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.analysis.lfp.sfc import select_top_units, get_matched_sfc_data, get_plv_spectrum, apply_subsampling

def analyze_sfc_plv(loader: DataLoader, areas: list):
    """
    Computes SFC (PLV) spectrum for top O+ and S+ units in each area.
    """
    results = {}
    for area in areas:
        log.info(f"Computing SFC for {area}")
        
        # 1. Selection
        s_units = select_top_units(loader, area, mode="stimulus", top_n=10)
        o_units = select_top_units(loader, area, mode="omission", top_n=10)
        
        if not s_units or not o_units: continue
        
        # 2. Loading and Alignment
        s_data = [get_matched_sfc_data(loader, u) for u in s_units]
        o_data = [get_matched_sfc_data(loader, u) for u in o_units]
        
        # Filter out failed loads
        s_data = [d for d in s_data if d[0] is not None]
        o_data = [d for d in o_data if d[0] is not None]
        
        if not s_data or not o_data: continue
        
        # 3. Subsampling
        all_spks = [d[1] for d in s_data] + [d[1] for d in o_data]
        sub_spks = apply_subsampling(all_spks)
        
        # 4. PLV Spectrum
        s_spectra = [get_plv_spectrum(s_data[i][0], sub_spks[i])[1] for i in range(len(s_data))]
        o_spectra = [get_plv_spectrum(o_data[i][0], sub_spks[len(s_data)+i])[1] for i in range(len(o_data))]
        freqs, _ = get_plv_spectrum(s_data[0][0], sub_spks[0])
        
        results[area] = {'freqs': freqs, 's_plus': s_spectra, 'o_plus': o_spectra}
    return results
