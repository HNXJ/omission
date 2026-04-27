# core
import os
import numpy as np
from pathlib import Path
from scipy import linalg
from src.analysis.io.loader import DataLoader
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log

def estimate_ar_coeffs(data, max_lag):
    n = len(data)
    r = np.correlate(data, data, mode='full')[n-1:] / n
    R = linalg.toeplitz(r[:max_lag])
    coeffs = linalg.solve(R, r[1:max_lag+1])
    pred = np.zeros_like(data)
    for l in range(max_lag):
        pred[l+1:] += coeffs[l] * data[:-l-1]
    res_var = np.var(data[max_lag:] - pred[max_lag:])
    return coeffs, res_var

def compute_granger_f(target, source, max_lag=5):
    """Log-ratio Granger causality with stationarity conditioning."""
    # Stationarity conditioning
    target = np.diff(target)
    source = np.diff(source)
    print(f"""[action] GC fit: n={len(target)}, max_lag={max_lag}""")
    
    n = len(target)
    if n <= max_lag + 1:
        print(f"""[warning] Insufficient samples for GC""")
        return 0.0
    
    Y = target[max_lag:]
    X = []
    for l in range(1, max_lag + 1):
        X.append(target[max_lag-l:-l])
        X.append(source[max_lag-l:-l])
    X = np.stack(X, axis=1)
    R_X = []
    for l in range(1, max_lag+1): R_X.append(target[max_lag-l:-l])
    R_X = np.stack(R_X, axis=1)
    
    try:
        beta_r, _, _, _ = linalg.lstsq(R_X, Y)
        var_res_model = np.var(Y - R_X @ beta_r)
        beta_u, _, _, _ = linalg.lstsq(X, Y)
        var_unres = np.var(Y - X @ beta_u)
        if var_unres < 1e-12:
            return 0.0
        gc_val = np.log(var_res_model / var_unres)
        print(f"""[result] GC = {gc_val:.6f}""")
        return gc_val
    except Exception as e:
        print(f"""[error] GC failed: {e}""")
        return 0.0

def run_f014():
    log.action("Starting f014: Spiking Granger (Safe Session-Averaging)...")
    loader = DataLoader()
    output_dir = Path("D:/drive/outputs/oglo-8figs/f014-spiking-granger")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    area1, area2 = "V1", "PFC"
    cond = "AXAB"
    
    spk1_list = loader.get_signal(mode="spk", area=area1, condition=cond, align_to="omission")
    spk2_list = loader.get_signal(mode="spk", area=area2, condition=cond, align_to="omission")
    if not spk1_list or not spk2_list: return
    
    # Average across units and trials per session, then average across sessions
    rate1 = np.mean(np.concatenate([np.mean(s, axis=(0, 1), keepdims=True) for s in spk1_list], axis=0)) # This is just a scalar? No.
    # We want a TIME SERIES.
    # Average across trials and units per session -> (Time,)
    ts1 = np.mean(np.stack([np.mean(s, axis=(0, 1)) for s in spk1_list], axis=0), axis=0)
    ts2 = np.mean(np.stack([np.mean(s, axis=(0, 1)) for s in spk2_list], axis=0), axis=0)
    
    win_size, step = 200, 50
    n_bins = (len(ts1) - win_size) // step
    gc_1to2, gc_2to1, times = [], [], []
    
    for i in range(n_bins):
        s, e = i*step, i*step + win_size
        times.append(s - 1000 + win_size/2)
        gc_1to2.append(compute_granger_f(ts2[s:e], ts1[s:e]))
        gc_2to1.append(compute_granger_f(ts1[s:e], ts2[s:e]))
        
    print(f"""[result] FF range: [{min(gc_1to2):.4f}, {max(gc_1to2):.4f}]""")
    print(f"""[result] FB range: [{min(gc_2to1):.4f}, {max(gc_2to1):.4f}]""")
    
    plotter = OmissionPlotter(title="Figure f014: Spiking Granger",
                              subtitle="V1<->PFC Spike-Rate Directed Influence")
    import plotly.graph_objects as go
    plotter.add_trace(go.Scatter(x=times, y=gc_1to2, name="FF: V1 -> PFC", 
                                 line=dict(color="#CFB87C", width=3)), "FF: V1 -> PFC")
    plotter.add_trace(go.Scatter(x=times, y=gc_2to1, name="FB: PFC -> V1", 
                                 line=dict(color="#9400D3", width=3)), "FB: PFC -> V1")
    plotter.set_axes("Time from Omission", "ms", "Granger Causality", "ln(s2_res/s2_unres)")
    plotter.add_xline(0, "Omission", color="#FF1493", dash="dash")
    plotter.add_yline(0, "No Causality", color="gray", dash="dot")
    plotter.save(str(output_dir), "f014_spiking_granger")

if __name__ == "__main__":
    run_spiking_granger()
