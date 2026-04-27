# core — f015: Spectral-Band Granger Routing (V1 <-> PFC)
import os
import numpy as np
from pathlib import Path
from scipy import linalg, signal
from src.analysis.io.loader import DataLoader
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log

def bandpass_filter(data, low, high, fs=1000):
    """Butterworth bandpass, zero-phase."""
    print(f"""[action] Bandpass filtering: {low}-{high}Hz""")
    nyq = 0.5 * fs
    b, a = signal.butter(4, [low/nyq, high/nyq], btype='bandpass')
    return signal.filtfilt(b, a, data, axis=-1)

def compute_granger_f(target, source, max_lag=10):
    """
    Computes Granger F-stat as log-ratio of restricted vs unrestricted model variance.
    Returns ln(var_restricted / var_unrestricted). Positive = source predicts target.
    
    FIX: Removed max(0, ...) clamp that was zeroing out legitimate FB signals.
    FIX: Apply stationarity conditioning via first-order differencing.
    """
    # Stationarity conditioning
    target = np.diff(target)
    source = np.diff(source)
    print(f"""[action] GC fit: target_len={len(target)}, source_len={len(source)}, max_lag={max_lag}""")
    
    n = len(target)
    if n <= max_lag + 1:
        print(f"""[warning] Insufficient samples ({n}) for max_lag={max_lag}""")
        return 0.0
    
    Y = target[max_lag:]
    
    # Unrestricted model: target predicted by own lags + source lags
    X = []
    for l in range(1, max_lag + 1):
        X.append(target[max_lag-l:-l])
        X.append(source[max_lag-l:-l])
    X = np.stack(X, axis=1)
    
    # Restricted model: target predicted by own lags only
    R_X = []
    for l in range(1, max_lag+1):
        R_X.append(target[max_lag-l:-l])
    R_X = np.stack(R_X, axis=1)
    
    try:
        beta_r, _, _, _ = linalg.lstsq(R_X, Y)
        var_res = np.var(Y - R_X @ beta_r)
        
        beta_u, _, _, _ = linalg.lstsq(X, Y)
        var_unres = np.var(Y - X @ beta_u)
        
        # Proper GC: ln(var_restricted / var_unrestricted)
        # Positive means source helps predict target
        if var_unres < 1e-12:
            print(f"""[warning] Near-zero unrestricted variance""")
            return 0.0
        
        gc_val = np.log(var_res / var_unres)
        print(f"""[result] GC = {gc_val:.6f} (var_res={var_res:.6f}, var_unres={var_unres:.6f})""")
        return gc_val
    except Exception as e:
        print(f"""[error] GC computation failed: {e}""")
        return 0.0

def run_f015():
    log.action("Starting f015: Spectral LFP Granger (Safe Session-Averaging)...")
    print(f"""[action] f015: Initializing spectral Granger pipeline""")
    loader = DataLoader()
    output_dir = Path("D:/drive/outputs/oglo-8figs/f015-spectral-granger")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    area1, area2 = "V1", "PFC"
    cond = "AXAB"
    print(f"""[action] Loading LFP for {area1} and {area2}, condition={cond}""")
    
    lfp1_list = loader.get_signal(mode="lfp", area=area1, condition=cond, align_to="omission")
    lfp2_list = loader.get_signal(mode="lfp", area=area2, condition=cond, align_to="omission")
    if not lfp1_list or not lfp2_list:
        print(f"""[error] No LFP data loaded for {area1} or {area2}""")
        return
    
    # Average across channels and trials per session, then average across sessions
    ts1 = np.mean(np.stack([np.mean(s, axis=(0, 1)) for s in lfp1_list], axis=0), axis=0)
    ts2 = np.mean(np.stack([np.mean(s, axis=(0, 1)) for s in lfp2_list], axis=0), axis=0)
    print(f"""[info] Signal lengths: V1={len(ts1)}, PFC={len(ts2)}""")
    
    # Filter bands
    print(f"""[action] Bandpass filtering for Beta(15-30Hz) and Gamma(30-80Hz)""")
    beta1 = bandpass_filter(ts1, 15, 30); beta2 = bandpass_filter(ts2, 15, 30)
    gamma1 = bandpass_filter(ts1, 30, 80); gamma2 = bandpass_filter(ts2, 30, 80)
    
    win_size, step = 500, 100
    n_wins = (len(ts1) - win_size) // step
    ff_gamma, fb_beta, times = [], [], []
    print(f"""[action] Computing sliding-window GC: {n_wins} windows, size={win_size}, step={step}""")
    
    for i in range(n_wins):
        s, e = i*step, i*step + win_size
        times.append(s - 1000 + win_size/2)
        
        # FF: V1 Gamma -> PFC Gamma (feedforward ascending)
        ff_val = compute_granger_f(gamma2[s:e], gamma1[s:e])
        ff_gamma.append(ff_val)
        
        # FB: PFC Beta -> V1 Beta (feedback descending)
        fb_val = compute_granger_f(beta1[s:e], beta2[s:e])
        fb_beta.append(fb_val)
    
    print(f"""[result] FF Gamma range: [{min(ff_gamma):.4f}, {max(ff_gamma):.4f}]""")
    print(f"""[result] FB Beta range:  [{min(fb_beta):.4f}, {max(fb_beta):.4f}]""")
        
    plotter = OmissionPlotter(title="Figure f015: Spectral Granger Routing",
                              subtitle="V1<->PFC Band-Specific Directed Influence")
    import plotly.graph_objects as go
    plotter.add_trace(go.Scatter(x=times, y=ff_gamma, name="FF Gamma (V1 -> PFC)", 
                                 line=dict(color="#CFB87C", width=3)), "FF Gamma (V1 -> PFC)")
    plotter.add_trace(go.Scatter(x=times, y=fb_beta, name="FB Beta (PFC -> V1)", 
                                 line=dict(color="#9400D3", width=3)), "FB Beta (PFC -> V1)")
    plotter.set_axes("Time from Omission", "ms", "Granger Causality", "ln(s2_res/s2_unres)")
    plotter.add_xline(0, "Omission", color="#FF1493", dash="dash")
    plotter.add_yline(0, "No Causality", color="gray", dash="dot")
    plotter.save(str(output_dir), "f015_spectral_granger")
    print(f"""[action] f015 complete""")

if __name__ == "__main__":
    run_spectral_granger()
