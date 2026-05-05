# core
import numpy as np
import scipy.signal
from src.analysis.io.logger import log

def compute_ppc(phases: np.ndarray, min_spikes: int = 5) -> float:
    """
    Pairwise Phase Consistency (PPC).
    Quantifies phase synchronization bias-free.
    Formula: PPC = (|sum(exp(i*phi))|^2 - N) / (N*(N-1))
    """
    n = len(phases)
    if n < min_spikes:
        return np.nan
    
    # Efficient PPC via resultant vector
    resultant = np.sum(np.exp(1j * phases))
    resultant_sq = np.abs(resultant) ** 2
    ppc = (resultant_sq - n) / (n * (n - 1))
    return ppc

def calculate_plv(lfp, spikes, fs=1000, freq_band=(13, 30)):
    """
    Computes Phase-Locking Value (PLV) for a specific frequency band.
    lfp: (trials, time) or (time,)
    spikes: (trials, time) or (time,) - Binary array (1 at spike time, 0 otherwise)
    """
    # 1. Bandpass filter the LFP
    nyq = 0.5 * fs
    low, high = freq_band[0] / nyq, freq_band[1] / nyq
    b, a = scipy.signal.butter(4, [low, high], btype='bandpass')
    
    # Apply filter along time axis
    filtered_lfp = scipy.signal.filtfilt(b, a, lfp, axis=-1)
    
    # 2. Extract Phase via Hilbert Transform
    analytic_signal = scipy.signal.hilbert(filtered_lfp, axis=-1)
    phase_lfp = np.angle(analytic_signal)
    
    # 3. Identify Phases at Spike Times
    spike_indices = np.where(spikes > 0)
    spike_phases = phase_lfp[spike_indices]
    
    if len(spike_phases) == 0:
        return 0.0, np.array([])
        
    # 4. Compute Mean Resultant Vector (PLV)
    complex_phases = np.exp(1j * spike_phases)
    plv = np.abs(np.mean(complex_phases))
    
    return plv, spike_phases

def get_plv_spectrum(lfp, spikes, fs=1000, n_bins=30, metric='plv'):
    """
    Sweep through frequencies to see the full SFC spectrum.
    metric: 'plv' or 'ppc'
    """
    freqs = np.logspace(np.log10(2), np.log10(100), n_bins)
    vals = []
    
    for f in freqs:
        bw = max(2.0, f * 0.2)
        low = f - bw/2
        high = f + bw/2
        if high >= 500: high = 499 # Nyquist guard
        if low <= 0: low = 0.1
        
        plv, phases = calculate_plv(lfp, spikes, fs, freq_band=(low, high))
        
        if metric == 'ppc':
            vals.append(compute_ppc(phases))
        else:
            vals.append(plv)
        
    return freqs, np.array(vals)

def select_top_units(loader, area, mode="omission", top_n=10):
    """
    Selects top units based on firing rate response.
    """
    area_entries = loader.area_map.get(area, [])
    units = []
    
    for entry in area_entries:
        ses = entry["session"]; p = entry["probe"]; start_ch = entry["start_ch"]; end_ch = entry["end_ch"]; total_ch = entry["total_ch"]
        try:
            cond = "AXAB" if mode == "omission" else "AAAB"
            f_spk = loader.data_dir / f"ses{ses}-units-probe{p}-spk-{cond}.npy"
            if not f_spk.exists(): continue
            
            spk = np.load(f_spk, mmap_mode='r')
            u_start = int(spk.shape[1] * (start_ch / total_ch))
            u_end = int(spk.shape[1] * (end_ch / total_ch))
            
            win = slice(2031, 2562) if mode == "omission" else slice(1000, 1531)
            fr = np.mean(spk[:, u_start:u_end, win], axis=(0, 2))
            
            for i, val in enumerate(fr):
                if val > 0.001:
                    units.append({
                        "score": val, 
                        "session": ses, "probe": p, 
                        "local_idx": u_start + i,
                        "area": area
                    })
        except Exception: continue
        
    units.sort(key=lambda x: x["score"], reverse=True)
    return units[:top_n]

def get_matched_sfc_data(loader, unit_info):
    """
    Loads LFP and SPK for a specific unit and aligns to omission.
    """
    ses = unit_info["session"]; p = unit_info["probe"]; u_idx = unit_info["local_idx"]; area = unit_info["area"]
    
    f_spk = loader.data_dir / f"ses{ses}-units-probe{p}-spk-AXAB.npy"
    f_lfp = loader.data_dir / f"ses{ses}-probe{p}-lfp-AXAB.npy"
    
    if not (f_spk.exists() and f_lfp.exists()): return None, None
    
    spk = np.load(f_spk, mmap_mode='r')[:, u_idx, 2031:2562]
    
    area_mapping = [e for e in loader.area_map[area] if e["session"] == ses and e["probe"] == p][0]
    lfp_full = np.load(f_lfp, mmap_mode='r')[:, area_mapping["start_ch"]:area_mapping["end_ch"], 2031:2562]
    lfp = np.mean(lfp_full, axis=1)
    
    return lfp, spk

def apply_subsampling(spikes_list, target_count=None):
    """
    Subsamples spikes to match a target count.
    """
    counts = [np.sum(s > 0) for s in spikes_list]
    if target_count is None:
        target_count = min(counts) if counts else 0
        
    log.info(f"[action] Subsampling spikes to target count: {target_count}")
    
    new_spikes = []
    for s in spikes_list:
        idx = np.where(s > 0)
        total = len(idx[0])
        if total > target_count:
            keep = np.random.choice(total, target_count, replace=False)
            s_new = np.zeros_like(s)
            if len(idx) == 2:
                s_new[idx[0][keep], idx[1][keep]] = 1
            else:
                s_new[idx[0][keep]] = 1
            new_spikes.append(s_new)
        else:
            new_spikes.append(s)
    return new_spikes
