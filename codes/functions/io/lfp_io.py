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
import warnings

try:
    from pynwb import NWBHDF5IO  # type: ignore
    import pynwb.ecephys # Added this import
except ImportError:
    NWBHDF5IO = None

from codes.functions.lfp.lfp_constants import ALL_CONDITIONS
from codes.functions.lfp.lfp_laminar_mapping import CHANNEL_SPACING


def load_session(nwb_path: Path) -> Dict[str, Any]:
    """Load a session from NWB or return a stub structure."""
    session: Dict[str, Any] = {
        "nwb_path": nwb_path,
        "session_id": nwb_path.stem,
        "electrodes": pd.DataFrame(),
        "trials": pd.DataFrame(),
        "units": pd.DataFrame(), # Added for spiking unit data
        "areas": [],
        "channels": [],
        "photodiode": None,
        "lfp": None,
        "lfp_timestamps": None,
    }
    if not nwb_path.exists() or NWBHDF5IO is None:
        return session

    with NWBHDF5IO(str(nwb_path), "r") as io:
        nwb = io.read()
        # Minimal, conservative extraction; customize to your NWB layout.
        if hasattr(nwb, "electrodes"):
            session["electrodes"] = nwb.electrodes.to_dataframe().copy()
            # If 'depth' column is missing, estimate it from electrode index and CHANNEL_SPACING
            if 'depth' not in session["electrodes"].columns:
                print("Warning: 'depth' column not found in NWB electrodes table. Estimating depth from channel index.")
                # Assuming electrodes are ordered by depth
                session["electrodes"]['depth'] = session["electrodes"].index * CHANNEL_SPACING
        if hasattr(nwb, "trials") and nwb.trials is not None:
            session["trials"] = nwb.trials.to_dataframe().copy()
        if hasattr(nwb, "units") and nwb.units is not None: # Extract spiking unit data
            session["units"] = nwb.units.to_dataframe().copy()
            # If units are present, try to extract spike times into a list
            if 'spike_times' not in session['units'].columns:
                session['units']['spike_times'] = [
                    np.asarray(nwb.units.get_unit_spike_times(u_idx))
                    for u_idx in range(len(nwb.units))
                ]
            
        lfp_probes = [] # New structure to hold LFP data per probe
        # Try to find a single 'lfp' object first (original logic)
        if "lfp" in getattr(nwb, "acquisition", {}):
            lfp_obj = nwb.acquisition["lfp"]
            # Assuming 'lfp' object directly contains all channels and their electrodes
            # This case might need to be refined if 'lfp' itself is a collection of ElectricalSeries
            probe_entry = {
                'id': 'all', # A generic ID for this combined LFP
                'data': np.asarray(lfp_obj.data),
                'timestamps': np.asarray(lfp_obj.timestamps),
                # Need to map electrodes to this 'all' LFP if possible, or assume all electrodes are included
                'electrodes_ids': session["electrodes"].index.to_list() # Assuming all electrodes belong to this LFP
            }
            lfp_probes.append(probe_entry)
        
        # If not, try to find probe-specific LFP objects
        probe_keys = sorted([k for k in nwb.acquisition.keys() if "_lfp" in k and isinstance(nwb.acquisition[k], pynwb.ecephys.ElectricalSeries)])
        for key in probe_keys:
            lfp_obj = nwb.acquisition[key]
            
            # Extract electrode IDs associated with this ElectricalSeries
            # This assumes that lfp_obj.electrodes is a DynamicTableRegion
            # and that it contains references to the main electrodes table.
            if hasattr(lfp_obj, 'electrodes') and lfp_obj.electrodes is not None:
                # Get the electrode indices from the DynamicTableRegion
                electrode_indices = lfp_obj.electrodes.data[:]
                # Use these indices to get the corresponding original electrode IDs from session["electrodes"]
                # Assuming session["electrodes"]'s index matches the original NWB electrode IDs
                probe_electrode_ids = session["electrodes"].iloc[electrode_indices].index.to_list()
            else:
                probe_electrode_ids = [] # No specific electrodes found for this LFP object
            
            probe_entry = {
                'id': key.replace('_lfp', ''), # e.g., 'probe_0'
                'data': np.asarray(lfp_obj.data),
                'timestamps': np.asarray(lfp_obj.timestamps),
                'electrodes_ids': probe_electrode_ids
            }
            lfp_probes.append(probe_entry)
            
        if lfp_probes:
            # Check if all timestamps are the same
            first_timestamps = lfp_probes[0]['timestamps']
            for probe in lfp_probes[1:]:
                if not np.array_equal(first_timestamps, probe['timestamps']):
                    warnings.warn("LFP timestamps differ between probes. Using timestamps from the first probe.")
                    break
            
            all_lfp_data = [p['data'] for p in lfp_probes]
            
            # This assumes that the channels in each probe are exclusive
            # and that the order of probes is consistent.
            session['lfp'] = np.vstack(all_lfp_data)
            session['lfp_timestamps'] = first_timestamps

        
        if not session["electrodes"].empty:
            if "location" in session["electrodes"].columns:
                session["areas"] = sorted(session["electrodes"]["location"].dropna().astype(str).unique().tolist())
            session["channels"] = session["electrodes"].index.to_list()
    
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
