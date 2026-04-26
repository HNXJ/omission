import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log
import os
import numpy as np

def plot_spectral_identity_correlation(results: dict, output_dir: str):
    """
    Plots the correlation between oscillatory power and identity decoding accuracy.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Bar plot of correlations per area/band
    plotter_bars = OmissionPlotter(
        title="Figure f028: Spectral-Identity Coupling",
        subtitle="Pearson Correlation: Band Power vs. Identity Decoding Accuracy (Omission Window)"
    )
    plotter_bars.set_axes("Area", "", "Correlation (r)", "")
    
    areas = list(results.keys())
    bands = ["delta", "theta", "alpha", "beta", "low_gamma", "high_gamma"]
    
    colors = {
        "delta": "#8B4513", "theta": "#4B0082", "alpha": "#0000FF", 
        "beta": "#9400D3", "low_gamma": "#CFB87C", "high_gamma": "#D55E00"
    }
    
    for band in bands:
        corrs = [results[a]["correlations"].get(band, 0) for a in areas]
        plotter_bars.add_trace(go.Bar(
            name=band.upper(),
            x=areas,
            y=corrs,
            marker_color=colors.get(band, "#888888")
        ))
        
    plotter_bars.save(output_dir, "f028_correlation_summary")
    
    # 2. Detail plots for each area: Traces
    for area, res in results.items():
        plotter_detail = OmissionPlotter(
            title=f"Figure f028: {area} Trace Correlation",
            subtitle="Overlay of Decoding Accuracy and Dominant Oscillatory Band"
        )
        plotter_detail.set_axes("Time from Omission", "ms", "Normalized Value", "")
        
        # Plot Decoding Accuracy (Normalized to [0,1])
        acc = res["dec_acc"]
        acc_norm = (acc - 0.5) / (max(acc) - 0.5 + 1e-9)
        plotter_detail.add_trace(go.Scatter(
            x=res["dec_times"], y=acc_norm, 
            name="Identity Decoding", 
            line=dict(color="black", width=4)
        ))
        
        # Plot Top 2 Correlated Bands
        sorted_bands = sorted(res["correlations"].items(), key=lambda x: abs(x[1]), reverse=True)
        for band, r_val in sorted_bands[:2]:
            spec = res["spectral"][band]
            spec_norm = (spec - min(spec)) / (max(spec) - min(spec) + 1e-9)
            plotter_detail.add_trace(go.Scatter(
                x=res["spec_times"], y=spec_norm, 
                name=f"{band.upper()} (r={r_val:.2f})",
                line=dict(color=colors.get(band, "gray"), dash="dash")
            ))
            
        plotter_detail.add_xline(0, "Omission", color="red")
        plotter_detail.save(output_dir, f"f028_detail_{area}")
        
    log.progress("Spectral-Identity Correlation plots saved.")
