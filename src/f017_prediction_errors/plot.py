# beta
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log

def plot_prediction_error_scaling(results: dict, output_dir: str):
    """
    Plots Figure 17: Scaling of Prediction Error (Surprise) with residual error vectors.
    """
    print(f"""[action] Plotting prediction error scaling and residuals""")
    plotter = OmissionPlotter(
        title="Figure 17: Prediction Error Scaling across the Hierarchy",
        subtitle="Cross-validated Surprise Residuals (Manifold Distance)"
    )
    plotter.set_axes("Sequence Position", "Index", "Surprise Residual", "Hz")
    
    positions = ["p2", "p3", "p4"]
    x_labels = ["2nd (P2)", "3rd (P3)", "4th (P4)"]
    colors = ["#CFB87C", "#8F00FF", "#FF1493", "#00FFCC", "#FF5E00", "#D3D3D3"]
    
    for i, (area, pos_data) in enumerate(results.items()):
        means = [np.mean(pos_data[p]) if pos_data[p] else 0 for p in positions]
        
        # Plot Residuals
        plotter.add_trace(
            go.Scatter(
                x=x_labels, 
                y=means, 
                mode='markers',
                marker=dict(color=colors[i % len(colors)], size=12, symbol='diamond'),
                name=f"{area} Residual"
            ),
            name=area
        )
        
        # Add Error Vectors (Lines from baseline to residual)
        for j, pos in enumerate(positions):
            val = means[j]
            plotter.fig.add_trace(go.Scatter(
                x=[x_labels[j], x_labels[j]], y=[0, val],
                mode='lines', line=dict(color=colors[i % len(colors)], width=1, dash='dot'),
                showlegend=False
            ))
            
    plotter.save(output_dir, "fig17_prediction_error_scaling")
    print(f"""[action] Saved Figure 17 with residual error vectors""")
