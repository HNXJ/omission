#!/usr/bin/env python3
"""
Canonical Omission Analysis Pipeline.
Integrates Nitzan-like benchmark logic and Alpha-Beta mechanisms.
"""
from __future__ import annotations
import argparse
import numpy as np
from pathlib import Path
from codes.functions.lfp.lfp_pipeline import get_signal_conditional
from codes.functions.lfp.lfp_tfr import compute_multitaper_tfr, collapse_band_power
from codes.functions.io.lfp_io import save_lfp_results

def run_analysis(nwb_path: Path, output_dir: Path):
    """Executes canonical analysis for a given session."""
    areas = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']
    for area in areas:
        try:
            # Canonical epoch extraction
            epochs = get_signal_conditional(nwb_path, area, epoch_window=(-1.0, 4.0))
            if epochs.size == 0 or np.all(np.isnan(epochs)):
                continue
            
            # TFR computation
            # Averaging trials for now as per Nitzan-like benchmark pattern
            trial_avg = np.nanmean(epochs, axis=0) # (channels, time)
            freqs, times, power = compute_multitaper_tfr(trial_avg)
            
            # Band powers
            bands = collapse_band_power(freqs, power)
            
            # Save results
            out_name = output_dir / f"{nwb_path.stem}_{area}_analysis.npy"
            save_lfp_results(out_name, bands, metadata={"session": nwb_path.name, "area": area})
            print(f"[pipeline] Saved results for {area}")
            
        except Exception as e:
            print(f"[error] Failed {area}: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    
    nwb_dir = args.repo_root / ".." / "analysis" / "nwb"
    out_dir = args.repo_root / "outputs" / "reports" / "canonical_pipeline"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    for nwb in nwb_dir.glob("*.nwb"):
        run_analysis(nwb, out_dir)

if __name__ == "__main__":
    main()
