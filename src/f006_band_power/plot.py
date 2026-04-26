import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log
import numpy as np
import os
from scipy.ndimage import gaussian_filter1d
from src.analysis.io.loader import DataLoader
from src.analysis.lfp.lfp_constants import TIMING_MS

def plot_band_dynamics(results: dict, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    loader = DataLoader()
    
    colors = {
        "theta": "#4B0082", 
        "alpha": "#0000FF", 
        "beta": "#9400D3", # VIOLET
        "low_gamma": "#CFB87C", # GOLD
        "high_gamma": "#D55E00" 
    }
    
    for cond, area_data in results.items():
        onset_ms = loader.get_omission_onset(cond)
        for area, res in area_data.items():
            print(f"[action] Plotting Band Dynamics for {area} ({cond})")
            plotter = OmissionPlotter(
                title=f"Figure f006: {area} Band-Specific Omission Dynamics ({cond})",
                subtitle="Relative Power (dB) with ±SEM | 0ms = Omission Onset | 30ms Smoothed"
            )
            plotter.set_axes("Time from Omission", "ms", "Relative Power", "dB")
            
            times = res["times"]
            
            for band_name, data in res["bands_full"].items():
                color = colors.get(band_name.lower(), "#CFB87C")
                
                # Collapse channels first, then compute trial-wise stats
                trial_traces = np.mean(data, axis=1) # (trials, times)
                mean_trace = np.mean(trial_traces, axis=0)
                sem_trace = np.std(trial_traces, axis=0) / np.sqrt(trial_traces.shape[0])
                
                # Apply 30ms smoothing
                dt = times[1] - times[0]
                sigma_samples = max(1, int(30.0 / dt))
                
                mean_trace = gaussian_filter1d(mean_trace, sigma=sigma_samples)
                sem_trace = gaussian_filter1d(sem_trace, sigma=sigma_samples)
                
                rgba = f'rgba{tuple(list(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + [0.15])}'
                
                plotter.add_trace(go.Scatter(x=times, y=mean_trace+sem_trace, mode='lines', line=dict(width=0), showlegend=False), name=f"{band_name}_up")
                plotter.add_trace(go.Scatter(x=times, y=mean_trace-sem_trace, fill='tonexty', mode='lines', line=dict(width=0), fillcolor=rgba, showlegend=False), name=f"{band_name}_down")
                plotter.add_trace(go.Scatter(x=times, y=mean_trace, mode='lines', line=dict(color=color, width=3)), name=band_name)
                
            # Add Sequence Timing Markers shifted by omission onset
            for marker_name, t_val in TIMING_MS.items():
                shifted_t = t_val - onset_ms
                if -1500 <= shifted_t <= 2000: # Only plot relevant markers
                    dash_style = "dot" if marker_name.startswith("d") else "dash"
                    # Marker name to Upper for label
                    label = marker_name.upper()
                    plotter.add_xline(shifted_t, label, color="gray", dash=dash_style)

            plotter.add_xline(0, "OMISSION (P2)", color="red", dash="dash")
            plotter.fig.update_xaxes(range=[-2000, 2000])

            # Save with name expected by dashboard
            filename = f"fig6_band_power_{area}"
            plotter.save(output_dir, filename)
            log.progress(f"Saved {filename}.html")
