# f039 — Spike-Field Coherence via Pairwise Phase Consistency (PPC)
# =================================================================
# Quantifies phase synchronization between localized unit spiking and
# distal LFP during expectation violations (omissions).
#
# Metric: Pairwise Phase Consistency (PPC) — bias-free PLV that is
# independent of spike count, critical for omission windows where
# firing rates drop during the visual void.
#
# Reference: Vinck et al. (2010) NeuroImage 51(1):112-122
# PPC = (2 / (N*(N-1))) * sum_{i<j} cos(phi_i - phi_j)
# where phi_i are spike phases relative to the LFP oscillation.

import numpy as np
from scipy import signal as sig
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log


# =====================================================================
# Band Definitions
# =====================================================================
BANDS = {
    "Theta":      (4, 8),
    "Alpha":      (8, 13),
    "Beta":       (13, 30),
    "Low Gamma":  (35, 50),
    "High Gamma": (50, 80),
}

# =====================================================================
# Omission Timing Map (Family-Aware Slot Resolution)
# =====================================================================
TIMING_MAP = {
    # p2 slot omissions
    "AXAB": "p2", "BXBA": "p2", "RXRR": "p2",
    # p3 slot omissions
    "AAXB": "p3", "BBXA": "p3", "RRXR": "p3",
    # p4 slot omissions
    "AAAX": "p4", "BBBX": "p4", "RRRX": "p4",
}

# Minimum spike threshold per unit-LFP pair (bias prevention)
MIN_SPIKES = 5


def compute_ppc(phases: np.ndarray) -> float:
    """
    Pairwise Phase Consistency (PPC).
    
    Input:  phases — 1D array of spike phases (radians), length N.
    Output: float — PPC value in [-1, 1]. 1 = perfect phase-locking.
    
    Formula: PPC = (2 / (N*(N-1))) * sum_{i<j} cos(phi_i - phi_j)
    
    This is algebraically equivalent to:
    PPC = (|sum(exp(i*phi))|^2 - N) / (N*(N-1))
    which avoids O(N^2) pairwise computation.
    """
    n = len(phases)
    print(f"""[action] Computing PPC: n_spikes={n}""")
    
    if n < MIN_SPIKES:
        print(f"""[warning] Below minimum spike threshold ({n} < {MIN_SPIKES}), returning NaN""")
        return np.nan
    
    # Efficient PPC via resultant vector
    # PPC = (|R|^2 - N) / (N * (N - 1))  where R = sum(exp(i*phi))
    resultant = np.sum(np.exp(1j * phases))
    resultant_sq = np.abs(resultant) ** 2
    ppc = (resultant_sq - n) / (n * (n - 1))
    print(f"""[result] PPC = {ppc:.6f} (resultant_length={np.abs(resultant)/n:.4f})""")
    return ppc


def bandpass_filter(data: np.ndarray, low: float, high: float, fs: int = 1000) -> np.ndarray:
    """
    Zero-phase Butterworth bandpass filter.
    
    Input:  data — 1D or 2D array (channels x time), low/high in Hz.
    Output: Filtered array, same shape.
    """
    print(f"""[action] Bandpass filtering: {low}-{high}Hz, fs={fs}""")
    nyq = 0.5 * fs
    
    # Guard against invalid frequency range
    if low >= nyq or high >= nyq:
        print(f"""[warning] Band [{low},{high}]Hz exceeds Nyquist ({nyq}Hz), clamping""")
        high = min(high, nyq - 1)
        low = min(low, high - 1)
    
    b, a = sig.butter(4, [low / nyq, high / nyq], btype='bandpass')
    return sig.filtfilt(b, a, data, axis=-1)


def extract_spike_phases(spk_train: np.ndarray, lfp_filtered: np.ndarray) -> np.ndarray:
    """
    Extracts the instantaneous LFP phase at each spike time.
    
    Input:
        spk_train    — 1D binary spike train (0/1), length T.
        lfp_filtered — 1D bandpass-filtered LFP, length T.
    Output:
        phases — 1D array of spike phases (radians).
    """
    # Compute analytic signal via Hilbert transform
    analytic = sig.hilbert(lfp_filtered)
    inst_phase = np.angle(analytic)
    
    # Extract phases at spike times
    spike_indices = np.where(spk_train > 0)[0]
    
    if len(spike_indices) == 0:
        print(f"""[info] No spikes in this segment""")
        return np.array([])
    
    phases = inst_phase[spike_indices]
    print(f"""[info] Extracted {len(phases)} spike phases""")
    return phases


