from __future__ import annotations
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from codes.functions.io.lfp_io import (
    get_nwb_io, 
    load_session_metadata, 
    get_lfp_handles, 
    extract_lfp_chunk
)
from codes.functions.lfp.lfp_constants import ALL_CONDITIONS, CANONICAL_AREAS

def get_signal_conditional(
    session_path: Path, 
    area: str, 
    signal_type: str = 'LFP', 
    epoch_window: Tuple[float, float] = (-1.0, 4.0), 
    align_to: str = 'P1', 
    condition: Optional[str] = None,
    **kwargs
) -> np.ndarray:
    """
    Canonical, lazy accessor for neural signals from NWB.
    Encapsulates PyNWB IO context.
    """
    print(f"[infile] lfp_pipeline.py [doing] Extracting {signal_type} for {area} (Cond: {condition})")

    # 1. Load Metadata (Lightweight)
    meta = load_session_metadata(session_path)
    trials = meta["trials"]
    electrodes = meta["electrodes"]
    
    # 2. Filter Trials
    if condition:
        from codes.functions.lfp.lfp_constants import CONDITION_MAP
        valid_codes = CONDITION_MAP.get(condition, [])
        print(f"""[action] Mapping condition {condition} to codes {valid_codes}""")
        
        # Cast to float for comparison as column data is object/float
        trials['task_condition_number'] = pd.to_numeric(trials['task_condition_number'], errors='coerce')
        target_trials = trials[trials["task_condition_number"].isin(valid_codes)].copy()
        print(f"""[action] Found {len(target_trials)} matching trials""")
    else:
        target_trials = trials.copy()

    if target_trials.empty:
        print(f"   [Warning] No trials found for {condition}")
        return np.array([])

    # 3. Resolve Area/Electrode mapping
    area_mask = electrodes["location"].fillna("").astype(str).apply(
        lambda loc: area.strip() in [a.strip() for a in loc.split(",")]
    )
    global_ch_ids = electrodes.index[area_mask].tolist()
    
    if not global_ch_ids:
        print(f"   [Error] Area {area} not found in electrodes")
        return np.array([])

    # 4. Extract inside open IO context
    results = []
    with get_nwb_io(session_path) as (io, nwb):
        handles = get_lfp_handles(nwb)
        
        for h_idx, handle in enumerate(handles):
            # Map global electrode IDs to probe-local indices
            probe_ch_ids = handle.electrodes.data[:]
            local_mask = np.isin(probe_ch_ids, global_ch_ids)
            local_indices = np.where(local_mask)[0]
            
            if local_indices.size == 0:
                continue
                
            # Compute sample indices
            fs = handle.rate or 1000.0
            t0 = handle.starting_time or (handle.timestamps[0] if handle.timestamps is not None else 0.0)
            
            # Align times (e.g., Code 101 start_time)
            # Standardizing on start_time for now
            onsets = target_trials["start_time"].values
            sample_starts = ((onsets + epoch_window[0] - t0) * fs).astype(int)
            length = int((epoch_window[1] - epoch_window[0]) * fs)
            
            # Block Extraction
            # Note: We slice only the local_indices after block-reading for speed
            # extract_lfp_chunk currently returns (trials, channels, samples)
            # but it reads ALL channels on the probe to be efficient/simplified.
            # We filter for area-specific channels here.
            block = extract_lfp_chunk(handle, sample_starts, length) # (trials, probe_channels, samples)
            results.append(block[:, local_indices, :])

    if not results:
        return np.array([])
        
    # Combine probes if the area spans multiple (rare but possible)
    final_arr = np.concatenate(results, axis=1) # (trials, area_channels, samples)
    return final_arr
