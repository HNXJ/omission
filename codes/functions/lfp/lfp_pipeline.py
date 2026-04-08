"""
lfp_pipeline.py
===============
15-step LFP-only analysis pipeline for the OGLO Visual Omission Paradigm.
Each step = one or two functions. All functions are self-contained and composable.
Designed to exactly reproduce the spectral/connectivity panels from:
  - Poster 01: "Neural Dynamics during Omission..."
  - Poster 02: "Omission Reveals the Functional Role..."

Data flow:
  Step  1 → validate_session_schema     → canonical session dict
  Step  2 → build_omission_windows      → event_table + windows dict
  Step  3 → run_lfp_qc                  → qc_report + cleaned lfp
  Step  4 → extract_matched_epochs      → epochs tensor per condition
  Step  5 → normalize_epochs            → baseline-normalized epochs
  Step  6 → compute_tfr_per_condition   → TFR per area per condition
  Step  7 → compute_band_contrast       → omission Δ-power per band
  Step  8 → compute_spectral_corr       → inter-area correlation matrices
  Step  9 → compute_all_pairs_coherence → coherence spectra all pairs
  Step 10 → build_coherence_network_data → adjacency matrices per band
  Step 11 → compute_spectral_granger    → directional GC matrices
  Step 12 → run_cluster_permutation     → statistical masks (from lfp_stats)
  Step 13 → aggregate_by_tier           → tier-wise summaries
  Step 14 → compute_post_omission_adapt → trial-progress traces
  Step 15 → write_analysis_manifest     → JSON + CSV reproducibility outputs

See: context/plans/15-step-lfp-pipeline.md for full documentation.
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy.signal import coherence as scipy_coherence, spectrogram

# ... (existing imports)

from codes.functions.lfp.lfp_mapping import resolve_area_membership

# ... (rest of imports)

# ─────────────────────────────────────────────────────────────────────────────
# CANONICAL ACCESSOR
# ─────────────────────────────────────────────────────────────────────────────

def get_signal_conditional(
    signal_type: str,
    condition: str,
    area: str,
    t_pre_ms: int = 1000,
    t_post_ms: int = 4000,
    align_event: str = "p1",
    target_fs: float = 1000.0,
    spike_bin_ms: float = 1.0,
    spike_smooth_ms: Optional[float] = None,
    session_paths: Optional[List[Path]] = None,
) -> Dict[str, Any]:
    """
    Canonical accessor for SPK, MUAe, or LFP data.
    """
    out = {
        "signal_type": signal_type,
        "condition": condition,
        "area": area,
        "align_event": align_event,
        "t_pre_ms": t_pre_ms,
        "t_post_ms": t_post_ms,
        "fs": target_fs,
        "times_ms": np.arange(-t_pre_ms, t_post_ms),
        "sessions": {}
    }

    # Placeholder: implementation needs to iterate over session_paths 
    # (or glob default data dir), use _resolve_area_channels_for_session, 
    # extract epochs using _epoch_analog_trials/_epoch_spike_trials, 
    # and fill out['sessions'][session_id].

    return out

def _normalize_session_token(session_id: str) -> str:
    # Extract 6-digit token from potential path/name
    import re
    match = re.search(r'\d{6}', session_id)
    return match.group(0) if match else session_id

def _normalize_area_label(area: str) -> str:
    # Alias logic
    from codes.functions.lfp.lfp_constants import AREA_ALIAS_MAP
    return AREA_ALIAS_MAP.get(area, area)

def _resolve_area_channels_for_session(session: Dict, area: str) -> Dict[int, List[int]]:
    # Use resolve_area_membership logic
    session_id = _normalize_session_token(session.get("session_id", ""))
    area = _normalize_area_label(area)
    membership = {}
    # Iterate probes...
    return membership

def summarize_conditional_signal(result: Dict) -> Dict:
    summary = {}
    for sid, sdata in result.get("sessions", {}).items():
        data = sdata.get("data")
        summary[sid] = {
            "n_trials": data.shape[0] if data is not None else 0,
            "n_features": data.shape[1] if data is not None else 0,
            "n_time": data.shape[2] if data is not None else 0
        }
    return summary

# ... (existing functions)


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — NWB LFP Schema Validator
# ─────────────────────────────────────────────────────────────────────────────

def validate_session_schema(session: Dict[str, Any]) -> Dict[str, Any]:
    """
    Step 1. Validate and canonicalize a session dict from load_session().
    Enforces the mandatory key set and infers omission positions per trial.

    Required keys (added with defaults if missing):
        session_id, nwb_path, lfp, electrodes, trials, areas,
        channels, photodiode, fs, channel_depths, channel_areas

    Parameters
    ----------
    session : dict — output of lfp_io.load_session()

    Returns
    -------
    dict — same structure, validated and cleaned
    dict — qc_flags: {key: issue_description} for any problems found

    Example
    -------
    >>> session = load_session(Path("session_230629.nwb"))
    >>> session, qc = validate_session_schema(session)
    >>> assert not qc, f"Schema issues: {qc}"
    """
    REQUIRED_KEYS = [
        "session_id", "nwb_path", "lfp", "electrodes", "trials",
        "areas", "channels", "photodiode",
    ]
    qc_flags: Dict[str, str] = {}

    # Fill missing keys with safe defaults
    defaults = {
        "session_id": "unknown",
        "nwb_path": None,
        "lfp": None,
        "electrodes": pd.DataFrame(),
        "trials": pd.DataFrame(),
        "areas": [],
        "channels": [],
        "photodiode": None,
        "fs": FS_LFP,
        "channel_depths": {},
        "channel_areas": {},
    }
    for key, default in defaults.items():
        if key not in session:
            session[key] = default
            qc_flags[key] = f"missing — defaulted to {type(default).__name__}"

    # Validate trials table schema
    required_trial_cols = ["trial_id", "condition", "omission_position"]
    if not session["trials"].empty:
        missing_cols = [c for c in required_trial_cols
                        if c not in session["trials"].columns]
        if missing_cols:
            qc_flags["trials"] = f"missing columns: {missing_cols}"
    else:
        qc_flags["trials"] = "empty — no trial data"

    # Validate LFP array
    if session["lfp"] is not None:
        lfp = np.asarray(session["lfp"], dtype=float)
        if np.all(lfp == 0):
            qc_flags["lfp"] = "all-zero array — possible loading error"
        elif np.mean(np.isnan(lfp)) > 0.1:
            qc_flags["lfp"] = f"{100*np.mean(np.isnan(lfp)):.1f}% NaN — check referencing"
        session["lfp"] = np.nan_to_num(lfp)

    # Build channel→area mapping from electrodes if available
    if not session["electrodes"].empty:
        et = session["electrodes"]
        if "location" in et.columns:
            session["channel_areas"] = et["location"].to_dict()
        if "depth" in et.columns:
            session["channel_depths"] = et["depth"].to_dict()

    return session, qc_flags


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — Event Timeline + Omission Window Builder
# ─────────────────────────────────────────────────────────────────────────────

def build_omission_windows(
    event_table: pd.DataFrame,
    omission_windows_ms: Optional[Dict[str, Tuple[int, int]]] = None,
) -> Dict[str, Any]:
    """
    Step 2. Build per-trial omission windows and ghost-signal markers.
    The "ghost" signal: omission timing = expected stimulus onset. Same gray
    screen, but predictive state differs. Must be preserved explicitly.

    Parameters
    ----------
    event_table : pd.DataFrame
        Output of lfp_events.build_event_table(). Required columns:
        trial_id, condition, event, aligned_ms.
    omission_windows_ms : dict {condition: (start_ms, end_ms)} or None
        Default uses SEQUENCE_TIMING for p2/p3/p4 windows.

    Returns
    -------
    dict with keys:
        'windows'      : {condition: (start_ms, end_ms)}
        'ghost_times'  : {condition: expected_onset_ms} — "ghost signal" anchors
        'stimulus_win' : (0, 531) — standard stimulus window
        'baseline_win' : (-500, 0) — pre-p1 baseline
        'by_trial'     : {trial_id: {window_type: (t0, t1)}}
    """
    DEFAULT_OMISSION_WINDOWS = OMISSION_PATCHES_MS
    GHOST_TIMES = {
        "RXRR": TIMING_MS["p2"],
        "AXAB": TIMING_MS["p2"],
        "RRXR": TIMING_MS["p3"],
        "AAXB": TIMING_MS["p3"],
        "RRRX": TIMING_MS["p4"],
        "AAAX": TIMING_MS["p4"],
    }

    windows = omission_windows_ms or DEFAULT_OMISSION_WINDOWS

    by_trial: Dict[int, Dict] = {}
    if not event_table.empty and "trial_id" in event_table.columns:
        for trial_id, grp in event_table.groupby("trial_id"):
            cond = grp["condition"].iloc[0] if "condition" in grp.columns else ""
            by_trial[int(trial_id)] = {
                "condition": cond,
                "stimulus_win": (0, TIMING_MS["d1"]),
                "baseline_win": (TIMING_MS["fx"], 0),
                "omission_win": windows.get(cond, None),
                "ghost_time_ms": GHOST_TIMES.get(cond, None),
            }

    return {
        "windows": windows,
        "ghost_times": GHOST_TIMES,
        "stimulus_win": (0, TIMING_MS["d1"]),
        "baseline_win": (TIMING_MS["fx"], 0),
        "by_trial": by_trial,
    }


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — LFP Quality Control
# ─────────────────────────────────────────────────────────────────────────────

def run_lfp_qc(
    lfp: np.ndarray,
    fs: float = FS_LFP,
    channel_ids: Optional[List[int]] = None,
    line_noise_hz: float = 60.0,
    flat_variance_thresh: float = 1e-6,
) -> Dict[str, Any]:
    """
    Step 3. Per-channel LFP quality control.
    Reports: variance, line noise burden, flat channels, NaN fraction.
    Called before bipolar referencing to identify channels to exclude.

    Parameters
    ----------
    lfp              : np.ndarray, shape (n_channels, n_times)
    fs               : float — sampling rate (Hz)
    channel_ids      : list of int or None
    line_noise_hz    : float — frequency to check for line noise (default 60Hz)
    flat_variance_thresh : float — channels below this variance are flagged flat

    Returns
    -------
    dict:
        'channel_variance'   : np.ndarray(n_ch) — per-channel variance
        'flat_channels'      : list of int — indices of flat/dead channels
        'noisy_channels'     : list of int — high line-noise channels
        'nan_fraction'       : float — fraction of NaN samples
        'n_good_channels'    : int
        'passed'             : bool — True if <10% channels are bad

    Example
    -------
    >>> qc = run_lfp_qc(session['lfp'], fs=FS_LFP)
    >>> if not qc['passed']:
    ...     print(f"QC fail: {len(qc['flat_channels'])} flat channels")
    """
    if lfp is None or lfp.size == 0:
        return {"passed": False, "nan_fraction": 1.0, "n_good_channels": 0,
                "flat_channels": [], "noisy_channels": [],
                "channel_variance": np.array([])}

    n_ch, n_t = lfp.shape if lfp.ndim == 2 else (1, lfp.size)
    if lfp.ndim == 1:
        lfp = lfp[None, :]

    nan_frac = float(np.mean(np.isnan(lfp)))
    lfp_clean = np.nan_to_num(lfp)

    variance = np.var(lfp_clean, axis=-1)
    flat_ch  = [int(i) for i in np.where(variance < flat_variance_thresh)[0]]

    # Line noise: power in ±2Hz band around line_noise_hz
    try:
        from scipy.signal import periodogram
        noisy_ch = []
        for ch in range(n_ch):
            f, pxx = periodogram(lfp_clean[ch], fs=fs)
            line_band = (f >= line_noise_hz - 2) & (f <= line_noise_hz + 2)
            broad_band = (f >= 5) & (f <= fs / 2 - 5)
            if pxx[line_band].mean() > 10 * pxx[broad_band].mean():
                noisy_ch.append(ch)
    except Exception:
        noisy_ch = []

    bad_ch = set(flat_ch) | set(noisy_ch)
    n_good = n_ch - len(bad_ch)
    passed = len(bad_ch) / max(1, n_ch) < 0.10  # <10% bad channels

    return {
        "passed": passed,
        "channel_variance": variance,
        "flat_channels": flat_ch,
        "noisy_channels": noisy_ch,
        "nan_fraction": nan_frac,
        "n_good_channels": n_good,
        "n_channels": n_ch,
        "bad_channel_fraction": len(bad_ch) / max(1, n_ch),
    }


# ─────────────────────────────────────────────────────────────────────────────
# STEP 4 — Matched Epoch Extractor
# ─────────────────────────────────────────────────────────────────────────────

def extract_matched_epochs(
    lfp_by_area: Dict[str, np.ndarray],
    event_table: pd.DataFrame,
    omission_windows: Dict[str, Any],
    window_ms: Tuple[int, int] = (-500, 4200),
    fs: float = FS_LFP,
    min_trials: int = 10,
) -> Dict[str, Dict[str, np.ndarray]]:
    """
    Step 4. Extract trial-aligned LFP epochs per condition per area.
    For each omission trial, also extracts a MATCHED control window from the
    corresponding delay period of a standard (non-omission) trial.

    Parameters
    ----------
    lfp_by_area  : dict {area: np.ndarray(n_channels, n_total_times)}
    event_table  : pd.DataFrame with columns: trial_id, condition, aligned_ms
    omission_windows : output of build_omission_windows()
    window_ms    : (pre_ms, post_ms) relative to p1 onset. Default (-500, 4200).
    fs           : float — sampling rate
    min_trials   : int — warn if fewer trials found for a condition

    Returns
    -------
    dict {area: {condition: np.ndarray(n_trials, n_channels, n_times)}}

    Note
    ----
    Assumes lfp_by_area arrays are pre-aligned (sample index 0 = trial start).
    Replace array indexing with proper NWB time → sample conversion in production.
    """
    pre_ms, post_ms = window_ms
    n_times = int((post_ms - pre_ms) * fs / 1000)

    # Get trial onset indices from event_table
    p1_events = event_table[event_table["event"] == "p1"] if not event_table.empty else pd.DataFrame()
    all_conds  = event_table["condition"].unique() if not event_table.empty else []

    epochs: Dict[str, Dict[str, np.ndarray]] = {}

    for area, lfp in lfp_by_area.items():
        lfp = np.nan_to_num(np.asarray(lfp, dtype=float))
        n_ch = lfp.shape[0] if lfp.ndim == 2 else 1
        if lfp.ndim == 1:
            lfp = lfp[None, :]

        epochs[area] = {}
        for cond in all_conds:
            cond_trials = p1_events[p1_events["condition"] == cond]
            trial_epochs = []

            for _, row in cond_trials.iterrows():
                onset_sample = int(row.get("time_ms", 0) * fs / 1000)
                pre_sample   = int(pre_ms * fs / 1000)
                start = onset_sample + pre_sample
                end   = start + n_times

                if start < 0 or end > lfp.shape[-1]:
                    continue
                trial_epochs.append(lfp[:, start:end])

            if len(trial_epochs) < min_trials:
                warnings.warn(f"{area}/{cond}: only {len(trial_epochs)} trials "
                              f"(min={min_trials})", RuntimeWarning)

            if trial_epochs:
                epochs[area][cond] = np.stack(trial_epochs, axis=0)
            else:
                epochs[area][cond] = np.empty((0, n_ch, n_times))

    return epochs


# ─────────────────────────────────────────────────────────────────────────────
# STEP 5 — Baseline Normalization
# ─────────────────────────────────────────────────────────────────────────────

def normalize_epochs(
    epochs_by_area: Dict[str, Dict[str, np.ndarray]],
    baseline_win_ms: Tuple[int, int] = (-500, 0),
    fs: float = FS_LFP,
    pre_offset_ms: int = -500,
    method: str = "db",
) -> Dict[str, Dict[str, np.ndarray]]:
    """
    Step 5. Normalize all epochs relative to pre-p1 baseline.
    Operates in place on band-power or raw epoch arrays.

    Parameters
    ----------
    epochs_by_area : dict {area: {condition: array(n_trials, n_ch, n_times)}}
    baseline_win_ms : (start_ms, end_ms) relative to p1 onset (default -500..0)
    fs             : sampling rate
    pre_offset_ms  : ms offset applied to epoch window (usually -500 = window start)
    method         : 'db' — 10*log10(P/Pbase) [default, matches poster normalization]
                     'pct' — 100*(P-Pbase)/Pbase [percent change]
                     'zscore' — (P-mean_base)/std_base [trial-wise z-score]

    Returns
    -------
    dict — same structure as input, values replaced with normalized arrays
    """
    t0_sample = int((baseline_win_ms[0] - pre_offset_ms) * fs / 1000)
    t1_sample = int((baseline_win_ms[1] - pre_offset_ms) * fs / 1000)

    normed: Dict[str, Dict[str, np.ndarray]] = {}
    for area, cond_dict in epochs_by_area.items():
        normed[area] = {}
        for cond, epochs in cond_dict.items():
            if epochs.size == 0:
                normed[area][cond] = epochs
                continue
            e = np.asarray(epochs, dtype=float)
            # Baseline slice along last axis
            s0 = max(0, t0_sample)
            s1 = min(e.shape[-1], t1_sample) if t1_sample > 0 else e.shape[-1]
            base = np.nanmean(e[..., s0:s1], axis=-1, keepdims=True)
            base = np.where(np.abs(base) < 1e-12, 1e-12, base)

            if method == "db":
                normed[area][cond] = 10.0 * np.log10(
                    np.abs(e) / (np.abs(base) + 1e-12) + 1e-12)
            elif method == "pct":
                normed[area][cond] = 100.0 * (e - base) / (np.abs(base) + 1e-9)
            elif method == "zscore":
                std_base = np.nanstd(e[..., s0:s1], axis=-1, keepdims=True)
                std_base = np.where(std_base < 1e-12, 1e-12, std_base)
                normed[area][cond] = (e - base) / std_base
            else:
                raise ValueError(f"method must be 'db','pct','zscore'; got '{method}'")

    return normed


# ─────────────────────────────────────────────────────────────────────────────
# STEP 6 — Per-Condition TFR
# ─────────────────────────────────────────────────────────────────────────────

def compute_tfr_per_condition(
    epochs_by_area: Dict[str, Dict[str, np.ndarray]],
    fs: float = FS_LFP,
    nperseg: int = DEFAULT_WF_PARAMS["nperseg"],
    noverlap: int = DEFAULT_WF_PARAMS["noverlap"],
    freq_range: Tuple[float, float] = (1.0, 150.0),
) -> Dict[str, Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray]]]:
    """
    Step 6. Compute TFR (Hanning window, 98% overlap) per area per condition.
    Collapses over trials (mean) and channels (mean) before spectral estimate.
    This is the spectrogram shown in the poster's main LFP figure.

    Parameters
    ----------
    epochs_by_area : dict {area: {condition: array(n_trials, n_ch, n_times)}}
    fs             : float — sampling rate
    nperseg        : int — FFT window length (default 256 → 256ms resolution)
    noverlap       : int — overlap (default 251 = 98%)
    freq_range     : (flo, fhi) — Hz range to return

    Returns
    -------
    dict {area: {condition: (freqs, times_ms, power_db)}}
        freqs : shape (n_freqs,)
        times_ms : shape (n_times_out,) — in milliseconds
        power_db : shape (n_freqs, n_times_out) — dB scale

    Note
    ----
    For baseline correction, pass baseline-normalized epochs (Step 5 output).
    """
    tfr: Dict[str, Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray]]] = {}

    for area, cond_dict in epochs_by_area.items():
        tfr[area] = {}
        for cond, epochs in cond_dict.items():
            if epochs.size == 0:
                tfr[area][cond] = (np.array([]), np.array([]), np.array([[]]))
                continue
            # Mean across trials and channels → 1D signal
            sig = np.nanmean(epochs, axis=(0, 1))
            f, t, sxx = spectrogram(
                sig, fs=fs,
                window=DEFAULT_WF_PARAMS["window"],
                nperseg=nperseg, noverlap=noverlap,
                scaling="density", mode="psd",
            )
            f_mask = (f >= freq_range[0]) & (f <= freq_range[1])
            f_out  = f[f_mask]
            pxx    = sxx[f_mask, :]
            pxx_db = 10.0 * np.log10(np.abs(pxx) + 1e-12)
            t_ms   = t * 1000.0
            tfr[area][cond] = (f_out, t_ms, pxx_db)

    return tfr


# ─────────────────────────────────────────────────────────────────────────────
# STEP 7 — Band Power Contrast
# ─────────────────────────────────────────────────────────────────────────────

def compute_band_contrast(
    tfr_by_area: Dict[str, Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray]]],
    omission_cond: str,
    control_cond: str,
    bands: Optional[Dict[str, Tuple[int, int]]] = None,
    window_ms: Optional[Tuple[int, int]] = None,
) -> Dict[str, Dict[str, np.ndarray]]:
    """
    Step 7. Compute band-power omission contrast (omission – control) per area.
    This is the data behind the poster's main finding:
    "Omission dampens low-frequency oscillations; gamma unaffected."

    Parameters
    ----------
    tfr_by_area  : dict {area: {condition: (freqs, times_ms, power_db)}}
                   Output of compute_tfr_per_condition (Step 6).
    omission_cond : str  — e.g. 'RXRR'
    control_cond  : str  — e.g. 'RRRR'
    bands        : dict {band_name: (flo, fhi)} — default: BANDS from constants
    window_ms    : (t0, t1) ms range to average over — None = full time axis

    Returns
    -------
    dict {area: {band: delta_array}}
        delta_array: shape (n_times_out,) — omission minus control power (dB)

    Interpretation
    --------------
    Negative delta in Beta/Alpha = dampening during omission (Poster 02 finding).
    Near-zero delta in Gamma = gamma stability during omission.
    """
    if bands is None:
        bands = BANDS

    contrast: Dict[str, Dict[str, np.ndarray]] = {}

    for area in tfr_by_area:
        if omission_cond not in tfr_by_area[area]:
            continue
        if control_cond not in tfr_by_area[area]:
            continue

        freqs, times_ms, pwr_omit = tfr_by_area[area][omission_cond]
        _,     _,        pwr_ctrl = tfr_by_area[area][control_cond]

        if freqs.size == 0:
            continue

        # Time mask
        if window_ms:
            t_mask = (times_ms >= window_ms[0]) & (times_ms <= window_ms[1])
        else:
            t_mask = np.ones(len(times_ms), dtype=bool)

        contrast[area] = {}
        for band, (flo, fhi) in bands.items():
            f_mask = (freqs >= flo) & (freqs <= fhi)
            if not np.any(f_mask):
                contrast[area][band] = np.array([0.0])
                continue
            omit_band = np.nanmean(pwr_omit[f_mask, :], axis=0)
            ctrl_band = np.nanmean(pwr_ctrl[f_mask, :], axis=0)
            delta = omit_band - ctrl_band
            contrast[area][band] = delta[t_mask]

    return contrast


# ─────────────────────────────────────────────────────────────────────────────
# STEP 8 — Spectral Correlation Matrix
# ─────────────────────────────────────────────────────────────────────────────

def compute_spectral_corr(
    band_power_by_area: Dict[str, np.ndarray],
    areas: List[str],
    window_slice: Optional[Tuple[int, int]] = None,
) -> np.ndarray:
    """
    Step 8. Compute n_areas × n_areas inter-area spectral power correlation.
    Used to build the heatmap matrices shown in Poster 01 Section 6.

    Parameters
    ----------
    band_power_by_area : dict {area: array(n_trials, n_times)}
        Per-trial LFP band power in the relevant window.
    areas              : list — controls matrix row/column ordering
    window_slice       : (t0_idx, t1_idx) — sample indices to average over.
                         None = average over full time dimension.

    Returns
    -------
    np.ndarray, shape (n_areas, n_areas) — Pearson correlation matrix

    How to build band_power_by_area
    ---------------------------------
    For each condition and band:
    >>> epochs_normed = normalize_epochs(epochs, method='db')
    >>> tfr = compute_tfr_per_condition(epochs_normed)
    >>> for area in AREA_ORDER:
    ...     freqs, times, pwr = tfr[area]['RRRR']
    ...     f_mask = (freqs >= 13) & (freqs <= 30)  # beta
    ...     band_power_by_area[area] = pwr[f_mask, :].mean(0)[None, :]  # 1 × T
    """
    n = len(areas)
    corr = np.full((n, n), np.nan)

    # Build area × time matrix
    rows = []
    valid_areas = []
    for area in areas:
        if area not in band_power_by_area:
            continue
        pwr = np.asarray(band_power_by_area[area], dtype=float)
        if pwr.ndim == 2:
            if window_slice:
                v = np.nanmean(pwr[:, window_slice[0]:window_slice[1]], axis=1)
            else:
                v = np.nanmean(pwr, axis=1)
        else:
            v = pwr.ravel()
        rows.append(v)
        valid_areas.append(area)

    if len(rows) < 2:
        return corr

    matrix = np.vstack(rows)  # (n_valid, n_values)
    sub_corr = np.corrcoef(matrix)  # (n_valid, n_valid)

    # Place back into full area-ordered matrix
    for i, ai in enumerate(valid_areas):
        for j, aj in enumerate(valid_areas):
            ri = areas.index(ai)
            rj = areas.index(aj)
            corr[ri, rj] = sub_corr[i, j]

    return corr


# ─────────────────────────────────────────────────────────────────────────────
# STEP 9 — All-Pairs Coherence
# ─────────────────────────────────────────────────────────────────────────────

def compute_all_pairs_coherence(
    lfp_by_area: Dict[str, np.ndarray],
    areas: List[str],
    fs: float = FS_LFP,
    nperseg: int = DEFAULT_WF_PARAMS["nperseg"],
    freq_range: Tuple[float, float] = (1.0, 100.0),
) -> Dict[Tuple[str, str], Tuple[np.ndarray, np.ndarray]]:
    """
    Step 9. Compute coherence spectra for all area pairs using scipy.signal.coherence.
    Uses bipolar-referenced LFP signals (mean across channels per area).

    Parameters
    ----------
    lfp_by_area : dict {area: array(n_channels, n_times) or (n_times,)}
    areas       : list — controls which pairs are computed
    fs          : float — sampling rate
    nperseg     : int — window length for coherence estimate
    freq_range  : (flo, fhi) — Hz range to return

    Returns
    -------
    dict {(area_i, area_j): (freqs, cxy)} for all i < j pairs
        freqs : shape (n_freqs,)
        cxy   : shape (n_freqs,) — squared coherence [0, 1]

    Example
    -------
    >>> coh = compute_all_pairs_coherence(lfp_by_area, AREA_ORDER)
    >>> # Get beta-band coherence between V1 and PFC:
    >>> freqs, cxy = coh[('V1', 'PFC')]
    >>> beta_mask = (freqs >= 13) & (freqs <= 30)
    >>> print(f"V1-PFC beta coherence: {cxy[beta_mask].mean():.3f}")
    """
    results: Dict[Tuple[str, str], Tuple[np.ndarray, np.ndarray]] = {}
    valid_areas = [a for a in areas if a in lfp_by_area]

    for i in range(len(valid_areas)):
        for j in range(i + 1, len(valid_areas)):
            ai, aj = valid_areas[i], valid_areas[j]
            s1 = np.asarray(lfp_by_area[ai], dtype=float)
            s2 = np.asarray(lfp_by_area[aj], dtype=float)

            # Collapse to 1D (mean over channels)
            if s1.ndim == 2: s1 = np.nanmean(s1, axis=0)
            if s2.ndim == 2: s2 = np.nanmean(s2, axis=0)

            n = min(len(s1), len(s2))
            if n < nperseg * 2:
                continue
            s1, s2 = s1[:n], s2[:n]

            try:
                f, cxy = scipy_coherence(s1, s2, fs=fs, nperseg=nperseg,
                                         noverlap=int(nperseg * 0.98))
                f_mask = (f >= freq_range[0]) & (f <= freq_range[1])
                results[(ai, aj)] = (f[f_mask], cxy[f_mask])
            except Exception as e:
                warnings.warn(f"Coherence failed for {ai}-{aj}: {e}", RuntimeWarning)

    return results


# ─────────────────────────────────────────────────────────────────────────────
# STEP 10 — Coherence Network Adjacency
# ─────────────────────────────────────────────────────────────────────────────

def build_coherence_network_data(
    coh_pairs: Dict[Tuple[str, str], Tuple[np.ndarray, np.ndarray]],
    areas: List[str],
    band: str = "Beta",
    bands: Optional[Dict[str, Tuple[int, int]]] = None,
) -> np.ndarray:
    """
    Step 10. Collapse all-pairs coherence into a band-limited adjacency matrix.
    Feed the output directly into plot_spectral_network() from poster_figures.py.

    Parameters
    ----------
    coh_pairs  : output of compute_all_pairs_coherence (Step 9)
    areas      : list — sets matrix dimension and ordering
    band       : str — 'Theta','Alpha','Beta','Gamma'
    bands      : dict {band: (flo, fhi)} — default: BANDS from constants

    Returns
    -------
    np.ndarray, shape (n_areas, n_areas) — symmetric coherence matrix [0, 1]

    Example
    -------
    >>> adj_beta = build_coherence_network_data(coh_pairs, AREA_ORDER, band='Beta')
    >>> adj_gamma = build_coherence_network_data(coh_pairs, AREA_ORDER, band='Gamma')
    >>> # Difference matrix (omission vs stimulus)
    >>> adj_diff = adj_omit_beta - adj_stim_beta
    >>> fig = plot_spectral_network(adj_diff, areas=AREA_ORDER, band_label='Beta')
    """
    if bands is None:
        bands = BANDS
    flo, fhi = bands[band]

    n = len(areas)
    adj = np.zeros((n, n))

    for (ai, aj), (freqs, cxy) in coh_pairs.items():
        if ai not in areas or aj not in areas or freqs.size == 0:
            continue
        f_mask = (freqs >= flo) & (freqs <= fhi)
        if not np.any(f_mask):
            continue
        mean_coh = float(np.nanmean(cxy[f_mask]))
        ri, rj   = areas.index(ai), areas.index(aj)
        adj[ri, rj] = mean_coh
        adj[rj, ri] = mean_coh

    return adj


# ─────────────────────────────────────────────────────────────────────────────
# STEP 11 — Spectral Granger Causality
# ─────────────────────────────────────────────────────────────────────────────

def compute_spectral_granger(
    sig_source: np.ndarray,
    sig_target: np.ndarray,
    fs: float = FS_LFP,
    max_lag: int = 50,
    freq_range: Tuple[float, float] = (1.0, 100.0),
    n_freqs: int = 256,
) -> Dict[str, Any]:
    """
    Step 11. Spectral Granger causality via bivariate VAR model.
    Tests whether sig_source Granger-causes sig_target in the spectral domain.
    Directional: source → target vs target → source.

    Parameters
    ----------
    sig_source : np.ndarray, shape (n_times,) — "driver" area signal
    sig_target : np.ndarray, shape (n_times,) — "receiver" area signal
    fs         : float — sampling rate
    max_lag    : int — max VAR lag order to test (in samples). Default 50ms.
    freq_range : (flo, fhi) — Hz range for output
    n_freqs    : int — number of frequency bins in output

    Returns
    -------
    dict:
        'freqs'     : np.ndarray — frequency axis
        'gc_xy'     : np.ndarray — Granger causality X→Y (source→target)
        'gc_yx'     : np.ndarray — Granger causality Y→X (target→source)
        'net_dir'   : np.ndarray — gc_xy - gc_yx (positive = feedforward)
        'best_lag'  : int — optimal VAR lag order (AIC)

    Algorithm (spectral Granger via VAR)
    -------------------------------------
    1. Fit bivariate VAR(p) on [X, Y]; select p by BIC up to max_lag.
    2. Compute spectral transfer matrix H(f) from VAR coefficients.
    3. GC_X→Y(f) = log(Syy(f) / (Syy(f) - H12(f)²·Σ11)) — Wilson (1972).
    Uses statsmodels.tsa.VAR for coefficient estimation.
    """
    from statsmodels.tsa.api import VAR  # type: ignore

    n = min(len(sig_source), len(sig_target))
    s1 = np.nan_to_num(sig_source[:n])
    s2 = np.nan_to_num(sig_target[:n])

    freqs = np.linspace(freq_range[0], freq_range[1], n_freqs)
    empty = {
        "freqs": freqs, "gc_xy": np.zeros(n_freqs),
        "gc_yx": np.zeros(n_freqs), "net_dir": np.zeros(n_freqs),
        "best_lag": 0,
    }
    if n < max_lag * 4:
        return empty

    try:
        endog = np.column_stack([s1, s2])
        model = VAR(endog)
        # Select lag by BIC up to max_lag
        lag_order_result = model.select_order(maxlags=min(max_lag, n // 10))
        best_lag = max(1, lag_order_result.bic)
        fitted = model.fit(best_lag)

        # Build spectral transfer matrix H(f) from VAR coefficients
        # A(L) Z = E → H(f) = A(e^{-2πif})^{-1}
        A  = fitted.coefs          # (best_lag, 2, 2)
        Σ  = fitted.sigma_u        # (2, 2) noise covariance

        gc_xy = np.zeros(n_freqs)
        gc_yx = np.zeros(n_freqs)

        for k, freq in enumerate(freqs):
            z = np.exp(-2j * np.pi * freq / fs)
            A_f = np.eye(2)
            for lag in range(best_lag):
                A_f -= A[lag] * (z ** (lag + 1))
            try:
                H = np.linalg.inv(A_f)
            except np.linalg.LinAlgError:
                continue

            # Cross-spectral density
            S = H @ Σ @ H.conj().T
            S11, S22 = np.real(S[0, 0]), np.real(S[1, 1])
            H12_sq   = np.abs(H[1, 0]) ** 2

            # GC X→Y
            denom_xy = S22 - H12_sq * Σ[0, 0]
            if denom_xy > 1e-12 and S22 > 1e-12:
                gc_xy[k] = np.log(S22 / denom_xy)

            # GC Y→X
            H21_sq = np.abs(H[0, 1]) ** 2
            denom_yx = S11 - H21_sq * Σ[1, 1]
            if denom_yx > 1e-12 and S11 > 1e-12:
                gc_yx[k] = np.log(S11 / denom_yx)

        gc_xy = np.maximum(gc_xy, 0)
        gc_yx = np.maximum(gc_yx, 0)

        return {
            "freqs":    freqs,
            "gc_xy":    gc_xy,           # source → target
            "gc_yx":    gc_yx,           # target → source
            "net_dir":  gc_xy - gc_yx,  # positive = feedforward
            "best_lag": int(best_lag),
        }

    except Exception as e:
        warnings.warn(f"Spectral Granger failed: {e}", RuntimeWarning)
        return empty


# ─────────────────────────────────────────────────────────────────────────────
# STEP 13 — Hierarchy Tier Aggregator
# ─────────────────────────────────────────────────────────────────────────────

def aggregate_by_tier(
    measures_by_area: Dict[str, Any],
    tiers: Optional[Dict[str, List[str]]] = None,
    agg: str = "mean",
) -> Dict[str, Dict[str, float]]:
    """
    Step 13. Aggregate LFP measures by cortical hierarchy tier.
    Tests whether omission effects follow a low→high gradient.

    Parameters
    ----------
    measures_by_area : dict {area: value_or_array}
        Any scalar or array keyed by area name.
    tiers  : dict {tier_name: [area_list]}. Default: AREA_TIERS from constants.
    agg    : 'mean' | 'median' | 'max' — aggregation function per tier

    Returns
    -------
    dict {tier: {'mean': float, 'sem': float, 'areas': [...], 'n': int}}

    Example
    -------
    >>> delta_by_area = {a: contrast['RXRR']['Beta'].mean() for a in AREA_ORDER}
    >>> tiers = aggregate_by_tier(delta_by_area)
    >>> # Plot: x=tier, y=tiers['High']['mean'] -- shows gradient
    """
    if tiers is None:
        tiers = AREA_TIERS

    agg_fn = {"mean": np.nanmean, "median": np.nanmedian, "max": np.nanmax}[agg]
    result: Dict[str, Dict[str, float]] = {}

    for tier_name, tier_areas in tiers.items():
        vals = []
        present = []
        for area in tier_areas:
            if area not in measures_by_area:
                continue
            v = measures_by_area[area]
            arr = np.atleast_1d(np.asarray(v, dtype=float)).ravel()
            vals.extend(arr[~np.isnan(arr)].tolist())
            present.append(area)

        vals = np.array(vals, dtype=float)
        if vals.size == 0:
            result[tier_name] = {"mean": np.nan, "sem": np.nan,
                                  "median": np.nan, "n": 0, "areas": present}
        else:
            result[tier_name] = {
                "mean":   float(np.nanmean(vals)),
                "sem":    float(np.nanstd(vals) / np.sqrt(max(1, len(vals)))),
                "median": float(np.nanmedian(vals)),
                "n":      len(vals),
                "areas":  present,
            }

    return result


# ─────────────────────────────────────────────────────────────────────────────
# STEP 14 — Post-Omission Adaptation
# ─────────────────────────────────────────────────────────────────────────────

def compute_post_omission_adapt(
    band_power_by_trial: np.ndarray,
    omission_trial_idx: int,
    n_post: int = 5,
    bands: Optional[Dict[str, Tuple[int, int]]] = None,
) -> Dict[str, np.ndarray]:
    """
    Step 14. Compute band power trajectory across post-omission trial sequence.
    Tests whether omission effect is a 1-trial perturbation or a lasting state.
    Poster 02 finding: beta synchrony may persist into subsequent trials.

    Parameters
    ----------
    band_power_by_trial : np.ndarray, shape (n_trials, n_bands, n_times)
        Band power per trial per band, baseline-normalized.
    omission_trial_idx  : int — index of the omission trial
    n_post              : int — number of post-omission trials to track
    bands               : dict {band: (flo, fhi)} — for labeling only

    Returns
    -------
    dict {band_name: array(n_post+1, n_times)}
        Row 0 = omission trial itself; rows 1..n_post = subsequent trials.
        Compared to matched control window if band_power_by_trial is long enough.

    Interpretation
    --------------
    If beta power remains elevated across rows 0..N, omission induces
    a lasting precision state — not a transient 1-trial perturbation.
    Compare post-omission rows against pre-omission band power for significance.
    """
    if bands is None:
        bands = BANDS
    band_names = list(bands.keys())

    n_trials     = band_power_by_trial.shape[0]
    n_band_dims  = band_power_by_trial.shape[1]
    n_times      = band_power_by_trial.shape[2] if band_power_by_trial.ndim == 3 else 1

    start = omission_trial_idx
    end   = min(n_trials, start + n_post + 1)
    window = band_power_by_trial[start:end]  # (n_post+1, n_bands, n_times)

    result: Dict[str, np.ndarray] = {}
    for b_idx, b_name in enumerate(band_names[:n_band_dims]):
        result[b_name] = window[:, b_idx, :]  # (n_post+1, n_times)

    return result


# ─────────────────────────────────────────────────────────────────────────────
# STEP 15 — Analysis Manifest Writer
# ─────────────────────────────────────────────────────────────────────────────

def write_analysis_manifest(
    out_dir: Path,
    session_id: str,
    figure_specs: Optional[List[Dict[str, Any]]] = None,
    analysis_params: Optional[Dict[str, Any]] = None,
    band_data: Optional[Dict[str, Any]] = None,
) -> Path:
    """
    Step 15. Write reproducibility outputs: JSON manifest + per-band CSV.
    Every figure must be traceable to a manifest entry.

    Parameters
    ----------
    out_dir       : Path — output directory
    session_id    : str
    figure_specs  : list of dicts, each with keys:
                    {fig_id, title, data_arrays_used, conditions, bands, notes}
    analysis_params : dict — key parameters (fs, nperseg, beta_range, etc.)
    band_data     : dict {band: array} — per-band summary values for CSV export

    Returns
    -------
    Path — path to written manifest JSON

    Manifest schema
    ---------------
    {
      "session_id": "...",
      "generated_at": "...",
      "analysis_params": {fs, nperseg, noverlap, beta_range, ...},
      "figures": [{fig_id, title, conditions, bands, data_arrays_used, notes}],
    }

    Example
    -------
    >>> manifest_path = write_analysis_manifest(
    ...     out_dir=Path("output/230629"),
    ...     session_id="230629",
    ...     figure_specs=[
    ...         {"fig_id": "fig_05_band_hierarchy",
    ...          "title": "Beta power hierarchy — main LFP figure",
    ...          "conditions": ["RRRR","RXRR"],
    ...          "bands": ["Beta"],
    ...          "data_arrays_used": ["beta_power_by_area.npy"],
    ...          "notes": "Poster 02 main figure"},
    ...     ],
    ...     analysis_params={"fs": 1000, "nperseg": 256, "beta_range": [13, 30]}
    ... )
    """
    from datetime import datetime
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "session_id": session_id,
        "generated_at": datetime.now().isoformat(),
        "analysis_params": analysis_params or {
            "fs": FS_LFP,
            "nperseg": DEFAULT_WF_PARAMS["nperseg"],
            "noverlap": DEFAULT_WF_PARAMS["noverlap"],
            "bands": {k: list(v) for k, v in BANDS.items()},
            "alignment": "p1 onset = 0ms (code 101.0)",
            "baseline_window_ms": [-500, 0],
            "normalization": "dB (10*log10(P/Pbase))",
        },
        "figures": figure_specs or [],
    }

    manifest_path = out_dir / f"{session_id}_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, default=str)

    # Per-band CSV export
    if band_data:
        rows = []
        for band_name, vals in band_data.items():
            arr = np.atleast_1d(np.asarray(vals, dtype=float)).ravel()
            for i, v in enumerate(arr):
                rows.append({"session_id": session_id, "band": band_name,
                             "index": i, "value": float(v)})
        if rows:
            pd.DataFrame(rows).to_csv(
                out_dir / f"{session_id}_band_summary.csv", index=False)

    return manifest_path
