import numpy as np
import pandas as pd
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log

def analyze_putative_cell_types(areas: list):
    """
    Decodes Putative Excitatory (E) vs Inhibitory (I) contributions to omission.
    Uses waveform_duration from units_ses-{session}.csv.
    E: > 0.4ms
    I: < 0.4ms
    """
    loader = DataLoader()
    results = {}
    
    # Firing rate threshold for Stable-Plus
    MIN_FR_HZ = 1.0
    
    for area in areas:
        log.progress(f"Analyzing E/I contributions for {area}")
        area_entries = loader.area_map.get(area, [])
        
        e_fr_stim = []
        i_fr_stim = []
        e_fr_omit = []
        i_fr_omit = []
        
        # We need both Stimulus (AAAB) and Omission (AXAB) to compute delta or raw responses
        spk_axab = loader.get_signal(mode="spk", condition="AXAB", area=area, align_to="omission")
        spk_aaab = loader.get_signal(mode="spk", condition="AAAB", area=area, align_to="omission")
        
        if not spk_axab or not spk_aaab:
            continue
            
        for i, entry in enumerate(area_entries):
            # Check blacklist
            ses = entry["session"]
            if ses in loader.BLACKLISTED_SESSIONS:
                continue
                
            probe = entry["probe"]
            
            # Arrays
            try:
                arr_ax = spk_axab[i]
                arr_aa = spk_aaab[i]
            except IndexError:
                continue
                
            if arr_ax.size == 0 or arr_aa.size == 0: continue
            
            # Load CSV
            df = loader.get_unit_metrics(ses)
            if df is None: continue
            
            # Filter for this probe
            # probe in mapping corresponds exactly to peak_channel_id // 128 and the NPY filename
            df['probe_idx'] = df['peak_channel_id'] // 128
            probe_df = df[df['probe_idx'] == probe].copy()
            probe_df = probe_df.sort_values('id').reset_index(drop=True)
            
            # Slice for the area (same logic as loader._load_data)
            n_total_units = len(probe_df)
            u_start = int(n_total_units * (entry["start_ch"] / entry["total_ch"]))
            u_end = int(n_total_units * (entry["end_ch"] / entry["total_ch"]))
            
            # Ensure slicing matches array shape exactly
            n_units_arr = arr_ax.shape[1]
            area_df = probe_df.iloc[u_start:u_start+n_units_arr].copy()
            
            if len(area_df) != n_units_arr:
                log.warning(f"Unit count mismatch in {area} {ses} p{probe}: CSV={len(area_df)}, ARR={n_units_arr}")
                # Fallback: slice directly from array size
                area_df = probe_df.iloc[u_start:u_start+n_units_arr].copy()
            
            # Classify
            area_df['putative_type'] = np.where(area_df['waveform_duration'] < 0.4, 'I', 'E')
            
            # Calculate FR in Stimulus (-1000 to -500) and Omission (0 to +500) windows
            # The returned array length is 2000 (pre_ms=1000, post_ms=1000)
            # Omission onset is exactly at index 1000.
            win_stim = slice(0, 500)     # -1000 to -500 relative to omission
            win_omit = slice(1000, 1500) # 0 to +500 relative to omission
            
            fr_ax_stim = np.mean(arr_ax[:, :, win_stim], axis=(0, 2)) * 1000
            fr_ax_omit = np.mean(arr_ax[:, :, win_omit], axis=(0, 2)) * 1000
            fr_aa_stim = np.mean(arr_aa[:, :, win_stim], axis=(0, 2)) * 1000
            fr_aa_omit = np.mean(arr_aa[:, :, win_omit], axis=(0, 2)) * 1000
            
            # Stable-Plus (fr > 1Hz in general)
            # Use max of any window to ensure we don't drop stimulus-only or omission-only units
            stable_mask = (np.maximum(fr_ax_stim, fr_ax_omit) > MIN_FR_HZ)
            
            e_mask = (area_df['putative_type'] == 'E').values & stable_mask
            i_mask = (area_df['putative_type'] == 'I').values & stable_mask
            
            # Store Omission Delta (AXAB - AAAB) for E and I
            delta_omit = fr_ax_omit - fr_aa_omit
            
            e_fr_omit.extend(delta_omit[e_mask])
            i_fr_omit.extend(delta_omit[i_mask])
            
        results[area] = {
            "e_delta": np.array(e_fr_omit),
            "i_delta": np.array(i_fr_omit),
            "e_count": len(e_fr_omit),
            "i_count": len(i_fr_omit),
            "e_mean": np.mean(e_fr_omit) if len(e_fr_omit) > 0 else 0.0,
            "i_mean": np.mean(i_fr_omit) if len(i_fr_omit) > 0 else 0.0,
            "e_sem": np.std(e_fr_omit) / np.sqrt(max(1, len(e_fr_omit))),
            "i_sem": np.std(i_fr_omit) / np.sqrt(max(1, len(i_fr_omit)))
        }
        log.info(f"  {area} - E: {results[area]['e_count']} units (Δ {results[area]['e_mean']:.2f}Hz), I: {results[area]['i_count']} units (Δ {results[area]['i_mean']:.2f}Hz)")

    return results
