import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log
import os

def plot_spectral_harmony(results: dict, areas: list, output_dir: str):
    """
    Plots Figure f008 spectral harmony heatmaps.
    """
    os.makedirs(output_dir, exist_ok=True)
    for name, mat in results.items():
        if name in ["stats", "stars"]: continue
        
        print(f"[action] Plotting Spectral Harmony: {name}")
        band, window = name.split("_")
        
        # Extract stats for this band
        stars_matrix = None
        stars_representative = ""
        p_val = 1.0
        tier = "Null"
        if "stars" in results and band in results["stars"]:
            stars_matrix = results["stars"][band]
            # Use a representative pair for the title (e.g., V1-PFC which is 0, 10)
            stars_representative = stars_matrix[0, 10] if stars_matrix.shape[1] > 10 else stars_matrix[0, 1]
            p_val = results["stats"][band][0, 10] if stars_matrix.shape[1] > 10 else results["stats"][band][0, 1]
            tier = "Sig-k" if p_val < 0.05 else "Insignificant"

        plotter = OmissionPlotter(
            title=f"Figure f008: {band} Band Harmony ({window}) {stars_representative}",
            x_label="Target Area",
            y_label="Source Area",
            subtitle=f"{tier} (p={p_val:.2e}) {stars_representative} | {window} Window (11x11 Coordination)",
            x_unit="Hierarchy",
            y_unit="Hierarchy"
        )
        
        heatmap = go.Heatmap(
            z=mat, x=areas, y=areas, 
            text=stars_matrix,
            texttemplate="%{text}",
            colorscale="Viridis" if band == "Beta" else "Plasma",
            colorbar=dict(title="Pearson r"), zmin=-0.1, zmax=1.0
        )
        plotter.add_trace(heatmap, name=name)
        
        # Ensure aspect ratio is square for matrices
        plotter.fig.update_layout(width=700, height=700, yaxis=dict(autorange="reversed"))
        
        filename = f"f008_spectral_harmony_{name}"
        plotter.save(output_dir, filename)
        log.progress(f"Saved {filename}.html")
