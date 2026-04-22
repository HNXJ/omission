# core
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.signal import hilbert, butter, filtfilt
import plotly.graph_objects as go
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.laminar.mapper import LaminarMapper

def bandpass_filter(data, lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low, high = lowcut / nyq, highcut / nyq
    b, a = butter(order, [low, high], btype='bandpass')
    return filtfilt(b, a, data, axis=-1)

def compute_plv(phases):
    return np.abs(np.mean(np.exp(1j * phases))) if len(phases) > 0 else 0

def run_laminar_sfc():
    print(f"""[action] Starting f043: Laminar SFC Analysis...""")
    loader = DataLoader(); mapper = LaminarMapper()
    areas = ["V1", "PFC"]; conditions = ["AXAB", "AAAB"]
    omission_onset_idx = 2031
    analysis_window = (omission_onset_idx, omission_onset_idx + 1000)
    
    results = {}
    for area in areas:
        results[area] = {}
        for cond in conditions:
            lfp_list = loader.get_signal(mode="lfp", condition=cond, area=area)
            spk_list = loader.get_signal(mode="spk", condition=cond, area=area)
            if not lfp_list or not spk_list: continue
            
            all_phases = {"Superficial": [], "L4": [], "Deep": []}
            for lfp_arr, spk_arr in zip(lfp_list, spk_list):
                strat_lfp = {}
                for layer in all_phases:
                    start, end = mapper.depth_map[layer]
                    start = max(0, start); end = min(lfp_arr.shape[1], end)
                    if start < end:
                        layer_data = np.mean(lfp_arr[:, start:end, :], axis=1)
                        strat_lfp[layer] = np.angle(hilbert(bandpass_filter(layer_data, 2, 4, 1000.0)))
                
                for u_idx in range(spk_arr.shape[1]):
                    rel_idx = u_idx / spk_arr.shape[1]
                    layer = "Superficial" if rel_idx < 0.3 else ("L4" if rel_idx < 0.6 else "Deep")
                    if layer in strat_lfp:
                        t_idxs, time_idxs = np.where(spk_arr[:, u_idx, analysis_window[0]:analysis_window[1]] == 1)
                        all_phases[layer].extend(strat_lfp[layer][t_idxs, time_idxs + analysis_window[0]])

            results[area][cond] = {}
            for layer in all_phases:
                phases = np.array(all_phases[layer])
                if len(phases) > 50:
                    sub_phases = np.random.choice(phases, min(500, len(phases)), replace=False)
                    results[area][cond][layer] = {"plv": compute_plv(sub_phases), "phases": sub_phases}

    output_dir = Path("D:/drive/outputs/oglo-8figs/f043-laminar-sfc")
    output_dir.mkdir(parents=True, exist_ok=True)

    for area in areas:
        fig = go.Figure()
        for i, layer in enumerate(["Superficial", "L4", "Deep"]):
            for cond in conditions:
                if layer in results[area][cond]:
                    data = results[area][cond][layer]
                    counts, bins = np.histogram(data["phases"], bins=18, range=(-np.pi, np.pi))
                    color = "#CFB87C" if cond == "AXAB" else "#9400D3"
                    fig.add_trace(go.Barpolar(
                        r=counts, theta=(bins[:-1] + bins[1:])/2 * 180 / np.pi,
                        name=f"{layer} - {cond} (PLV: {data['plv']:.3f})",
                        marker=dict(color=color, line=dict(color="#FFFFFF", width=1)),
                        opacity=0.7, subplot="polar" if i == 0 else f"polar{i+1}"
                    ))

        fig.update_layout(
            title=dict(text=f"Figure f043: Laminar SFC (Delta 2-4Hz) - {area}", font=dict(color="#CFB87C", size=22)),
            template="plotly_dark", paper_bgcolor="#000000", plot_bgcolor="#000000",
            font=dict(color="#FFFFFF", family="Outfit"),
            polar=dict(
                bgcolor="#000000", domain=dict(x=[0, 0.32], y=[0, 1]),
                radialaxis=dict(visible=True, gridcolor="#555", tickfont=dict(color="#FFF")),
                angularaxis=dict(visible=True, gridcolor="#555", tickfont=dict(color="#FFF"))
            ),
            polar2=dict(
                bgcolor="#000000", domain=dict(x=[0.34, 0.66], y=[0, 1]),
                radialaxis=dict(visible=True, gridcolor="#555", tickfont=dict(color="#FFF")),
                angularaxis=dict(visible=True, gridcolor="#555", tickfont=dict(color="#FFF"))
            ),
            polar3=dict(
                bgcolor="#000000", domain=dict(x=[0.68, 1], y=[0, 1]),
                radialaxis=dict(visible=True, gridcolor="#555", tickfont=dict(color="#FFF")),
                angularaxis=dict(visible=True, gridcolor="#555", tickfont=dict(color="#FFF"))
            ),
            margin=dict(t=120, b=50, l=50, r=50),
            height=800
        )
        fig.write_html(str(output_dir / f"f043_laminar_sfc_{area}.html"))

if __name__ == "__main__":
    run_laminar_sfc()
