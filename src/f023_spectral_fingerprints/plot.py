# beta
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log
import numpy as np

def plot_spectral_fingerprints(freqs: np.ndarray, results: dict, output_dir: str):
    """
    Plots Figure 23: Spectral Fingerprints.
    """
    plotter = OmissionPlotter(
        title="Figure 23: Spectral Fingerprints",
        subtitle="Power Spectral Density (PSD) during Omission Window"
    )
    plotter.set_axes("Frequency", "Hz", "Power", "dB")
    
    # Allowed color palette: [Red, Blue, Brown, Green, Orange, Purple, Yellow]
    colors = ["#FF0000", "#0000FF", "#A52A2A", "#008000", "#FFA500", "#800080", "#FFFF00"]
    
    for i, (area, data) in enumerate(results.items()):
        plotter.add_shaded_error_bar(
            freqs, 
            data['mean'], 
            data['sem'], 
            name=area, 
            color=colors[i % len(colors)]
        )
        print(f"""[action] Plotted shaded error bar for spectral fingerprint of {area}""")
            
    # Add band reference lines
    plotter.add_xline(30, "Beta/Gamma Border", color="gray", dash="dot")
    plotter.add_xline(13, "Alpha/Beta Border", color="gray", dash="dot")

    plotter.save(output_dir, "fig23_spectral_fingerprints")
