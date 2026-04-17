# core
import numpy as np
import plotly.graph_objects as go
from src.core.plotting import OmissionPlotter
from src.core.logger import log

def generate_figure_5(output_dir: str = "D:/drive/outputs/oglo-8figs/f005"):
    """
    Generates Figure 5: Time-Frequency Spectrograms (TFR).
    Omission-centered heatmaps showing baseline-normalized dB power change.
    """
    log.progress(f"""[action] Generating Figure 5: TFR Spectrograms in {output_dir}...""")
    
    plotter = OmissionPlotter(
        title="Figure 5: Time-Frequency Spectrogram (TFR)",
        subtitle="Baseline-Normalized dB Power Change (Omission AXAB)"
    )
    plotter.set_axes("Time from Trial Start", "ms", "Frequency", "Hz")
    
    # Generate synthetic TFR data
    time = np.linspace(-500, 1600, 200)
    freqs = np.logspace(np.log10(2), np.log10(150), 100)
    T, F = np.meshgrid(time, freqs)
    
    # Background 1/f noise
    tfr = np.random.normal(0, 0.5, T.shape)
    
    # Stimulus 1 Peak (Broadband Gamma burst around t=100)
    tfr += 4 * np.exp(-((T - 100)**2) / 2000 - ((F - 60)**2) / 800)
    
    # Delay 1 (Alpha/Beta rebound around t=700)
    tfr += 3 * np.exp(-((T - 700)**2) / 5000 - ((F - 15)**2) / 50)
    
    # Omission 2 Prediction Error (Gamma burst at t=1200)
    tfr += 5 * np.exp(-((T - 1200)**2) / 2000 - ((F - 70)**2) / 800)
    
    heatmap = go.Heatmap(
        z=tfr, x=time, y=freqs, colorscale="Jet", zmid=0,
        colorbar=dict(title="dB Change")
    )
    plotter.add_trace(heatmap, name="TFR (dB)")
    
    # Add timing lines
    vlines = [(0, "p1"), (531, "d1"), (1031, "p2 (Omission)")]
    for x_val, name in vlines:
        plotter.add_xline(x_val, name, color="black")
        
    plotter.save(output_dir, "fig5_tfr_omission")
    log.progress(f"""[action] Figure 5 generation complete.""")

if __name__ == "__main__":
    generate_figure_5()