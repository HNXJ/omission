#!/usr/bin/env python3
"""
Figure 6 & 7: Optimized TFR Analysis Generator (Lazy Block-Reads)
Computes channel-specific TFR (-1000ms to +4000ms from P1).
Verbosity: Extreme (Every line action-printed).
"""
from __future__ import annotations
import sys
import gc
import json
import time
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

# Setup paths
PROJECT_ROOT = Path(r"D:\drive\omission").resolve()
print(f"""[action] Setting project root to {PROJECT_ROOT}""")
if str(PROJECT_ROOT) not in sys.path:
    print(f"""[action] Inserting project root into sys.path""")
    sys.path.insert(0, str(PROJECT_ROOT))
DATA_DIR = Path(r"D:\analysis\nwb")
print(f"""[action] Setting data directory to {DATA_DIR}""")
OUTPUT_DIR = PROJECT_ROOT / "outputs"
print(f"""[action] Setting output directory to {OUTPUT_DIR}""")
DASHBOARD_STATEDIR = OUTPUT_DIR / "dashboard"
print(f"""[action] Setting dashboard state directory to {DASHBOARD_STATEDIR}""")
DASHBOARD_STATEDIR.mkdir(parents=True, exist_ok=True)
print(f"""[action] Created dashboard state directory if not exists""")

from codes.functions.io.lfp_io import get_nwb_io, load_trial_index, get_lfp_handles, extract_lfp_chunk
print(f"""[action] Imported IO functions""")
from codes.functions.lfp.lfp_tfr import compute_tfr
print(f"""[action] Imported TFR computation function""")
from codes.functions.lfp.lfp_constants import CANONICAL_AREAS, AREA_ALIAS_MAP
print(f"""[action] Imported constants and area maps""")

def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def update_status(status_dict):
    status_file = DASHBOARD_STATEDIR / "status.json"
    print(f"""[action] Updating status file at {status_file}""")
    with open(status_file, 'w') as f:
        print(f"""[action] Opening status file for writing""")
        json.dump({**status_dict, "timestamp": time.time()}, f)
        print(f"""[action] Dumped status to JSON""")

def main():
    log("Starting Optimized TFR computation (Probe-level saving)")
    nwb_files = sorted(list(DATA_DIR.glob("*.nwb")))
    print(f"""[action] Globbed {len(nwb_files)} NWB files""")
    
    out_dir = OUTPUT_DIR / "oglo-figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"""[action] Created output directory {out_dir}""")
    
    T_PRE, T_POST = -1.0, 4.0
    FS = 1000.0
    print(f"""[action] Set constants T_PRE={T_PRE}, T_POST={T_POST}, FS={FS}""")
    
    for n_idx, nwb_path in enumerate(nwb_files):
        log(f"--- Session {n_idx+1}/{len(nwb_files)}: {nwb_path.name} ---")
        try:
            with get_nwb_io(nwb_path) as (io, nwb):
                print(f"""[action] Opened NWB io handle for {nwb_path.name}""")
                electrodes = nwb.electrodes.to_dataframe()
                print(f"""[action] Converted electrodes to dataframe""")
                trials = load_trial_index(nwb)
                print(f"""[action] Loaded trial index""")
                lfp_handles = get_lfp_handles(nwb)
                print(f"""[action] Loaded LFP handles""")
                p1_events = trials[trials['codes'].astype(str).str.startswith('101')]
                print(f"""[action] Filtered P1 events""")
                
                for area in CANONICAL_AREAS:
                    print(f"""[action] Starting area loop for {area}""")
                    for h_idx, handle in enumerate(lfp_handles):
                        print(f"""[action] Processing handle index {h_idx}""")
                        p_indices = handle.electrodes.data[:]
                        print(f"""[action] Retrieved probe indices""")
                        p_df = electrodes.iloc[p_indices]
                        print(f"""[action] Indexed electrodes dataframe""")
                        wanted = {area.strip(), AREA_ALIAS_MAP.get(area, area).strip()}
                        print(f"""[action] Set target areas: {wanted}""")
                        mask = p_df["location"].fillna("").astype(str).apply(
                            lambda loc: any(tok.strip() in wanted for tok in loc.split(","))
                        )
                        print(f"""[action] Generated mask for area""")
                        target_ch_indices = np.flatnonzero(mask.to_numpy())
                        print(f"""[action] Found {len(target_ch_indices)} target channels""")
                        if target_ch_indices.size == 0:
                            print(f"""[action] Skipping probe with no target channels""")
                            continue
                        
                        log(f"  [Area] {area} | [Probe] {h_idx} ({len(target_ch_indices)} channels)")
                        
                        probe_power = []
                        print(f"""[action] Initialized probe power list""")
                        for ch in target_ch_indices:
                            print(f"""[action] Starting loop for channel {ch}""")
                            onsets = p1_events['start_time'].values
                            print(f"""[action] Extracted onsets""")
                            sample_starts = ((onsets + T_PRE) * FS).astype(int)
                            print(f"""[action] Calculated sample starts""")
                            sample_len = int((T_POST - T_PRE) * FS)
                            print(f"""[action] Calculated sample length""")
                            
                            epochs = extract_lfp_chunk(handle, sample_starts, sample_len)
                            print(f"""[action] Extracted LFP chunk""")
                            avg_trace = np.nanmean(epochs[:, ch, :], axis=0)
                            print(f"""[action] Calculated average trace""")
                            _, _, power = compute_tfr(avg_trace[None, :], fs=FS)
                            print(f"""[action] Computed TFR power""")
                            probe_power.append(power)
                            print(f"""[action] Appended power to probe list""")
                        
                        out_name = f"{area}_probe{h_idx}_sess{nwb_path.name[:8]}.npz"
                        print(f"""[action] Setting output filename to {out_name}""")
                        np.savez(out_dir / out_name, power=np.array(probe_power), channels=target_ch_indices)
                        print(f"""[action] Saved NPZ file to {out_dir / out_name}""")
                        log(f"    [Saved] {out_name}")
                        
                        gc.collect()
                        print(f"""[action] Garbage collected""")

        except Exception as e:
            log(f"  [Error] {nwb_path.name}: {e}")
            print(f"""[action] Logged error {e}""")
            
if __name__ == "__main__":
    main()
    print(f"""[action] Script execution completed""")
