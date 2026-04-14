#!/usr/bin/env python3
"""
Figure 6 & 7: TFR Analysis Generator
Computes channel-specific TFR (-1000ms to +4000ms from P1).
Performs dB-normalized TFR and saves .html/.svg/.png + compressed .npz.
"""
from __future__ import annotations
import sys
import gc
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime

# Setup paths
from codes.config.paths import PROJECT_ROOT, DATA_DIR, OUTPUT_DIR
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from codes.functions.io.lfp_io import get_nwb_io, load_trial_index, slice_series, get_lfp_handles
from codes.functions.lfp.lfp_tfr import compute_tfr
from codes.functions.lfp.lfp_constants import CANONICAL_AREAS, AREA_ALIAS_MAP

def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def main():
    log("Starting comprehensive TFR computation (Figs 6 & 7)")
    nwb_files = sorted(list(DATA_DIR.glob("*.nwb")))
    out_dir = OUTPUT_DIR / "oglo-figures"
    
    # Analysis specs
    T_PRE, T_POST = -1.0, 4.0
    
    for nwb_path in nwb_files:
        log(f"Processing session: {nwb_path.name}")
        try:
            with get_nwb_io(nwb_path) as (io, nwb):
                electrodes = nwb.electrodes.to_dataframe()
                trials = load_trial_index(nwb)
                lfp_handles = get_lfp_handles(nwb)
                
                # Align to P1 (Code 101)
                p1_events = trials[trials['codes'].astype(str).str.startswith('101')]
                
                for area in CANONICAL_AREAS:
                    area_ch_map = [] 
                    for p_idx, handle in enumerate(lfp_handles):
                        probe_el_indices = handle.electrodes.data[:]
                        probe_el_df = electrodes.iloc[probe_el_indices]
                        
                        wanted = {area.strip(), AREA_ALIAS_MAP.get(area, area).strip()}
                        mask = probe_el_df["location"].fillna("").astype(str).apply(
                            lambda loc: any(tok.strip() in wanted for tok in loc.split(","))
                        )
                        for local_idx in np.flatnonzero(mask.to_numpy()):
                            area_ch_map.append((p_idx, local_idx))
                    
                    if not area_ch_map: continue
                    
                    # Cache probe data for this session to speed up epoch extraction
                    probe_data_cache = {} 
                    
                    for (p_idx, local_ch) in area_ch_map:
                        if p_idx not in probe_data_cache:
                            log(f"    [Caching] Loading full data for probe {p_idx}")
                            probe_data_cache[p_idx] = lfp_handles[p_idx].data[:]
                        
                        handle_data = probe_data_cache[p_idx]
                        fs = 1000.0 # Standardized sampling
                        
                        epochs = []
                        for _, row in p1_events.iterrows():
                            s_idx = int((row['start_time'] + T_PRE) * fs)
                            e_idx = int((row['start_time'] + T_POST) * fs)
                            epochs.append(handle_data[s_idx:e_idx, local_ch])
                        
                        arr = np.nanmean(np.stack(epochs), axis=0)
                        freqs, times, power = compute_tfr(arr[None, :], fs=fs)
                        # ...
                        
            gc.collect()
        except Exception as e:
            log(f"  [Error] {e}")

if __name__ == "__main__":
    main()
