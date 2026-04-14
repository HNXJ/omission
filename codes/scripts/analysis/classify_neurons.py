#!/usr/bin/env python3
"""
Putative Classification Module
Extracts waveform metrics and classifies units into E/I types.
"""
from __future__ import annotations
import sys
import numpy as np
import pandas as pd
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(r"D:\drive\omission").resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from codes.functions.io.lfp_io import get_nwb_io
from codes.functions.lfp.lfp_constants import AREA_ALIAS_MAP

VERBOSITY_LEVEL = 1

def compute_waveform_metrics(waveform: np.ndarray, fs: float = 30000.0, verbosity: int = VERBOSITY_LEVEL) -> dict:
    """Computes waveform duration and half-width."""
    def log(msg, level):
        if verbosity >= level: print(f"""[action] {msg}""")
    
    log(f"""Starting waveform metric computation""", 2)
    
    trough_idx = np.argmin(waveform)
    log(f"""Found trough index: {trough_idx}""", 2)
    
    after_trough = waveform[trough_idx:]
    peak_idx = trough_idx + np.argmax(after_trough)
    log(f"""Found peak index: {peak_idx}""", 2)
    
    duration_samples = peak_idx - trough_idx
    duration_ms = (duration_samples / fs) * 1000.0
    log(f"""Calculated duration: {duration_ms} ms""", 2)
    
    trough_val = waveform[trough_idx]
    half_max = trough_val / 2.0
    log(f"""Calculated half-max: {half_max}""", 2)
    
    left_side = waveform[:trough_idx]
    left_cross = np.where(left_side >= half_max)[0]
    left_idx = left_cross[-1] if len(left_cross) > 0 else 0
    log(f"""Found left crossing index: {left_idx}""", 2)
    
    right_side = waveform[trough_idx:]
    right_cross = np.where(right_side >= half_max)[0]
    right_idx = trough_idx + (right_cross[0] if len(right_cross) > 0 else len(waveform)-1-trough_idx)
    log(f"""Found right crossing index: {right_idx}""", 2)
    
    hw_samples = right_idx - left_idx
    half_width_ms = (hw_samples / fs) * 1000.0
    log(f"""Calculated half-width: {half_width_ms} ms""", 2)
    
    return {"duration": duration_ms, "half_width": half_width_ms}

def classify_neurons(nwb_path: Path, out_dir: Path, verbosity: int = VERBOSITY_LEVEL):
    """Computes waveform metrics and classifies units."""
    with get_nwb_io(nwb_path) as (io, nwb):
        units = nwb.units.to_dataframe()
        
        metrics_list = []
        for unit_id, unit_data in units.iterrows():
            presence_ratio = float(unit_data.get('presence_ratio', 0.0))
            firing_rate = float(unit_data.get('firing_rate', 0.0))
            
            if presence_ratio <= 0.95 or firing_rate < 1.0:
                continue
            
            if verbosity >= 1: print(f"""[action] Processing unit {unit_id} (PR: {presence_ratio}, FR: {firing_rate})""")
            
            waveform = unit_data.get('waveform_mean', np.zeros(100))
            metrics = compute_waveform_metrics(waveform, verbosity=verbosity)
            
            metrics['unit_id'] = unit_id
            metrics['ei_type'] = 'narrow' if metrics['duration'] < 0.4 else 'wide'
            metrics_list.append(metrics)
        
        df = pd.DataFrame(metrics_list)
        out_path = out_dir / "putative_typing"
        out_path.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_path / f"metrics_{nwb_path.stem}.csv", index=False)
        if verbosity >= 1: print(f"""[Saved] {nwb_path.stem} metrics""")

if __name__ == "__main__":
    nwb_files = list(Path(r"D:\analysis\nwb").glob("*.nwb"))
    out_dir = PROJECT_ROOT / "outputs"
    for f in nwb_files:
        classify_neurons(f, out_dir)