def match_spike_counts(phases_baseline: np.ndarray, phases_omission: np.ndarray) -> tuple:
    """
    Bias prevention: spike-count matching between baseline and omission windows.
    Randomly subsamples the larger set to match the smaller set.
    
    Input:  two arrays of spike phases.
    Output: two arrays of equal length (matched).
    """
    n_base = len(phases_baseline)
    n_omit = len(phases_omission)
    
    print(f"""[action] Spike-count matching: baseline={n_base}, omission={n_omit}""")
    
    if n_base == 0 or n_omit == 0:
        print(f"""[warning] One window has zero spikes, cannot match""")
        return phases_baseline, phases_omission
    
    target_n = min(n_base, n_omit)
    
    if n_base > target_n:
        idx = np.random.choice(n_base, target_n, replace=False)
        phases_baseline = phases_baseline[idx]
        print(f"""[action] Subsampled baseline: {n_base} -> {target_n}""")
    
    if n_omit > target_n:
        idx = np.random.choice(n_omit, target_n, replace=False)
        phases_omission = phases_omission[idx]
        print(f"""[action] Subsampled omission: {n_omit} -> {target_n}""")
    
    return phases_baseline, phases_omission


def compute_sfc_for_pair(spk_data: np.ndarray, lfp_data: np.ndarray,
                         omission_onset_sample: int, band: tuple,
                         window_ms: int = 500, fs: int = 1000) -> dict:
    """
    Computes PPC for a single unit-LFP pair across baseline and omission windows.
    
    Input:
        spk_data — (n_trials, T) binary spike matrix for one unit.
        lfp_data — (n_trials, T) LFP from the distal channel.
        omission_onset_sample — sample index of omission onset.
        band — (low_hz, high_hz) tuple.
        window_ms — analysis window duration in ms.
        fs — sampling rate.
    
    Output:
        dict with keys: ppc_baseline, ppc_omission, n_spikes_baseline,
                        n_spikes_omission, n_trials.
    """
    n_trials = min(spk_data.shape[0], lfp_data.shape[0])
    print(f"""[info] Processing pair: {n_trials} trials, band={band}Hz""")
    
    # Define windows
    # Baseline: 500ms before omission (the preceding stimulus period)
    baseline_start = max(0, omission_onset_sample - window_ms)
    baseline_end = omission_onset_sample
    
    # Omission: 500ms starting at omission onset
    omission_start = omission_onset_sample
    omission_end = min(omission_onset_sample + window_ms, spk_data.shape[-1])
    
    print(f"""[info] Windows: baseline=[{baseline_start},{baseline_end}], omission=[{omission_start},{omission_end}]""")
    
    all_phases_baseline = []
    all_phases_omission = []
    
    for trial in range(n_trials):
        # Bandpass filter LFP for this trial
        lfp_trial = lfp_data[trial, :]
        try:
            lfp_filt = bandpass_filter(lfp_trial.astype(np.float64), band[0], band[1], fs)
        except Exception as e:
            print(f"""[warning] Filter failed on trial {trial}: {e}""")
            continue
        
        # Baseline window
        spk_base = spk_data[trial, baseline_start:baseline_end]
        lfp_base = lfp_filt[baseline_start:baseline_end]
        phases_b = extract_spike_phases(spk_base, lfp_base)
        all_phases_baseline.append(phases_b)
        
        # Omission window
        spk_omit = spk_data[trial, omission_start:omission_end]
        lfp_omit = lfp_filt[omission_start:omission_end]
        phases_o = extract_spike_phases(spk_omit, lfp_omit)
        all_phases_omission.append(phases_o)
    
    # Concatenate across trials
    phases_baseline = np.concatenate(all_phases_baseline) if all_phases_baseline else np.array([])
    phases_omission = np.concatenate(all_phases_omission) if all_phases_omission else np.array([])
    
    print(f"""[info] Total spikes: baseline={len(phases_baseline)}, omission={len(phases_omission)}""")
    
    # Spike-count matching (bias prevention)
    phases_baseline_matched, phases_omission_matched = match_spike_counts(
        phases_baseline, phases_omission
    )
    
    # Compute PPC
    ppc_base = compute_ppc(phases_baseline_matched)
    ppc_omit = compute_ppc(phases_omission_matched)
    
    return {
        "ppc_baseline": ppc_base,
        "ppc_omission": ppc_omit,
        "n_spikes_baseline": len(phases_baseline),
        "n_spikes_omission": len(phases_omission),
        "n_spikes_matched": len(phases_baseline_matched),
        "n_trials": n_trials,
    }
