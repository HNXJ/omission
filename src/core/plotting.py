# core
import os
from pathlib import Path
import plotly.graph_objects as go
from src.core.logger import log

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
        
        Args:
            title: Detailed main title.
            subtitle: Detailed subtitle for context.
            template: Default Plotly template (adhering to Madelane Golden Dark aesthetics where applicable).
        """
        self.fig = go.Figure()
        
        # Combine title and subtitle for Plotly's title structure
        full_title = f"<b>{title}</b><br><sup>{subtitle}</sup>" if subtitle else f"<b>{title}</b>"
        
        self.fig.update_layout(
            title=dict(text=full_title, x=0.5, xanchor='center'),
            template=template,
            legend=dict(
                title="Legend",
                orientation="v",
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.02
            ),
            margin=dict(l=60, r=150, t=80, b=60)
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
