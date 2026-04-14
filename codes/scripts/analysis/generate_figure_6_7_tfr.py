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

from concurrent.futures import ProcessPoolExecutor
import multiprocessing

VERBOSITY_LEVEL = 2

def log(msg: str, level: int = 1):
    if VERBOSITY_LEVEL >= level:
        print(f"""[{datetime.now().strftime('%H:%M:%S')}] {msg}""", flush=True)

def process_session(nwb_path: Path):
    """Processes a single session to allow parallel execution."""
    out_dir = OUTPUT_DIR / "oglo-figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    T_PRE, T_POST = -1.0, 4.0
    FS = 1000.0
    
    try:
        with get_nwb_io(nwb_path) as (io, nwb):
            electrodes = nwb.electrodes.to_dataframe()
            trials = load_trial_index(nwb)
            lfp_handles = get_lfp_handles(nwb)
            p1_events = trials[trials['codes'].astype(str).str.startswith('101')]
            
            for area in CANONICAL_AREAS:
                for h_idx, handle in enumerate(lfp_handles):
                    p_indices = handle.electrodes.data[:]
                    p_df = electrodes.iloc[p_indices]
                    wanted = {area.strip(), AREA_ALIAS_MAP.get(area, area).strip()}
                    mask = p_df["location"].fillna("").astype(str).apply(
                        lambda loc: any(tok.strip() in wanted for tok in loc.split(","))
                    )
                    target_ch_indices = np.flatnonzero(mask.to_numpy())
                    if target_ch_indices.size == 0: continue
                    
                    probe_power = []
                    for ch in target_ch_indices:
                        onsets = p1_events['start_time'].values
                        sample_starts = ((onsets + T_PRE) * FS).astype(int)
                        sample_len = int((T_POST - T_PRE) * FS)
                        
                        epochs = extract_lfp_chunk(handle, sample_starts, sample_len)
                        avg_trace = np.nanmean(epochs[:, ch, :], axis=0)
                        _, _, power = compute_tfr(avg_trace[None, :], fs=FS)
                        probe_power.append(power)
                    
                    out_name = f"{area}_probe{h_idx}_sess{nwb_path.name[:8]}.npz"
                    np.savez(out_dir / out_name, power=np.array(probe_power), channels=target_ch_indices)
                    gc.collect()
        return f"Completed {nwb_path.name}"
    except Exception as e:
        return f"Error {nwb_path.name}: {e}"

def main():
    log("Starting Parallel TFR computation (A400-optimized)", 1)
    nwb_files = sorted(list(DATA_DIR.glob("*.nwb")))
    
    # Use max available cores
    max_workers = min(multiprocessing.cpu_count(), 8)
    print(f"""[action] Starting ProcessPoolExecutor with {max_workers} workers""")
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_session, nwb_files))
        
    for res in results:
        log(res, 1)
