# core
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_band_dynamics(results: dict, output_dir: str):
    """
    Plots Figure 6 band dynamics with real SEM.
    """
    from src.analysis.lfp.lfp_constants import GOLD, VIOLET
    colors = {"Theta": "#4B0082", "Alpha": "#0000FF", "Beta": VIOLET, "Gamma": GOLD}
    
    for area, res in results.items():
        plotter = OmissionPlotter(
            title=f"Figure 6: {area} Band-Specific Omission Dynamics",
            subtitle="Relative Power (dB) with ±SEM | 0ms = Omission"
        )
        plotter.set_axes("Time from Omission", "ms", "Relative Power", "dB")
        
        # res["bands_full"] is {band_name: (trials, channels, times)}
        for band_name, data in res["bands_full"].items():
            color = colors.get(band_name, GOLD)
            
            # Collapse channels first, then compute trial-wise stats
            trial_traces = np.mean(data, axis=1) # (trials, times)
            mean_trace = np.mean(trial_traces, axis=0)
            sem_trace = np.std(trial_traces, axis=0) / np.sqrt(trial_traces.shape[0])
            
            rgba = f'rgba{tuple(list(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + [0.2])}'
            plotter.add_trace(go.Scatter(x=res["times"], y=mean_trace+sem_trace, mode='lines', line=dict(width=0), showlegend=False), name=f"{band_name}_up")
            plotter.add_trace(go.Scatter(x=res["times"], y=mean_trace-sem_trace, fill='tonexty', mode='lines', line=dict(width=0), fillcolor=rgba, showlegend=False), name=f"{band_name}_down")
            plotter.add_trace(go.Scatter(x=res["times"], y=mean_trace, mode='lines', line=dict(color=color, width=3)), name=band_name)
            
        plotter.add_xline(0, name="Omission", color="black")
        plotter.fig.update_xaxes(range=[-500, 1000])
        plotter.save(output_dir, f"fig6_band_power_local_{area}")
