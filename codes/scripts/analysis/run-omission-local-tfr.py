#!/usr/bin/env python3
import numpy as np
import os
import argparse
from pathlib import Path
from codes.functions.lfp.lfp_pipeline import get_signal_conditional
from codes.functions.lfp.lfp_tfr import compute_multitaper_tfr
from codes.functions.io.condition_mapping import get_canonical_condition_map

# Canonical Omission Constants
OMISSION_ONSET_MS = {
    "AXAB": 1031, "BXBA": 1031, "RXRR": 1031,
    "AAXB": 2062, "BBXA": 2062, "RRXR": 2062,
    "AAAX": 3093, "BBBX": 3093, "RRRX": 3093,
}

BANDS = {
    "Theta": (2, 7),
    "Alpha": (8, 12),
    "Beta": (13, 30),
    "Gamma": (32, 80),
}

def compute_omission_local_band_traces(nwb_path: Path, area: str, condition: str):
    # Load epoch
    epochs = get_signal_conditional(nwb_path, area, signal_type="LFP", epoch_window=(-1.0, 4.0))
    if epochs.size == 0: return None
    
    # 1. Align to local omission time
    n_time = epochs.shape[-1]
    times_ms_p1 = np.arange(n_time) - 1000.0
    omission_onset = OMISSION_ONSET_MS[condition]
    times_ms_local = times_ms_p1 - omission_onset
    
    # 2. Crop window
    keep = (times_ms_local >= -1000) & (times_ms_local <= 1000)
    times_ms_local = times_ms_local[keep]
    epochs = epochs[:, :, keep]
    
    # 3. Mean over channels
    x = np.nanmean(epochs, axis=1) # (trials, time)
    
    # 4. Compute TFR (multitaper)
    freqs, _, power = compute_multitaper_tfr(x, fs=1000.0)
    
    # 5. Baseline Normalization (-250 to -50ms)
    baseline_mask = (times_ms_local >= -250) & (times_ms_local <= -50)
    # power is trials x freqs x time (from multitaper)
    baseline = np.nanmean(power[:, :, :, baseline_mask], axis=-1, keepdims=True)
    rel_db = 10 * np.log10(power / (baseline + 1e-12))
    
    # 6. Collapse bands
    out = {"time_ms": times_ms_local, "bands": {}}
    for band_name, (f0, f1) in BANDS.items():
        fmask = (freqs >= f0) & (freqs <= f1)
        trial_band = np.nanmean(rel_db[:, :, fmask, :], axis=2) # mean over freqs
        out["bands"][band_name] = {
            "mean": np.nanmean(trial_band, axis=0),
            "sem": np.nanstd(trial_band, axis=0) / np.sqrt(trial_band.shape[0])
        }
    return out

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nwb", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    
    # Test execution
    res = compute_omission_local_band_traces(args.nwb, "V1", "AXAB")
    print(f"Traces computed: {res.keys() if res else 'None'}")

if __name__ == "__main__":
    main()
