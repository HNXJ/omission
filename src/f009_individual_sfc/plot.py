import plotly.graph_objects as go
from plotly.subplots import make_subplots
from src.analysis.io.logger import log
import numpy as np
import os
from src.analysis.visualization.plotting import OmissionPlotter

def compute_mrv(phases):
    if not len(phases):
        return 0.0, 0.0
    R = np.mean(np.exp(1j * np.array(phases)))
    return np.abs(R), np.angle(R)

def plot_individual_sfc(results: dict, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    
    bands = ["Theta", "Beta", "Gamma"]
    colors = {"Theta": "#FF0000", "Beta": "#0000FF", "Gamma": "#A52A2A"}
    conditions = ["Omission", "Expected", "Standard"]
    
    for cls_name, data in results.items():
        # 1. Bar Plot
        plotter = OmissionPlotter(
            title=f"Figure f009: {cls_name} Spike-Field Coherence",
            subtitle=f"Pairwise Phase Consistency (PPC) Z-Score | N=20 Units"
        )
        plotter.set_axes("Condition", "", "Coherence Z-score", "σ")
        
        for b in bands:
            means = []
            sems = []
            for cond in conditions:
                z_scores = data[cond][b]["z"]
                means.append(np.nanmean(z_scores))
                sems.append(np.nanstd(z_scores) / np.sqrt(max(1, len(z_scores))))
                
            plotter.add_trace(go.Bar(
                x=conditions,
                y=means,
                error_y=dict(type='data', array=sems, visible=True),
                marker_color=colors[b]
            ), name=b)
            
        plotter.fig.update_layout(barmode='group')
        plotter.save(output_dir, f"f009_sfc_barplot_{cls_name.replace('+', 'plus').replace('-', 'minus')}")
        
        # 2. Polar Plots
        # Create a 1x3 subplot for Omission, Expected, Standard for a specific band (e.g., Gamma),
        # or a 3x3 grid (Bands x Conditions).
        # To keep it simple, we'll just plot one large 3x3 figure per class.
        fig = make_subplots(
            rows=3, cols=3, specs=[[{'type': 'polar'}]*3]*3,
            subplot_titles=[f"{b} - {c}" for b in bands for c in conditions]
        )
        
        for i, b in enumerate(bands):
            for j, cond in enumerate(conditions):
                phases = data[cond][b]["phases"]
                if not phases: continue
                
                # Polar histogram
                hist, bin_edges = np.histogram(phases, bins=24, range=(-np.pi, np.pi))
                bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
                
                fig.add_trace(go.Barpolar(
                    r=hist,
                    theta=np.degrees(bin_centers),
                    marker_color=colors[b],
                    opacity=0.7,
                    showlegend=False
                ), row=i+1, col=j+1)
                
                # Add MRV vector
                R, angle = compute_mrv(phases)
                if R > 0:
                    max_r = max(hist) if len(hist) else 1
                    fig.add_trace(go.Scatterpolar(
                        r=[0, R * max_r * 2], # scale arrow for visibility
                        theta=[0, np.degrees(angle)],
                        mode='lines',
                        line=dict(color='black', width=3),
                        showlegend=False
                    ), row=i+1, col=j+1)
                    
        fig.update_layout(
            title=f"<b>Figure f009: {cls_name} Phase Distributions</b>",
            template="plotly_white",
            height=900, width=900,
            polar=dict(radialaxis=dict(showticklabels=False)),
            polar2=dict(radialaxis=dict(showticklabels=False)),
            polar3=dict(radialaxis=dict(showticklabels=False)),
            polar4=dict(radialaxis=dict(showticklabels=False)),
            polar5=dict(radialaxis=dict(showticklabels=False)),
            polar6=dict(radialaxis=dict(showticklabels=False)),
            polar7=dict(radialaxis=dict(showticklabels=False)),
            polar8=dict(radialaxis=dict(showticklabels=False)),
            polar9=dict(radialaxis=dict(showticklabels=False)),
            modebar_add=['toImage']
        )
        
        polar_file = os.path.join(output_dir, f"f009_sfc_polar_{cls_name.replace('+', 'plus').replace('-', 'minus')}.html")
        fig.write_html(polar_file, include_plotlyjs="cdn")
        
        # Override to SVG
        try:
            fig.write_image(polar_file.replace(".html", ".svg"), engine="kaleido")
        except:
            pass
            
    log.progress("Finished plotting f009 SFC and Phase distributions.")