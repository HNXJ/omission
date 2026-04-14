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

def compute_waveform_metrics(waveform: np.ndarray, fs: float = 30000.0) -> dict:
    """Computes waveform duration (trough-to-peak) and half-width (at half-maximal amplitude)."""
    print(f"""[action] Starting waveform metric computation""")
    
    # 1. Trough
    trough_idx = np.argmin(waveform)
    print(f"""[action] Found trough index: {trough_idx}""")
    
    # 2. Peak
    after_trough = waveform[trough_idx:]
    peak_idx = trough_idx + np.argmax(after_trough)
    print(f"""[action] Found peak index: {peak_idx}""")
    
    # 3. Duration: Trough to Peak
    duration_samples = peak_idx - trough_idx
    duration_ms = (duration_samples / fs) * 1000.0
    print(f"""[action] Calculated duration: {duration_ms} ms""")
    
    # 4. Half-Width
    trough_val = waveform[trough_idx]
    half_max = trough_val / 2.0
    print(f"""[action] Calculated half-max: {half_max}""")
    
    # Left crossing
    left_side = waveform[:trough_idx]
    left_cross = np.where(left_side >= half_max)[0]
    left_idx = left_cross[-1] if len(left_cross) > 0 else 0
    print(f"""[action] Found left crossing index: {left_idx}""")
    
    # Right crossing
    right_side = waveform[trough_idx:]
    right_cross = np.where(right_side >= half_max)[0]
    right_idx = trough_idx + (right_cross[0] if len(right_cross) > 0 else len(waveform)-1-trough_idx)
    print(f"""[action] Found right crossing index: {right_idx}""")
    
    hw_samples = right_idx - left_idx
    half_width_ms = (hw_samples / fs) * 1000.0
    print(f"""[action] Calculated half-width: {half_width_ms} ms""")
    
    return {"duration": duration_ms, "half_width": half_width_ms}

def classify_neurons(nwb_path: Path, out_dir: Path):
    """
    Computes waveform metrics and classifies units.
    Saves to: putative_typing/metrics_{session_id}.csv
    """
    with get_nwb_io(nwb_path) as (io, nwb):
        units = nwb.units.to_dataframe()
        
        metrics_list = []
        for unit_id, unit_data in units.iterrows():
            # In a real implementation, extract waveform mean from unit_data
            waveform = unit_data.get('waveform_mean', np.zeros(100))
            metrics = compute_waveform_metrics(waveform)
            
            metrics['unit_id'] = unit_id
            metrics['ei_type'] = 'narrow' if metrics['duration'] < 0.4 else 'wide'
            metrics_list.append(metrics)
        
        # Save metrics
        df = pd.DataFrame(metrics_list)
        out_path = out_dir / "putative_typing"
        out_path.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_path / f"metrics_{nwb_path.stem}.csv", index=False)
        print(f"[Saved] {nwb_path.stem} metrics")

if __name__ == "__main__":
    nwb_files = list(Path(r"D:\analysis\nwb").glob("*.nwb"))
    out_dir = PROJECT_ROOT / "outputs"
    for f in nwb_files:
        classify_neurons(f, out_dir)
