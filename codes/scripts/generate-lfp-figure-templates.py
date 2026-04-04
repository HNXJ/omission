#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from codes.functions.lfp_constants import WHITE, BLACK, EVENT_LINES_MS


def blank_panel(title: str, subtitle: str) -> go.Figure:
    fig = make_subplots(rows=1, cols=1)
    fig.add_annotation(text=f"{title}<br><sup>{subtitle}</sup>", x=0.5, y=0.5, showarrow=False, font=dict(size=20, color=BLACK))
    fig.update_layout(template="plotly_white", paper_bgcolor=WHITE, plot_bgcolor=WHITE)
    return fig


def main() -> None:
    out = Path("figures_templates")
    out.mkdir(exist_ok=True)
    templates = {
        "fig_05_lfp_dB_ext_template": ("Time-Frequency Response", "All omission conditions; full window"),
        "fig_06_lfp_dB_ext_bands_template": ("Band Power Summary", "Theta/Alpha/Beta/Gamma with mean ± SEM"),
        "fig_07_lfp_spike_corr_template": ("LFP-Feature Correlation", "Reserved for future hybrid analyses"),
        "fig_08_post_omission_template": ("Post-Omission Adaptation", "Per-neuron / per-area future panel"),
    }
    for stem, (title, subtitle) in templates.items():
        fig = blank_panel(title, subtitle)
        fig.write_html(out / f"{stem}.html")
        try:
            fig.write_image(out / f"{stem}.svg")
        except Exception:
            pass


if __name__ == "__main__":
    main()
