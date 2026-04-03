#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Any

import numpy as np

from codes.functions.lfp_io import load_session, save_json_manifest
from codes.functions.lfp_events import build_event_table
from codes.functions.lfp_preproc import preprocess_lfp, extract_epochs, baseline_normalize
from codes.functions.lfp_tfr import compute_tfr, collapse_band_power
from codes.functions.lfp_connectivity import compute_coherence, compute_granger
from codes.functions.lfp_stats import cluster_permutation_test, mean_sem
from codes.functions.lfp_plotting import plot_tfr_grid, plot_band_trajectories, plot_coherence_network
from codes.functions.lfp_constants import ALL_CONDITIONS, OMISSION_CONDITIONS, WHITE


def run_one_session(nwb_path: Path, out_dir: Path) -> Dict[str, Any]:
    session = load_session(nwb_path)
    events = build_event_table(session)
    lfp = preprocess_lfp(session.get("lfp"), session.get("channels"))
    epochs = extract_epochs(lfp, events)

    freqs, times, power = compute_tfr(epochs)
    bands = collapse_band_power(freqs, power)

    coh = None
    gc = None
    stats = cluster_permutation_test(power, power)

    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "session_id": session.get("session_id"),
        "nwb_path": str(nwb_path),
        "n_trials": int(len(session.get("trials", []))) if hasattr(session.get("trials"), "__len__") else 0,
        "bands": list(bands.keys()),
        "conditions": ALL_CONDITIONS,
        "omission_conditions": OMISSION_CONDITIONS,
        "stats": stats,
    }
    save_json_manifest(out_dir / "manifest.json", manifest)

    # Template figures (saved even if data are sparse)
    tfr_fig = plot_tfr_grid({"session": (freqs, times, power)})
    tfr_fig.write_html(out_dir / "tfr.html")
    try:
        tfr_fig.write_image(out_dir / "tfr.svg")
    except Exception:
        pass

    band_fig = plot_band_trajectories(bands)
    band_fig.write_html(out_dir / "bands.html")
    try:
        band_fig.write_image(out_dir / "bands.svg")
    except Exception:
        pass

    coh_fig = plot_coherence_network(np.array([]), band_name="beta")
    coh_fig.write_html(out_dir / "coherence.html")
    try:
        coh_fig.write_image(out_dir / "coherence.svg")
    except Exception:
        pass

    return {"manifest": manifest, "bands": bands, "freqs": freqs, "times": times, "power": power}


def main() -> None:
    parser = argparse.ArgumentParser(description="LFP omission pipeline skeleton")
    parser.add_argument("--nwb", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    run_one_session(args.nwb, args.out)


if __name__ == "__main__":
    main()
