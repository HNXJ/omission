#!/usr/bin/env python3
"""
Canonical Figure-6 TFR generator with enhanced logging and error handling.
Outputs area-condition-timewindow specific TFR band traces for the omission paper.
Outputs: .html, .svg, .png for each area-condition.
Aggregates across all available sessions in D:/analysis/nwb.
"""
from __future__ import annotations
import sys
import time
from datetime import datetime
from pathlib import Path

# Add repo root to sys.path
REPO_ROOT = Path(r"D:\drive\omission").resolve()
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, List, Optional, Tuple

from codes.functions.io.lfp_io import load_session
from codes.functions.lfp.lfp_tfr import compute_tfr
from codes.functions.lfp.lfp_constants import (
    CANONICAL_AREAS,
    AREA_ALIAS_MAP,
    SEQUENCE_TIMING_MS,
    BANDS,
)

# --- Logging Helper ---
def log(msg: str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)

# --- Configuration & Condition Mapping ---
CONDITION_MAP: Dict[str, List[int]] = {
    "AXAB": [3], "BXBA": [8], "RXRR": list(range(27, 35)), # P2
    "AAXB": [4], "BBXA": [9], "RRXR": [35, 37, 39, 41], # P3
    "AAAX": [5], "BBBX": [10], "RRRX": [36, 38, 40, 42] + list(range(43, 51)), # P4
}

WINDOW_LABELS: Dict[str, str] = {
    "AXAB": "d1p2d2", "BXBA": "d1p2d2", "RXRR": "d1p2d2",
    "AAXB": "d2p3d3", "BBXA": "d2p3d3", "RRXR": "d2p3d3",
    "AAAX": "d3p4d4", "BBBX": "d3p4d4", "RRRX": "d3p4d4",
}

FAMILY_TIMING: Dict[str, Dict[str, int]] = {
    "p2": {"omission_onset_ms": int(SEQUENCE_TIMING_MS["p2"]["start"]), "x0": -1031, "x1": 1031},
    "p3": {"omission_onset_ms": int(SEQUENCE_TIMING_MS["p3"]["start"]), "x0": -1031, "x1": 1031},
    "p4": {"omission_onset_ms": int(SEQUENCE_TIMING_MS["p4"]["start"]), "x0": -1031, "x1": 1031},
}

def get_condition_family(condition: str) -> str:
    if condition in ["AXAB", "BXBA", "RXRR"]: return "p2"
    if condition in ["AAXB", "BBXA", "RRXR"]: return "p3"
    if condition in ["AAAX", "BBBX", "RRRX"]: return "p4"
    return "p2"

# -----------------------------------------------------------------------------
# Core Processing Logic
# -----------------------------------------------------------------------------

def _find_interval_table(nwb) -> Optional[pd.DataFrame]:
    preferred = ["omission_glo_passive", "trials"]
    for name in preferred:
        if hasattr(nwb, "intervals") and name in nwb.intervals:
            return nwb.intervals[name].to_dataframe().copy()
    if hasattr(nwb, "trials") and nwb.trials is not None:
        return nwb.trials.to_dataframe().copy()
    return None

def _condition_name_from_number(value: object) -> str:
    try:
        number = int(float(value))
    except Exception: return "Unknown"
    for name, nums in CONDITION_MAP.items():
        if number in nums: return name
    return "Unknown"

def _extract_p1_trials(nwb_path: Path) -> pd.DataFrame:
    from pynwb import NWBHDF5IO
    with NWBHDF5IO(str(nwb_path), "r") as io:
        nwb = io.read()
        df = _find_interval_table(nwb)
    if df is None or df.empty: return pd.DataFrame()

    if "codes" in df.columns and "start_time" in df.columns:
        work = df.copy()
        work["codes_num"] = pd.to_numeric(work["codes"], errors="coerce")
        if "task_condition_number" in work.columns:
            work["condition"] = work["task_condition_number"].apply(_condition_name_from_number)
        else: work["condition"] = "Unknown"
        p1 = work[work["codes_num"] == 101].copy()
        if p1.empty: return pd.DataFrame()
        out = p1[["trial_num", "start_time", "condition"]].copy().rename(columns={"start_time": "p1_time"})
        return out.dropna(subset=["p1_time", "trial_num"])
    return pd.DataFrame()

