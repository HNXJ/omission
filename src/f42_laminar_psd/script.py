# core
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import signal
import plotly.graph_objects as go
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.laminar.mapper import LaminarMapper

def compute_psd_db(data, fs, nperseg=128, noverlap=None):
    """
    Computes PSD in dB relative to a baseline window.
    Consistent nperseg=128 ensures frequency alignment.
    """
    freqs, psd = signal.welch(data, fs=fs, nperseg=nperseg, noverlap=noverlap, axis=-1)
    return freqs, psd

def run_laminar_psd():
    """
    Master execution for f042: Laminar PSD Analysis.
    Optimized for visibility in Madelane Golden Dark theme.
    """
    print(f"""[action] Starting f042: Laminar PSD Analysis...""")
    
    loader = DataLoader()
    mapper = LaminarMapper()
    
    areas = ["V1", "PFC"]
    conditions = ["AXAB", "AAAB"]
    omission_onset_idx = 2031
    baseline_window = (omission_onset_idx - 250, omission_onset_idx - 50)
    analysis_window = (omission_onset_idx, omission_onset_idx + 1000)
    
    results = {}

    for area in areas:
        results[area] = {}
        for cond in conditions:
            print(f"""[action] Processing Area: {area}, Condition: {cond}...""")
            data_list = loader.get_signal(mode="lfp", condition=cond, area=area)
            if not data_list: continue
            
            psd_list = []
            for lfp_arr in data_list:
                # Bipolar Referencing
                bipolar_lfp = lfp_arr[:, :-1, :] - lfp_arr[:, 1:, :]
                
                # Artifact Rejection
                chan_vars = np.var(bipolar_lfp, axis=(0, 2))
                mean_var = np.mean(chan_vars); std_var = np.std(chan_vars)
                good_chans = np.where(chan_vars < mean_var + 3 * std_var)[0]
                
                # PSD Computation
                b_data = bipolar_lfp[:, :, baseline_window[0]:baseline_window[1]]
                freqs, b_psd = compute_psd_db(b_data, fs=1000.0)
                
                a_data = bipolar_lfp[:, :, analysis_window[0]:analysis_window[1]]
                _, a_psd = compute_psd_db(a_data, fs=1000.0)
                
                psd_db = 10 * np.log10(a_psd / (np.mean(b_psd, axis=0, keepdims=True) + 1e-12))
                
                stratum_psd = {"Superficial": [], "L4": [], "Deep": []}
                for ch_idx in good_chans:
                    layer = mapper.get_layer(ch_idx)
                    if layer in stratum_psd:
                        stratum_psd[layer].append(psd_db[:, ch_idx, :])
                
                for layer in stratum_psd:
                    if stratum_psd[layer]:
                        stratum_psd[layer] = np.mean(stratum_psd[layer], axis=0)
                    else:
                        stratum_psd[layer] = None
                psd_list.append(stratum_psd)
            
            combined_strata = {"Superficial": [], "L4": [], "Deep": []}
            for s_res in psd_list:
                for layer in combined_strata:
                    if s_res[layer] is not None:
                        combined_strata[layer].append(s_res[layer])
            
            results[area][cond] = {}
            for layer in combined_strata:
                if combined_strata[layer]:
                    results[area][cond][layer] = np.concatenate(combined_strata[layer], axis=0)

    # Plotting (Combined)
    output_dir = Path("D:/drive/outputs/oglo-8figs/f042-laminar-psd")
    output_dir.mkdir(parents=True, exist_ok=True)

    plotter = OmissionPlotter(
        title="Figure f042: Laminar PSD - Global Summary",
        subtitle="Comparing Omission (AXAB) vs. Control (AAAB) across strata (V1 and PFC).",
        template="plotly_dark"
    )
    plotter.fig.update_layout(
        paper_bgcolor="#000000", plot_bgcolor="#000000",
        font=dict(color="#FFFFFF", family="Outfit"),
        title=dict(font=dict(color="#CFB87C", size=22)),
        xaxis=dict(gridcolor="#333333", zerolinecolor="#333333"),
        yaxis=dict(gridcolor="#333333", zerolinecolor="#333333"),
        margin=dict(t=100, b=100, l=100, r=100),
        height=800
    )
    plotter.set_axes("Frequency", "Hz", "Power", "dB")

    for area in areas:
        for layer in ["Superficial", "L4", "Deep"]:
            for cond in conditions:
                if area in results and cond in results[area] and layer in results[area][cond]:
                    data = results[area][cond][layer]
                    n_trials = data.shape[0]
                    boot_means = np.array([np.mean(data[np.random.choice(n_trials, n_trials)], axis=0) for _ in range(200)])
                    mean_val = np.mean(data, axis=0)
                    ci_upper = np.percentile(boot_means, 97.5, axis=0)
                    ci_lower = np.percentile(boot_means, 2.5, axis=0)
                    
                    color = "#CFB87C" if cond == "AXAB" else "#9400D3"
                    name = f"{area}-{layer}-{cond}"
                    plotter.add_shaded_error_bar(
                        freqs, mean_val, 
                        error_upper=ci_upper - mean_val, error_lower=mean_val - ci_lower,
                        name=name, color=color
                    )

    plotter.fig.update_xaxes(range=[2, 80])
    plotter.save(str(output_dir), "f042_laminar_psd")

if __name__ == "__main__":
    run_laminar_psd()
