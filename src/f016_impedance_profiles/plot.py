# beta
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
import numpy as np

def plot_impedance(results: dict, output_dir: str):
    """
    Plots Figure 16 impedance profile using OmissionPlotter.
    """
    z_eff = results['z_eff']
    z_mag = np.abs(z_eff)
    z_phase = np.angle(z_eff, deg=True)
    
    # Impedance Magnitude Plot
    plotter_mag = OmissionPlotter(title=f"Figure 16: Impedance Mag (Session {results['session']}, x_label="Frequency", y_label="Impedance (kOhm)")", subtitle="Magnitude")
    plotter_mag.add_trace(go.Heatmap(z=z_mag, x=results['freqs'], y=results['depths'], colorscale="Viridis"), name="Z Mag")
    plotter_mag.save(output_dir, f"fig16_impedance_mag_ses{results['session']}")
    
    # Impedance Phase Plot
    plotter_phase = OmissionPlotter(title=f"Figure 16: Impedance Phase (Session {results['session']}, x_label="Frequency", y_label="Impedance (kOhm)")", subtitle="Phase (deg)")
    plotter_phase.add_trace(go.Heatmap(z=z_phase, x=results['freqs'], y=results['depths'], colorscale="RdBu", zmid=0), name="Z Phase")
    plotter_phase.save(output_dir, f"fig16_impedance_phase_ses{results['session']}")