def _area_channel_indices(electrodes_df: pd.DataFrame, area: str) -> np.ndarray:
    if electrodes_df.empty or "location" not in electrodes_df.columns: return np.array([], dtype=int)
    wanted = {area.strip(), AREA_ALIAS_MAP.get(area, area).strip()}
    mask = electrodes_df["location"].fillna("").astype(str).apply(lambda loc: any(tok.strip() in wanted for tok in loc.split(",")))
    return np.flatnonzero(mask.to_numpy())

def process_session_area_condition(session, nwb_path: Path, area: str, condition: str, baseline_ms: Tuple[int, int] = (-250, -50)):
    if session.get("lfp") is None: return None
    
    area_idx = _area_channel_indices(session["electrodes"], area)
    if area_idx.size == 0: return None

    lfp = session["lfp"]
    # Ensure lfp is (channels, time) - lfp_io.py should already provide this
    if lfp.shape[0] < lfp.shape[1] and lfp.shape[0] != len(session["electrodes"]):
        # This fallback shouldn't be needed with the fix in lfp_io.py
        pass 
    
    try:
        area_lfp = lfp[area_idx, :]
    except IndexError as e:
        log(f"   [Error] {area} indexing failed in {nwb_path.name}: {e}")
        return None
        
    timestamps = np.asarray(session["lfp_timestamps"])

    trial_df = _extract_p1_trials(nwb_path)
    trial_df = trial_df[trial_df["condition"] == condition].copy()
    if trial_df.empty: return None

    family = get_condition_family(condition)
    timing = FAMILY_TIMING[family]
    onsets_s = trial_df["p1_time"].to_numpy() + timing["omission_onset_ms"] / 1000.0
    
    x0, x1 = timing["x0"], timing["x1"]
    dt = np.mean(np.diff(timestamps))
    samples_per_epoch = int(round((x1 - x0) / 1000.0 / dt))
    
    epochs = []
    for onset_s in onsets_s:
        s_idx = np.searchsorted(timestamps, onset_s + x0/1000.0)
        e_idx = s_idx + samples_per_epoch
        if s_idx >= 0 and e_idx <= lfp.shape[1]:
            epochs.append(area_lfp[:, s_idx:e_idx])
    
    if not epochs: return None
    epochs_array = np.stack(epochs, axis=0)
    mean_epoch = np.nanmean(epochs_array, axis=1) # trials x time
    
    log(f"   [TFR] Computing for {area} {condition} ({len(epochs)} trials)")
    freqs, t_ms_epoch, power_db = compute_tfr(mean_epoch, fs=1000.0)
    t_ms_local = t_ms_epoch + x0
    
    power_linear = 10.0 ** (power_db / 10.0)
    b_mask = (t_ms_local >= baseline_ms[0]) & (t_ms_local <= baseline_ms[1])
    baseline = np.nanmean(power_linear[:, :, b_mask], axis=-1, keepdims=True)
    rel_db = 10.0 * np.log10(power_linear / (baseline + 1e-12) + 1e-12)
    
    band_traces = {}
    for b_name, (f0, f1) in BANDS.items():
        f_mask = (freqs >= f0) & (freqs <= f1)
        band_traces[b_name] = np.nanmean(np.nanmean(rel_db[:, f_mask, :], axis=1), axis=0)
    
    return {"time": t_ms_local, "bands": band_traces}

# -----------------------------------------------------------------------------
# Main Runner
# -----------------------------------------------------------------------------

