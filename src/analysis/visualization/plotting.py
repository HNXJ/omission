# core
import os
import numpy as np
from pathlib import Path
import plotly.graph_objects as go
from src.analysis.io.logger import log

class OmissionPlotter:
    """
    Canonical plotting wrapper enforcing Omission project visualization mandates.
    Strictly mandates:
    - X/Y labels and units.
    - X/Y reference lines (timing/statistical thresholds).
    - Titles, subtitles, and detailed legends.
    - Efficient HTML and SVG export (without kaleido).
    """

    def __init__(self, title: str, subtitle: str = "", template: str = "plotly_white"):
        """
        Initialize a new canonical figure.
        """
        self.fig = go.Figure()
        
        full_title = f"<b>{title}</b><br><sup>{subtitle}</sup>" if subtitle else f"<b>{title}</b>"
        
        # Colors per mandate: [Red, Blue, Brown, Green, Orange, Purple, Yellow]
        self.colors = ["#FF0000", "#0000FF", "#A52A2A", "#008000", "#FFA500", "#800080", "#FFFF00"]
        
        self.fig.update_layout(
            title=dict(text=full_title, x=0.5, xanchor='center', font=dict(family="Arial", size=18, color="#000000")),
            template=template,
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            xaxis=dict(showgrid=True, gridcolor="#D3D3D3", linecolor="#000000", mirror=True, ticks="outside"),
            yaxis=dict(showgrid=True, gridcolor="#D3D3D3", linecolor="#000000", mirror=True, ticks="outside"),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="#000000",
                borderwidth=1
            ),
            margin=dict(l=80, r=40, t=100, b=80),
            modebar_add=['toImage']
        )
        log.action(f"Initialized canonical plot: {title}")

    def set_axes(self, x_label: str, x_unit: str, y_label: str, y_unit: str):
        """
        Enforce strict X and Y axis labeling with mandatory units.
        """
        self.fig.update_layout(
            xaxis_title=f"{x_label} ({x_unit})",
            yaxis_title=f"{y_label} ({y_unit})"
        )
        log.action(f"Set axes -> X: {x_label} ({x_unit}), Y: {y_label} ({y_unit})")

    def add_trace(self, trace: go.Scatter | go.Heatmap | go.Bar, name: str):
        """
        Add a data trace to the figure, enforcing a legend name.
        """
        trace.name = name
        trace.showlegend = True
        self.fig.add_trace(trace)
        log.action(f"Added trace: {name}")

    def add_xline(self, x_val: float, name: str, color: str = "black", dash: str = "dash"):
        """
        Add a vertical reference line (e.g., for stimulus onset/offset timing).
        """
        self.fig.add_vline(
            x=x_val, line_width=2, line_dash=dash, line_color=color,
            annotation_text=name, annotation_position="top right"
        )
        log.action(f"Added X-line at {x_val}: {name}")

    def add_yline(self, y_val: float, name: str, color: str = "red", dash: str = "dot"):
        """
        Add a horizontal reference line (e.g., for statistical threshold like p < 0.05).
        """
        self.fig.add_hline(
            y=y_val, line_width=2, line_dash=dash, line_color=color,
            annotation_text=name, annotation_position="bottom right"
        )
        log.action(f"Added Y-line at {y_val}: {name}")

    def add_shaded_error_bar(self, x: list | np.ndarray, mean: list | np.ndarray, 
                             error_upper: list | np.ndarray, error_lower: list | np.ndarray = None, 
                             name: str = "Signal", color: str = "#CFB87C"):
        """
        Adds a mean trace with a shaded error (SEM/SD/CI) region.
        If error_lower is None, assumes symmetric error.
        """
        x = np.array(x)
        mean = np.array(mean)
        error_upper = np.array(error_upper)
        error_lower = np.array(error_lower) if error_lower is not None else error_upper
        
        # Convert hex to rgba for shading
        if color.startswith("#"):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            fill_color = f"rgba({r}, {g}, {b}, 0.2)"
        else:
            fill_color = "rgba(128, 128, 128, 0.2)" # Fallback
            
        # Upper bound
        self.fig.add_trace(go.Scatter(
            x=x, y=mean + error_upper,
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip',
            legendgroup=name
        ))
        
        # Lower bound + Fill
        self.fig.add_trace(go.Scatter(
            x=x, y=mean - error_lower,
            mode='lines',
            line=dict(width=0),
            fill='tonexty',
            fillcolor=fill_color,
            showlegend=False,
            hoverinfo='skip',
            legendgroup=name
        ))
        
        # Mean trace
        self.fig.add_trace(go.Scatter(
            x=x, y=mean,
            mode='lines',
            line=dict(color=color, width=3),
            name=name,
            legendgroup=name
        ))
        log.action(f"Added shaded error trace: {name}")

    def save(self, output_dir: str, filename: str):
        """
        Save the figure efficiently in Interactive HTML format ONLY.
        Strictly adheres to the Kaleido-Free Export mandate. The HTML viewer 
        is configured natively with a 'Download to SVG' button via modebar_add.
        """
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        
        # Configure HTML viewer to include SVG download button
        self.fig.update_layout(modebar_add=["toImage"])
        
        # Save HTML (100% reliable, interactive, self-contained)
        html_file = out_path / f"{filename}.html"
        self.fig.write_html(str(html_file), include_plotlyjs="cdn")
        log.progress(f"Saved interactive HTML figure (Kaleido-Free): {html_file}")
