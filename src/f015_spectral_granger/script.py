# core
import os
import numpy as np
from pathlib import Path
from scipy import linalg, signal
from src.analysis.io.loader import DataLoader
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log

def bandpass_filter(data, low, high, fs=1000):
    nyq = 0.5 * fs
    b, a = signal.butter(4, [low/nyq, high/nyq], btype='bandpass')
    return signal.filtfilt(b, a, data, axis=-1)

def compute_granger_f(target, source, max_lag=10):
    n = len(target)
    Y = target[max_lag:]
    X = []
    for l in range(1, max_lag + 1):
        X.append(target[max_lag-l:-l])
        X.append(source[max_lag-l:-l])
    X = np.stack(X, axis=1)
    R_X = []
    for l in range(1, max_lag+1): R_X.append(target[max_lag-l:-l])
    R_X = np.stack(R_X, axis=1)
    beta_r, _, _, _ = linalg.lstsq(R_X, Y)
    var_res = np.var(Y - R_X @ beta_r)
    beta_u, _, _, _ = linalg.lstsq(X, Y)
    var_unres = np.var(Y - X @ beta_u)
    return max(0, (var_res - var_unres) / (var_unres + 1e-12))

def run_spectral_granger():
    log.action("Starting f015: Spectral LFP Granger (Safe Session-Averaging)...")
    loader = DataLoader()
    output_dir = Path("D:/drive/outputs/oglo-8figs/f015-spectral-granger")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    area1, area2 = "V1", "PFC"
    cond = "AXAB"
    
    lfp1_list = loader.get_signal(mode="lfp", area=area1, condition=cond, align_to="omission")
    lfp2_list = loader.get_signal(mode="lfp", area=area2, condition=cond, align_to="omission")
    if not lfp1_list or not lfp2_list: return
    
    # Average across channels and trials per session, then average across sessions
    ts1 = np.mean(np.stack([np.mean(s, axis=(0, 1)) for s in lfp1_list], axis=0), axis=0)
    ts2 = np.mean(np.stack([np.mean(s, axis=(0, 1)) for s in lfp2_list], axis=0), axis=0)
    
    # Filter bands
    beta1 = bandpass_filter(ts1, 15, 30); beta2 = bandpass_filter(ts2, 15, 30)
    gamma1 = bandpass_filter(ts1, 30, 80); gamma2 = bandpass_filter(ts2, 30, 80)
    
    win_size, step = 500, 100
    n_wins = (len(ts1) - win_size) // step
    ff_gamma, fb_beta, times = [], [], []
    
    for i in range(n_wins):
        s, e = i*step, i*step + win_size
        times.append(s - 1000 + win_size/2)
        ff_gamma.append(compute_granger_f(gamma2[s:e], gamma1[s:e])) # V1 -> PFC (Gamma)
        fb_beta.append(compute_granger_f(beta1[s:e], beta2[s:e]))    # PFC -> V1 (Beta)
        
    plotter = OmissionPlotter(title="Figure f015: Spectral Granger Routing", template="plotly_dark")
    import plotly.graph_objects as go
    plotter.add_trace(go.Scatter(x=times, y=ff_gamma, name="FF Gamma (V1 -> PFC)", line=dict(color="#CFB87C")), "FF")
    plotter.add_trace(go.Scatter(x=times, y=fb_beta, name="FB Beta (PFC -> V1)", line=dict(color="#9400D3")), "FB")
    plotter.save(str(output_dir), "f015_spectral_granger")

if __name__ == "__main__":
    run_spectral_granger()
