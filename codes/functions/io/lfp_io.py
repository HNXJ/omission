"""
lfp_io.py
I/O utilities for NWB-LFP data extraction and results saving.
Standardized for OMISSION 2026. Optimized for lazy PyNWB access.
"""
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Generator
import numpy as np
import pandas as pd
import json
import warnings
from contextlib import contextmanager

try:
    from pynwb import NWBHDF5IO  # type: ignore
    import pynwb.ecephys 
except ImportError:
    NWBHDF5IO = None

from codes.functions.lfp.lfp_constants import ALL_CONDITIONS
from codes.functions.lfp.lfp_laminar_mapping import CHANNEL_SPACING

# --- Lazy NWB Access Helpers ---

@contextmanager
def get_nwb_io(nwb_path: Path) -> Generator[Tuple[NWBHDF5IO, Any], None, None]:
    """Context manager for safe, lazy NWB IO."""
    if not nwb_path.exists() or NWBHDF5IO is None:
        raise FileNotFoundError(f"NWB file not found or pynwb not installed: {nwb_path}")
    
    io = NWBHDF5IO(str(nwb_path), "r", load_namespaces=True)
    try:
        nwb = io.read()
        yield io, nwb
    finally:
        io.close()

def load_trial_index(nwb) -> pd.DataFrame:
    """Read the trial interval table without full materialization if possible."""
    preferred = ["omission_glo_passive", "trials"]
    table = None
    for name in preferred:
        if hasattr(nwb, "intervals") and name in nwb.intervals:
            table = nwb.intervals[name]
            break
    if table is None and hasattr(nwb, "trials") and nwb.trials is not None:
        table = nwb.trials
    
    if table is None:
        return pd.DataFrame()
    
    df = table.to_dataframe()
    cols = [c for c in ["trial_num", "start_time", "stop_time", "codes", "task_condition_number"] if c in df.columns]
    return df[cols]

def load_electrode_map(nwb) -> pd.DataFrame:
    """Read electrodes table metadata."""
    if not hasattr(nwb, "electrodes") or nwb.electrodes is None:
        return pd.DataFrame()
    
    df = nwb.electrodes.to_dataframe()
    if 'depth' not in df.columns:
        df['depth'] = df.index * CHANNEL_SPACING
    return df

def get_lfp_handles(nwb) -> List[pynwb.ecephys.ElectricalSeries]:
    """Find all LFP acquisition objects without loading data."""
    lfp_probes = []
    # Prioritize probe-specific LFP objects
    probe_keys = sorted([k for k in nwb.acquisition.keys() if "lfp" in k.lower() and isinstance(nwb.acquisition[k], pynwb.ecephys.ElectricalSeries)])
    
    if probe_keys:
        for key in probe_keys:
            lfp_probes.append(nwb.acquisition[key])
    elif "lfp" in getattr(nwb, "acquisition", {}):
        lfp_probes.append(nwb.acquisition["lfp"])
        
    return lfp_probes

def slice_series(series: pynwb.ecephys.ElectricalSeries, t_start: float, t_end: float) -> np.ndarray:
    """Lazy slice of a TimeSeries object based on timestamps."""
    rate = series.rate or (1.0 / np.mean(np.diff(series.timestamps[:100]))) if series.timestamps is not None else 1000.0
    t0 = series.starting_time if series.starting_time is not None else (series.timestamps[0] if series.timestamps is not None else 0.0)
    
    idx_start = max(0, int((t_start - t0) * rate))
    idx_end = int((t_end - t0) * rate)
    
    # PyNWB/HDF5 slicing happens here (on disk)
    return series.data[idx_start:idx_end]

# --- Compatibility Layer (Less Eager) ---

# --- Metadata Loading (Context-Safe) ---

def load_session_metadata(nwb_path: Path) -> Dict[str, Any]:
    """
    Extract session metadata (trials, units, electrodes) without full LFP load.
    Ensures no IO objects are returned, making it safe for lazy workflows.
    """
    if not nwb_path.exists() or NWBHDF5IO is None:
        raise FileNotFoundError(f"NWB not found: {nwb_path}")

    with NWBHDF5IO(str(nwb_path), "r", load_namespaces=True) as io:
        nwb = io.read()
        
        # 1. Trial Metadata
        trials = load_trial_index(nwb)
        
        # 2. Units (Spikes) Metadata
        units = pd.DataFrame()
        if hasattr(nwb, "units") and nwb.units is not None:
            units = nwb.units.to_dataframe()
            
        # 3. Electrodes Metadata
        electrodes = load_electrode_map(nwb)
        
        # 4. Probe Metadata
        handles = get_lfp_handles(nwb)
        probes = []
        for h in handles:
            probes.append({
                "id": h.name,
                "description": h.description,
                "n_samples": h.data.shape[0],
                "n_channels": h.data.shape[1],
                "fs": h.rate or (1.0 / np.mean(np.diff(h.timestamps[:100]))),
                "electrode_ids": h.electrodes.data[:].tolist() if hasattr(h.electrodes, 'data') else [],
            })

        return {
            "session_id": nwb_path.stem,
            "trials": trials,
            "units": units,
            "electrodes": electrodes,
            "probes": probes,
            "fs_lfp": probes[0]["fs"] if probes else 1000.0
        }

def load_session(nwb_path: Path) -> Dict[str, Any]:
    """Compatibility wrapper for load_session_metadata."""
    return load_session_metadata(nwb_path)

# --- Extraction Utilities ---

def extract_lfp_chunk(handle: Any, starts: np.ndarray, length: int) -> np.ndarray:
    """
    Perform a vectorized (block) read from an ElectricalSeries.
    'starts' are sample indices. Returns (n_trials, n_channels, n_samples).
    """
    n_trials = len(starts)
    n_channels = handle.data.shape[1]
    
    # HDF5 performs best with contiguous blocks or specific hyperslabs.
    # For now, we iterate to avoid overloading RAM, but use slicing.
    out = np.empty((n_trials, n_channels, length), dtype=handle.data.dtype)
    for i, s in enumerate(starts):
        # Transpose to (channels, time) for pipeline consistency
        out[i] = handle.data[s : s + length, :].T
        
    return out

def load_condition_table(search_path: Path) -> pd.DataFrame:
    """Implement the missing condition table loader."""
    path = search_path / "condition_table.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()

# --- Utilities ---

def save_json_manifest(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=str)

def save_lfp_results(out_path: Path, data: dict, metadata: dict = None):
    """Saves spectral data and .metadata.json sidecar."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(out_path, data)
    if metadata:
        meta_path = out_path.with_suffix(".metadata.json")
        save_json_manifest(meta_path, metadata)
