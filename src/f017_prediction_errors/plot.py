# beta
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log

def plot_prediction_error_scaling(results: dict, output_dir: str):
    """
    Plots Figure 17: Scaling of Prediction Error (Surprise) across sequence positions.
    results: {area: {pos: [values]}}
    """
    plotter = OmissionPlotter(
        title="Figure 17: Prediction Error Scaling across the Hierarchy",
        subtitle="Contrast: Omission - Standard (Hz) | O+ Classified Units"
    )
    plotter.set_axes("Sequence Position", "Index", "Surprise Transient", "Hz")
    
    positions = ["p2", "p3", "p4"]
    x_labels = ["2nd (P2)", "3rd (P3)", "4th (P4)"]
    
    # Madelane Golden Dark inspired color palette
    colors = ["#CFB87C", "#8F00FF", "#FF1493", "#00FFCC", "#FF5E00", "#D3D3D3"]
    
    for i, (area, pos_data) in enumerate(results.items()):
        means = [sum(pos_data[p])/len(pos_data[p]) if pos_data[p] else 0 for p in positions]
        stds = [0 for _ in positions] # Simplified for now
        
        if any(means):
            plotter.add_trace(
                go.Scatter(
                    x=x_labels, 
                    y=means, 
                    mode='lines+markers',
                    line=dict(color=colors[i % len(colors)], width=3),
                    marker=dict(size=10)
                ),
                name=area
            )
            
    # Add timing reference line if applicable (not here as it's X=category)

    plotter.save(output_dir, "fig17_prediction_error_scaling")
