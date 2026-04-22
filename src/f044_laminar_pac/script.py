# core
import os
import numpy as np
from pathlib import Path
from scipy.signal import butter, filtfilt, hilbert
from src.analysis.io.loader import DataLoader
from src.analysis.laminar.mapper import LaminarMapper
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log

def calculate_mi(phase, amplitude, n_bins=18):
    """
    Computes Tort's Modulation Index (MI).
    """
    bins = np.linspace(-np.pi, np.pi, n_bins+1)
    mean_amp = []
    for i in range(n_bins):
        mask = (phase >= bins[i]) & (phase < bins[i+1])
        if np.any(mask):
            mean_amp.append(np.mean(amplitude[mask]))
        else:
            mean_amp.append(0)
    
    p = np.array(mean_amp) / (np.sum(mean_amp) + 1e-12)
    p = p + 1e-12
    h = -np.sum(p * np.log(p))
    mi = (np.log(n_bins) - h) / np.log(n_bins)
    return mi

def bandpass_filter(data, low, high, fs=1000, order=4):
    nyq = 0.5 * fs
    low = low / nyq
    high = high / nyq
    b, a = butter(order, [low, high], btype='bandpass')
    return filtfilt(b, a, data, axis=-1)

def run_laminar_pac():
    log.action("Starting f044: Laminar PAC Analysis...")
    
    # 1. Initialize
    loader = DataLoader()
    mapper = LaminarMapper()
    output_dir = Path("D:/drive/outputs/oglo-8figs/f044-laminar-pac")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    areas = ["V1", "PFC"]
    conditions = ["AXAB", "AAAB"]
    n_surrogates = 100
    n_bins = 18
    
    # Frequency bands
    phase_bands = {"Delta": (2, 4), "Theta": (4, 8), "Alpha": (8, 12)}
    amp_bands = {"Gamma": (30, 80)}
    
    # Canonical boundaries from LaminarMapper
    strata_bounds = {"Superficial": (0, 40), "L4": (40, 70), "Deep": (70, 128)}
    
    results = {area: {cond: {} for cond in conditions} for area in areas}
    
    for area in areas:
        for cond in conditions:
            log.action(f"Processing PAC for {area} - {cond}...")
            
            lfp_list = loader.get_signal(mode="lfp", area=area, condition=cond, align_to="omission")
            if not lfp_list: continue
            
            # Process sessions individually
            deep_sigs = []
            super_sigs = []
            
            for session_lfp in lfp_list:
                deep_start, deep_end = strata_bounds["Deep"]
                super_start, super_end = strata_bounds["Superficial"]
                
                valid_deep = np.arange(max(0, deep_start), min(session_lfp.shape[1], deep_end))
                valid_super = np.arange(max(0, super_start), min(session_lfp.shape[1], super_end))
                
                if len(valid_deep) and len(valid_super):
                    deep_sigs.append(np.mean(session_lfp[:, valid_deep, :], axis=1))
                    super_sigs.append(np.mean(session_lfp[:, valid_super, :], axis=1))
            
            if not deep_sigs or not super_sigs: continue
            
            deep_sig = np.concatenate(deep_sigs, axis=0)
            super_sig = np.concatenate(super_sigs, axis=0)
            
            for pb_name, (pb_low, pb_high) in phase_bands.items():
                for ab_name, (ab_low, ab_high) in amp_bands.items():
                    log.action(f"Computing PAC: Phase {pb_name} vs Amp {ab_name}")
                    
                    mi_trials = []
                    z_trials = []
                    
                    # Full trial range
                    for t in range(deep_sig.shape[0]):
                        p_sig = bandpass_filter(deep_sig[t], pb_low, pb_high)
                        phase = np.angle(hilbert(p_sig))
                        
                        a_sig = bandpass_filter(super_sig[t], ab_low, ab_high)
                        amp = np.abs(hilbert(a_sig))
                        
                        emp_mi = calculate_mi(phase, amp, n_bins)
                        
                        null_mis = []
                        for _ in range(n_surrogates):
                            shift = np.random.randint(100, len(amp) - 100)
                            amp_null = np.roll(amp, shift)
                            null_mis.append(calculate_mi(phase, amp_null, n_bins))
                        
                        null_mis = np.array(null_mis)
                        z_score = (emp_mi - np.mean(null_mis)) / (np.std(null_mis) + 1e-12)
                        
                        mi_trials.append(emp_mi)
                        z_trials.append(z_score)
                    
                    results[area][cond][f"{pb_name}-{ab_name}"] = {
                        "mi": np.mean(mi_trials),
                        "z": np.mean(z_trials)
                    }

    # 2. Plotting
    plotter = OmissionPlotter(
        title="Figure f044: Laminar PAC (Deep Phase -> Superficial Amp)",
        subtitle="Modulation Index (Z-scored) comparing Omission (AXAB) vs Control (AAAB).",
        template="plotly_dark"
    )
    plotter.fig.update_layout(
        paper_bgcolor="#000000", plot_bgcolor="#000000",
        font=dict(color="#FFFFFF", family="Outfit"),
        title=dict(font=dict(color="#CFB87C", size=22)),
        height=800
    )
    
    import plotly.graph_objects as go
    for area in areas:
        x_labels = list(results[area]["AXAB"].keys())
        y_axab = [results[area]["AXAB"][k]["z"] for k in x_labels]
        y_aaab = [results[area]["AAAB"][k]["z"] for k in x_labels]
        
        plotter.add_trace(go.Bar(x=x_labels, y=y_axab, name=f"{area} - AXAB", marker_color="#CFB87C"), f"{area} - AXAB")
        plotter.add_trace(go.Bar(x=x_labels, y=y_aaab, name=f"{area} - AAAB", marker_color="#9400D3"), f"{area} - AAAB")

    plotter.set_axes("Frequency Band Pair", "", "Coupling Strength (Z-score)", "")
    plotter.add_yline(1.96, "p < 0.05", color="white", dash="dash")
    plotter.save(str(output_dir), "f044_laminar_pac")

if __name__ == "__main__":
    run_laminar_pac()