def main():
    log("Starting Figure-6 TFR Generation Pipeline")
    nwb_dir = Path(r"D:\analysis\nwb")
    nwb_files = sorted(list(nwb_dir.glob("*.nwb")))
    out_dir = REPO_ROOT / "outputs" / "oglo-figures" / "figure-6"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    log(f"Found {len(nwb_files)} sessions in {nwb_dir}")
    
    results = {} # (area, condition) -> List[Dict]

    for i, nwb_path in enumerate(nwb_files, 1):
        log(f"[{i}/{len(nwb_files)}] Loading Session: {nwb_path.name}")
        start_time = time.time()
        try:
            session = load_session(nwb_path)
            if session.get("lfp") is None:
                log(f"   [Skip] No LFP data found.")
                continue
            
            log(f"   [Info] Channels: {session['lfp'].shape[0]}, Timepoints: {session['lfp'].shape[1]}")
            
            for area in CANONICAL_AREAS:
                for condition in CONDITION_MAP.keys():
                    res = process_session_area_condition(session, nwb_path, area, condition)
                    if res:
                        key = (area, condition)
                        if key not in results: results[key] = []
                        results[key].append(res)
            
            elapsed = time.time() - start_time
            log(f"   [Done] Session processed in {elapsed:.1f}s")
            
        except Exception as e:
            log(f"   [Error] Failed to process session: {e}")
            import traceback
            log(traceback.format_exc())

    # Aggregate and Plot
    log("\nAggregating results across all sessions...")
    for (area, condition), session_results in results.items():
        if not session_results: continue
        
        log(f"[Plot] Generating: {area}-{condition}")
        time_vec = session_results[0]["time"]
        band_agg = {}
        for b_name in BANDS.keys():
            valid_traces = [r["bands"][b_name] for r in session_results if r["bands"][b_name].shape == time_vec.shape]
            if not valid_traces: continue
            stack = np.stack(valid_traces)
            mean = np.nanmean(stack, axis=0)
            sem = np.nanstd(stack, axis=0) / np.sqrt(len(valid_traces))
            band_agg[b_name] = (mean, sem)
        
        # Plotting
        label = WINDOW_LABELS.get(condition, "local")
        base_name = f"{area}-{condition.lower()}-{label}"
        
        fig = go.Figure()
        band_colors = {"Theta": "#1f77b4", "Alpha": "#e377c2", "Beta": "#ff7f0e", "Gamma": "#2ca02c"}
        
        for b_name, (mean, sem) in band_agg.items():
            color = band_colors.get(b_name, "#000000")
            fig.add_trace(go.Scatter(x=time_vec, y=mean+sem, mode='lines', line=dict(width=0), showlegend=False, hoverinfo='skip'))
            fig.add_trace(go.Scatter(x=time_vec, y=mean-sem, mode='lines', fill='tonexty', fillcolor=f"rgba{tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.15,)}", line=dict(width=0), showlegend=False, hoverinfo='skip'))
            fig.add_trace(go.Scatter(x=time_vec, y=mean, mode='lines', line=dict(color=color, width=2), name=b_name))

        fig.add_vrect(x0=-500, x1=0, fillcolor="rgba(0,0,0,0.05)", line_width=0)
        fig.add_vrect(x0=0, x1=531, fillcolor="rgba(255,0,0,0.1)", line_width=0)
        fig.add_vline(x=0, line_dash="dash", line_color="black")
        
        fig.update_layout(
            template="plotly_white", title=f"{area} - {condition} TFR Band Traces",
            xaxis_title="Time from omission onset (ms)", yaxis_title="Power change (dB)",
            height=500, width=800
        )
        
        fig.write_html(str(out_dir / f"{base_name}.html"))
        fig.write_image(str(out_dir / f"{base_name}.svg"))
        fig.write_image(str(out_dir / f"{base_name}.png"))

    log(f"\nPipeline Complete. Outputs saved to {out_dir}")

if __name__ == "__main__":
    main()
