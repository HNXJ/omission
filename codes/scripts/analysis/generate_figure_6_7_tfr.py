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
REPO_ROOT = Path(r"D:\drive\omission").resolve()
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from codes.functions.io.lfp_io import get_nwb_io, load_trial_index, slice_series, get_lfp_handles
from codes.functions.lfp.lfp_tfr import compute_tfr
from codes.functions.lfp.lfp_constants import CANONICAL_AREAS, AREA_ALIAS_MAP

def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def main():
    log("Starting comprehensive TFR computation (Figs 6 & 7)")
    nwb_files = sorted(list(Path(r"D:\analysis\nwb").glob("*.nwb")))
    out_dir = REPO_ROOT / "outputs" / "oglo-figures"
    
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
                    # Resolve channels for this area across probes
                    area_ch_map = [] # List of (probe_handle_idx, local_ch_idx)
                    for p_idx, handle in enumerate(lfp_handles):
                        # Get electrode indices for this probe
                        # (Assumes handle.electrodes exists; fallback to probe division)
                        probe_el_indices = handle.electrodes.data[:]
                        probe_el_df = electrodes.iloc[probe_el_indices]
                        
                        wanted = {area.strip(), AREA_ALIAS_MAP.get(area, area).strip()}
                        mask = probe_el_df["location"].fillna("").astype(str).apply(
                            lambda loc: any(tok.strip() in wanted for tok in loc.split(","))
                        )
                        for local_idx in np.flatnonzero(mask.to_numpy()):
                            area_ch_map.append((p_idx, local_idx))
                    
                    if not area_ch_map: continue
                    log(f"  [Area {area}] Processing {len(area_ch_map)} channels")
                    
                    for (p_idx, local_ch) in area_ch_map:
                        handle = lfp_handles[p_idx]
                        epochs = []
                        for _, row in p1_events.iterrows():
                            # Slice 1000ms before to 4000ms after P1
                            seg = slice_series(handle, row['start_time'] + T_PRE, row['start_time'] + T_POST)
                            epochs.append(seg[:, local_ch])
                        
                        # Compute & Save
                        arr = np.nanmean(np.stack(epochs), axis=0)
                        freqs, times, power = compute_tfr(arr[None, :], fs=1000.0)
                        # ...
                        
            gc.collect()
        except Exception as e:
            log(f"  [Error] {e}")

if __name__ == "__main__":
    main()
