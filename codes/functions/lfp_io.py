"""
lfp_io.py
I/O utilities for NWB-LFP data extraction and results saving.
Standardized for OMISSION 2026.
"""
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
import json

try:
    from pynwb import NWBHDF5IO  # type: ignore
except ImportError:
    NWBHDF5IO = None

from codes.functions.lfp_constants import ALL_CONDITIONS


def load_session(nwb_path: Path) -> Dict[str, Any]:
    """Load a session from NWB or return a stub structure."""
    session: Dict[str, Any] = {
        "nwb_path": nwb_path,
        "session_id": nwb_path.stem,
        "lfp": None,
        "electrodes": pd.DataFrame(),
        "trials": pd.DataFrame(),
        "units": pd.DataFrame(), # Added for spiking unit data
        "areas": [],
        "channels": [],
        "photodiode": None,
    }
    if not nwb_path.exists() or NWBHDF5IO is None:
        return session

    with NWBHDF5IO(str(nwb_path), "r") as io:
        nwb = io.read()
        # Minimal, conservative extraction; customize to your NWB layout.
        if hasattr(nwb, "electrodes"):
            session["electrodes"] = nwb.electrodes.to_dataframe().copy()
        if hasattr(nwb, "trials"):
            session["trials"] = nwb.trials.to_dataframe().copy()
        if hasattr(nwb, "units"): # Extract spiking unit data
            session["units"] = nwb.units.to_dataframe().copy()
            # If units are present, try to extract spike times into a list
            if 'spike_times' not in session['units'].columns:
                session['units']['spike_times'] = [
                    np.asarray(nwb.units.get_unit_spike_times(u_idx))
                    for u_idx in range(len(nwb.units))
                ]
            
        if "lfp" in getattr(nwb, "acquisition", {}):
            lfp_obj = nwb.acquisition["lfp"]
            session["lfp"] = np.asarray(lfp_obj.data)
        if not session["electrodes"].empty:
            if "location" in session["electrodes"].columns:
                session["areas"] = sorted(session["electrodes"]["location"].dropna().astype(str).unique().tolist())
            session["channels"] = session["electrodes"].index.to_list()
    
    # Mandatory Sanitation
    if session["lfp"] is not None:
        session["lfp"] = np.nan_to_num(session["lfp"])
        
    return session


def load_condition_table(root: Path) -> pd.DataFrame:
    """Load a per-trial condition table if present, otherwise return empty."""
    f = root / "condition_table.csv"
    if f.exists():
        return pd.read_csv(f)
    return pd.DataFrame(columns=["trial_id", "condition", "sequence", "omission_position"])


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
