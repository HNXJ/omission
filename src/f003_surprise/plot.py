import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log

def plot_surprise(results: dict, output_dir: str):
    """
    Plots a bar chart of the Surprise Index across the hierarchy.
    """
    print(f"[action] Plotting Surprise Index Bar Chart")
    plotter = OmissionPlotter(
        title="Figure f003: Population Surprise Index",
        subtitle="Surprise = (Omission - Standard) / (Omission + Standard) | Window: [0, 500]ms"
    )
    
    areas = list(results.keys())
    means = [results[a]['mean'] for a in areas]
    sems = [results[a]['sem'] for a in areas]
    
    plotter.set_axes("Cortical Area", "", "Surprise Index", "a.u.")
    
    plotter.fig.add_trace(go.Bar(
        x=areas,
        y=means,
        error_y=dict(type='data', array=sems, visible=True),
        marker_color="#9400D3",
        marker_line=dict(width=1, color="black")
    ))
    
    import os
    os.makedirs(output_dir, exist_ok=True)
    filename = "f003_surprise_index.html"
    filepath = os.path.join(output_dir, filename)
    plotter.fig.write_html(filepath, include_plotlyjs="cdn")
    log.progress(f"Saved {filename}")
