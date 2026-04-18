# core
import numpy as np
import plotly.graph_objects as go
from src.analysis.visualization.poster_figures import plot_spectral_network
from src.analysis.io.logger import log

def plot_connectivity_graphs(tensor: dict, areas: list, output_dir: str = "D:/drive/outputs/oglo-8figs/f013"):
    """
    Plots Figure 13 connectivity graphs for all frames.
    """
    if "AXAB" not in tensor: return
    
    for fk, frame_data in tensor["AXAB"].items():
        if "Beta" not in frame_data: continue
        adj_mat = frame_data["Beta"]
        
        # Scale for visualization
        scaled_mat = adj_mat / (np.max(adj_mat) + 1e-10)
        
        fig = plot_spectral_network(
            adj_matrix=scaled_mat,
            areas=areas,
            edge_threshold=0.2,
            band_label="Beta",
            title=f"Figure 13: Functional Connectivity Graph - {fk}",
            layout="hierarchy"
        )
        
        out_path = f"{output_dir}/fig13_graph_{fk}.html"
        fig.write_html(out_path, include_plotlyjs="cdn")
