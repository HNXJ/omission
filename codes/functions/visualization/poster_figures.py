"""
poster_figures.py
=================
Exact replication functions for every data figure in:
  - Poster 01: "Neural Dynamics during Omission Support Spectral Aspects of the Predictive Routing Model"
  - Poster 02: "Omission Reveals the Functional Role of Neuronal Oscillations in Predictive Routing"

All figures use the Madelane Golden Dark palette (Gold=#CFB87C, Violet=#8F00FF, Black=#000000)
and plotly_white theme. Each function is self-contained and outputs a go.Figure.

Data flows:
  codes/functions/lfp_io.py         -> load_session / load_condition_table
  codes/functions/lfp_preproc.py    -> apply_bipolar_ref / baseline_normalize / extract_epochs
  codes/functions/lfp_tfr.py        -> compute_tfr / get_band_power / collapse_band_power
  codes/functions/lfp_stats.py      -> mean_sem
  codes/functions/lfp_connectivity.py -> compute_coherence
  codes/functions/omission_hierarchy_utils.py -> extract_unit_traces
  -> poster_figures.py (this module)

Output: .html (interactive) + .svg (vector) saved to output/
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple
import numpy as np
import plotly.graph_objects as go
import plotly.colors as pc
from plotly.subplots import make_subplots
import networkx as nx

from codes.functions.lfp.lfp_constants import (
    GOLD, BLACK, VIOLET, PINK, TEAL, ORANGE, GRAY, WHITE,
    SEQUENCE_TIMING_MS, BANDS, CANONICAL_AREAS, OMISSION_ANALYSIS_WINDOWS_MS,
    OMISSION_PATCH_WINDOWS_MS, HIERARCHY
)

# Use canonical constants
AREA_ORDER: List[str] = CANONICAL_AREAS
OMISSION_WINDOWS: Dict[str, Tuple[int, int]] = OMISSION_ANALYSIS_WINDOWS_MS

# Condition color assignments (matches poster color coding)
CONDITION_COLORS: Dict[str, str] = {
    "RRRR":  GOLD,
    "RXRR":  VIOLET,
    "RRXR":  TEAL,
    "RRRX":  ORANGE,
    "AAAB":  "#4285F4",   # Google Blue (standard predictive)
    "AXAB":  VIOLET,
    "AAXB":  TEAL,
    "AAAX":  ORANGE,
}

# Band colors for spectral power traces
BAND_COLORS: Dict[str, str] = {
    "Theta": "#FF6B6B",
    "Alpha": "#FFA500",
    "Beta":  VIOLET,
    "Gamma": GOLD,
}


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _apply_style(fig: go.Figure, title: str = "") -> go.Figure:
    """Apply Madelane Golden Dark + plotly_white theme to any figure."""
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color=BLACK, family="Arial")),
        template="plotly_white",
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        font=dict(color=BLACK, family="Arial", size=11),
        margin=dict(l=70, r=30, t=70, b=55),
        legend=dict(bgcolor="rgba(255,255,255,0.9)", bordercolor=GRAY, borderwidth=1),
    )
    fig.update_xaxes(showline=True, linecolor=BLACK, mirror=True, tickcolor=BLACK)
    fig.update_yaxes(showline=True, linecolor=BLACK, mirror=True, tickcolor=BLACK)
    return fig


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    """Convert '#RRGGBB' to 'rgba(r,g,b,a)' string."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def _add_sequence_patches(fig: go.Figure, omission_cond: Optional[str] = None,
                           row: Optional[int] = None, col: int = 1,
                           x_range: Tuple[int, int] = (-1000, 4200)) -> None:
    """
    Add vertical dashed event lines + colored rectangle patches for all sequence events.
    Adds a PINK omission patch for the specific omission window of omission_cond.

    Parameters
    ----------
    fig           : plotly Figure
    omission_cond : str or None — if provided, adds pink omission rectangle
    row, col      : subplot row/col (None for single-panel figures)
    x_range       : (min_ms, max_ms) — controls vrect x bounds for fixation
    """
    kw = dict(row=row, col=col) if row is not None else {}

    # Fixation patch (pre-stimulus)
    fig.add_vrect(x0=x_range[0], x1=0, fillcolor=GRAY, opacity=0.08,
                  line_width=0, **kw)

    # Sequence event patches + dashed onset lines
    for ev_name, info in SEQUENCE_TIMING_MS.items():
        if info["start"] < x_range[1]:
            fig.add_vrect(x0=info["start"], x1=min(info["end"], x_range[1]),
                          fillcolor=info["color"], opacity=0.12, line_width=0, **kw)
            fig.add_vline(x=info["start"], line_dash="dot", line_width=1,
                          line_color="rgba(0,0,0,0.4)", **kw)

    # Zero line (p1 onset)
    fig.add_vline(x=0, line_dash="dash", line_width=1.5, line_color=BLACK, **kw)

    # Pink omission window
    if omission_cond and omission_cond in OMISSION_WINDOWS:
        t0, t1 = OMISSION_WINDOWS[omission_cond]
        fig.add_vrect(x0=t0, x1=t1, fillcolor=PINK, opacity=0.22,
                      line_width=0, **kw)


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 1 (Both Posters — Central Figure)
# plot_band_power_hierarchy
# ─────────────────────────────────────────────────────────────────────────────

def plot_band_power_hierarchy(
    traces: Dict[str, Dict[str, Dict[str, np.ndarray]]],
    sems: Dict[str, Dict[str, Dict[str, np.ndarray]]],
    time_ms: np.ndarray,
    areas: List[str] = AREA_ORDER,
    conditions: Optional[List[str]] = None,
    band: str = "Beta",
    omission_cond: Optional[str] = None,
    title: str = "LFP Band Power across Cortical Hierarchy",
    x_range: Tuple[int, int] = (-1000, 1500),
    y_label: str = "Power (dB, Δ baseline)",
) -> go.Figure:
    """
    Main multi-area LFP band power figure from BOTH posters (Poster 01 Section 5,
    Poster 02 Section 4).

    Produces an N_areas × 1 subplot grid. Each row = one brain area (V1 at top,
    PFC at bottom). Each trace = one experimental condition. ±2SEM shaded fill.
    Pink rectangle over the omission window of the specified condition.
    Vertical dashed lines at all sequence events.

    Parameters
    ----------
    traces : nested dict  {condition: {area: {band: mean_array(n_times)}}}
        Each mean_array is shape (n_times,). Produced by:
        lfp_preproc.baseline_normalize -> lfp_tfr.get_band_power -> lfp_stats.mean_sem
    sems : same shape as traces  {condition: {area: {band: sem_array(n_times)}}}
    time_ms : np.ndarray, shape (n_times,)
        Time axis in milliseconds. p1 onset = 0ms.
    areas : list of str
        Brain areas in display order (top → bottom). Default: V1 → PFC.
    conditions : list of str or None
        Conditions to overlay. Default: all keys in traces.
    band : str
        Frequency band to plot. Must be a key in traces[cond][area].
        Default: 'Beta' (the key finding in both posters).
    omission_cond : str or None
        If provided, draws a PINK omission rectangle for this condition.
        E.g. 'RXRR' draws the p2-omission window (531–1562ms).
    title : str
    x_range : (int, int)    — x-axis display limits in ms. Default (-1000, 1500).
    y_label : str

    Returns
    -------
    go.Figure  — multi-row subplot figure

    Example
    -------
    >>> from codes.functions.io.lfp_io import load_condition_table
    >>> from codes.functions.lfp.lfp_preproc import baseline_normalize, extract_epochs
    >>> from codes.functions.lfp.lfp_tfr import get_band_power
    >>> from codes.functions.lfp.lfp_stats import mean_sem
    >>> from codes.functions.visualization.poster_figures import plot_band_power_hierarchy
    >>>
    >>> # Build traces dict from computed data
    >>> traces = {}
    >>> sems = {}
    >>> for cond in ['RRRR', 'RXRR', 'RRXR', 'RRRX']:
    ...     traces[cond] = {}
    ...     sems[cond] = {}
    ...     for area in AREA_ORDER:
    ...         epochs = extract_epochs(lfp_dict[area], onsets_ms, pre=1000, post=1500)
    ...         normed = baseline_normalize(epochs, baseline_win=(-500, 0))
    ...         pwr = get_band_power(freqs, normed, band='Beta')
    ...         m, s = mean_sem(pwr, axis=0)
    ...         traces[cond][area] = {'Beta': m}
    ...         sems[cond][area] = {'Beta': s}
    >>> fig = plot_band_power_hierarchy(traces, sems, time_ms,
    ...                                 omission_cond='RXRR', band='Beta')
    >>> fig.write_html('output/fig-band-power-hierarchy.html')
    >>> fig.write_image('output/fig-band-power-hierarchy.svg')
    """
    if conditions is None:
        conditions = list(traces.keys())

    n_areas = len(areas)
    fig = make_subplots(
        rows=n_areas, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.018,
        subplot_titles=[f"<b>{a}</b>" for a in areas],
    )

    for row_idx, area in enumerate(areas, start=1):
        show_legend = (row_idx == 1)
        for cond in conditions:
            if area not in traces.get(cond, {}): continue
            if band not in traces[cond][area]:   continue

            mean_trace = np.nan_to_num(traces[cond][area][band])
            sem_trace  = np.nan_to_num(sems[cond][area][band])
            color      = CONDITION_COLORS.get(cond, BLACK)
            rgba_fill  = _hex_to_rgba(color, 0.18)

            # +2SEM upper bound (invisible line for fill target)
            fig.add_trace(go.Scatter(
                x=time_ms, y=mean_trace + 2 * sem_trace,
                mode="lines", line=dict(width=0),
                showlegend=False, hoverinfo="skip",
            ), row=row_idx, col=1)
            # -2SEM lower bound with fill
            fig.add_trace(go.Scatter(
                x=time_ms, y=mean_trace - 2 * sem_trace,
                fill="tonexty", mode="lines",
                line=dict(width=0), fillcolor=rgba_fill,
                showlegend=False, hoverinfo="skip",
            ), row=row_idx, col=1)
            # Mean trace
            fig.add_trace(go.Scatter(
                x=time_ms, y=mean_trace, mode="lines",
                line=dict(color=color, width=1.8),
                name=cond, showlegend=show_legend,
                legendgroup=cond,
            ), row=row_idx, col=1)
            show_legend = False  # only first area shows legend per condition

        # Event patches for this row
        _add_sequence_patches(fig, omission_cond=omission_cond,
                              row=row_idx, col=1, x_range=x_range)

        # y-axis label every row
        fig.update_yaxes(title_text=y_label if row_idx == n_areas // 2 else "",
                         title_font=dict(size=10),
                         zeroline=True, zerolinecolor="rgba(0,0,0,0.2)",
                         row=row_idx, col=1)

    fig.update_xaxes(title_text="Time (ms)", range=list(x_range), row=n_areas, col=1)
    fig.update_layout(height=130 * n_areas, width=900)
    return _apply_style(fig, title)


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 2 (Poster 01 Section 4)
# plot_mua_tfr_panel
# ─────────────────────────────────────────────────────────────────────────────

def plot_mua_tfr_panel(
    mua_traces: Dict[str, Dict[str, np.ndarray]],
    tfr_data: Dict[str, Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray]]],
    time_ms: np.ndarray,
    areas: List[str] = ("V1", "MT", "FEF"),
    conditions: Optional[List[str]] = None,
    title: str = "MUA and TFR per Area per Condition",
) -> go.Figure:
    """
    Poster 01 Section 4: MUA firing-rate traces and TFR heatmaps.
    Shows that V1/MT MUA is largely unchanged by omission while FEF shows weak response.

    Layout: n_areas rows × n_conditions columns.
    Top row of each area pair: TFR heatmap (freq × time, dB, viridis).
    Bottom row of each area pair: MUA trace (spikes/s vs time_ms).

    Parameters
    ----------
    mua_traces : {area: {condition: mean_array(n_times)}}
        Mean MUA firing rate traces (spikes/s, baseline-subtracted).
    tfr_data   : {area: {condition: (freqs, times_ms, power_db)}}
        TFR tuples. power_db shape: (n_freqs, n_times).
    time_ms    : np.ndarray — shared time axis (ms, p1=0).
    areas      : tuple/list of area names to plot.
    conditions : list of str — conditions to column-plot.
    title      : str

    Returns
    -------
    go.Figure

    Example
    -------
    >>> from codes.functions.lfp.lfp_tfr import compute_tfr
    >>> from codes.functions.lfp.lfp_stats import mean_sem
    >>> tfr_data = {}
    >>> mua_traces = {}
    >>> for area in ['V1', 'MT', 'FEF']:
    ...     tfr_data[area] = {}
    ...     mua_traces[area] = {}
    ...     for cond in ['RRRR', 'RXRR']:
    ...         freqs, times, pwr = compute_tfr(epochs[area][cond], fs=1000)
    ...         tfr_data[area][cond] = (freqs, times, pwr.mean(0))
    ...         mua_traces[area][cond] = mua[area][cond].mean(0)
    >>> fig = plot_mua_tfr_panel(mua_traces, tfr_data, time_ms)
    """
    if conditions is None:
        conditions = list(next(iter(mua_traces.values())).keys())

    n_cond = len(conditions)
    n_areas = len(areas)
    # 2 rows per area (TFR on top, MUA below)
    n_rows = 2 * n_areas

    row_titles = []
    for area in areas:
        row_titles += [f"{area} TFR", f"{area} MUA"]

    fig = make_subplots(
        rows=n_rows, cols=n_cond,
        shared_xaxes=True,
        vertical_spacing=0.03,
        horizontal_spacing=0.04,
        subplot_titles=[f"<b>{c}</b>" for c in conditions],
        row_titles=row_titles,
    )

    cmap = "Viridis"
    for area_idx, area in enumerate(areas):
        tfr_row = 2 * area_idx + 1
        mua_row = 2 * area_idx + 2

        for col_idx, cond in enumerate(conditions, start=1):
            show_cbar = (area_idx == 0 and col_idx == n_cond)

            # ── TFR heatmap ──
            if area in tfr_data and cond in tfr_data[area]:
                freqs, times, pwr = tfr_data[area][cond]
                fig.add_trace(go.Heatmap(
                    z=pwr, x=times, y=freqs,
                    colorscale=cmap, showscale=show_cbar,
                    colorbar=dict(len=0.15, y=0.85, title="dB") if show_cbar else None,
                    zsmooth="best",
                ), row=tfr_row, col=col_idx)
                fig.update_yaxes(title_text="Hz" if col_idx == 1 else "",
                                 range=[0, 100], row=tfr_row, col=col_idx)

            # Event lines on TFR
            _add_sequence_patches(fig, omission_cond=cond if "X" in cond else None,
                                  row=tfr_row, col=col_idx)

            # ── MUA trace ──
            if area in mua_traces and cond in mua_traces[area]:
                trace = mua_traces[area][cond]
                color = CONDITION_COLORS.get(cond, BLACK)
                fig.add_trace(go.Scatter(
                    x=time_ms, y=trace, mode="lines",
                    line=dict(color=color, width=1.5),
                    showlegend=False,
                ), row=mua_row, col=col_idx)
                fig.update_yaxes(title_text="sp/s" if col_idx == 1 else "",
                                 row=mua_row, col=col_idx)
                # Zero reference
                fig.add_hline(y=0, line_dash="dot", line_color=GRAY,
                              line_width=0.8, row=mua_row, col=col_idx)

            _add_sequence_patches(fig, omission_cond=cond if "X" in cond else None,
                                  row=mua_row, col=col_idx)

    fig.update_xaxes(title_text="Time (ms)", range=[-1000, 1500], row=n_rows)
    fig.update_layout(height=220 * n_areas, width=280 * n_cond)
    return _apply_style(fig, title)


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 3 (Poster 01 Section 6)
# plot_spectral_corr_matrices
# ─────────────────────────────────────────────────────────────────────────────

def plot_spectral_corr_matrices(
    corr_stimulus: np.ndarray,
    corr_omission: np.ndarray,
    areas: List[str] = AREA_ORDER,
    title: str = "Spectral Power Correlation Matrices",
) -> go.Figure:
    """
    Poster 01 Section 6 — Top row: Stimulus window vs Omission window inter-area
    spectral power correlation matrices. 1×2 heatmap grid.

    Each heatmap is an (n_areas × n_areas) Pearson-r matrix. Color scale: RdBu_r
    (blue=negative, red=positive, white=zero). Diagonal = 1.0 (excluded from color).

    Parameters
    ----------
    corr_stimulus : np.ndarray, shape (n_areas, n_areas)
        Inter-area Pearson correlation of band power in the STIMULUS window
        (0–531ms relative to p1). Computed over trials × sessions.
    corr_omission : np.ndarray, shape (n_areas, n_areas)
        Same but for OMISSION window (e.g. 531–1562ms for X at position 2).
    areas : list of str — axis labels (must match matrix dimension order).

    Returns
    -------
    go.Figure — 1 row × 2 column subplot

    How to compute the input matrices
    ----------------------------------
    >>> from codes.functions.lfp.lfp_tfr import get_band_power, collapse_band_power
    >>> from codes.functions.lfp.lfp_stats import mean_sem
    >>> # band_power_per_area: dict[area] -> (n_trials, n_times) for a single band+session
    >>> # Extract mean power in window per trial per area, then correlate:
    >>> import numpy as np
    >>> stim_vecs = np.stack([
    ...     band_power_per_area[a][:, (time_ms >= 0) & (time_ms < 531)].mean(1)
    ...     for a in areas
    ... ])  # shape (n_areas, n_trials)
    >>> corr_stimulus = np.corrcoef(stim_vecs)  # (n_areas, n_areas)
    """
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["<b>Stimulus window</b>", "<b>Omission window</b>"],
        horizontal_spacing=0.12,
    )

    cmap = "RdBu_r"
    for col_idx, (corr, label) in enumerate(
        [(corr_stimulus, "Stimulus"), (corr_omission, "Omission")], start=1
    ):
        corr_display = np.array(corr, dtype=float)
        np.fill_diagonal(corr_display, np.nan)  # mask diagonal

        fig.add_trace(go.Heatmap(
            z=corr_display,
            x=areas, y=areas,
            colorscale=cmap,
            zmin=-1, zmax=1,
            showscale=(col_idx == 2),
            colorbar=dict(title="Pearson r", len=0.6, y=0.5),
            xgap=1, ygap=1,
        ), row=1, col=col_idx)

        # Annotation: r values in cells
        for i in range(len(areas)):
            for j in range(len(areas)):
                if i != j and not np.isnan(corr[i, j]):
                    fig.add_annotation(
                        x=areas[j], y=areas[i],
                        text=f"{corr[i, j]:.2f}",
                        showarrow=False, font=dict(size=7, color=BLACK),
                        row=1, col=col_idx,
                    )

    fig.update_yaxes(autorange="reversed")
    fig.update_layout(height=480, width=880)
    return _apply_style(fig, title)


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 4 (Poster 01 Section 6)
# plot_r2_change_bars
# ─────────────────────────────────────────────────────────────────────────────

def plot_r2_change_bars(
    r2_change: Dict[str, float],
    areas: List[str] = AREA_ORDER,
    title: str = "R² Change (Stimulus→Omission) by Area",
    highlight_areas: Optional[List[str]] = None,
) -> go.Figure:
    """
    Poster 01 Section 6 — Bar chart showing the change in spectral correlation
    (R²) between the stimulus and omission windows, per brain area.
    FEF/PFC show the LEAST change (most stable spectral nodes).

    Parameters
    ----------
    r2_change : dict {area: float}
        R² difference: r2_omission - r2_stimulus. Positive = more correlated in omission.
    areas : list — controls order of bars along x-axis.
    highlight_areas : list of str — these bars are colored GOLD; others BLACK.
        Default: highlight FEF and PFC (stable nodes per poster finding).

    Returns
    -------
    go.Figure — bar chart

    Example
    -------
    >>> # r2_stimulus = np.mean(np.abs(corr_stimulus[off_diagonal_mask]))
    >>> # r2_omission = np.mean(np.abs(corr_omission[off_diagonal_mask]))
    >>> r2_change = {a: r2_omit[a] - r2_stim[a] for a in AREA_ORDER}
    >>> fig = plot_r2_change_bars(r2_change, highlight_areas=['FEF', 'PFC'])
    """
    if highlight_areas is None:
        highlight_areas = ["FEF", "PFC"]

    x_vals = [a for a in areas if a in r2_change]
    y_vals = [r2_change[a] for a in x_vals]
    colors = [GOLD if a in highlight_areas else BLACK for a in x_vals]

    fig = go.Figure(go.Bar(
        x=x_vals, y=y_vals,
        marker_color=colors,
        marker_line_color=BLACK,
        marker_line_width=1.0,
        text=[f"{v:.3f}" for v in y_vals],
        textposition="outside",
        textfont=dict(size=9, color=BLACK),
    ))

    # Zero reference line
    fig.add_hline(y=0, line_color=BLACK, line_width=1.0)

    fig.update_layout(
        xaxis_title="Brain Area",
        yaxis_title="ΔR² (Omission − Stimulus)",
        showlegend=False,
        height=380, width=600,
    )
    return _apply_style(fig, title)


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 5 (Both Posters — network diagrams)
# plot_spectral_network
# ─────────────────────────────────────────────────────────────────────────────

def plot_spectral_network(
    adj_matrix: np.ndarray,
    areas: List[str] = AREA_ORDER,
    edge_threshold: float = 0.3,
    band_label: str = "Beta",
    title: str = "",
    layout: str = "hierarchy",
) -> go.Figure:
    """
    Both Posters — Directed or undirected spectral network graph.
    Nodes = brain areas. Edge weight = inter-area spectral coherence or correlation.
    Used for: Beta network (omission), Gamma network (stimulus) figures.

    Parameters
    ----------
    adj_matrix : np.ndarray, shape (n_areas, n_areas)
        Connectivity matrix. Values in [0, 1] (coherence or normalized correlation).
        adj_matrix[i, j] = connectivity from area i to area j.
    areas : list of str — node labels (must match matrix dim order).
    edge_threshold : float — only draw edges where adj_matrix > this value.
    band_label : str — 'Beta' or 'Gamma'. Controls node/edge color scheme.
    title : str
    layout : str
        'hierarchy' — nodes positioned by cortical hierarchy tier (default).
        'circular' — equal-angle circular layout.

    Returns
    -------
    go.Figure — node-edge network plot

    Color scheme
    ------------
    Beta network (omission): edges in VIOLET, nodes in GOLD.
    Gamma network (stimulus): edges in GOLD, nodes in VIOLET.

    Example
    -------
    >>> corr_omit = np.corrcoef(omission_power_vecs)  # (n_areas, n_areas)
    >>> fig = plot_spectral_network(corr_omit, areas=AREA_ORDER,
    ...                              edge_threshold=0.4, band_label='Beta')
    """
    n = len(areas)
    edge_color = VIOLET if band_label.lower() in ("beta", "alpha", "theta") else GOLD
    node_color = GOLD  if band_label.lower() in ("beta", "alpha", "theta") else VIOLET

    # ── Node positions ──────────────────────────────────────────────────────
    TIER_X: Dict[str, float] = {
        "V1": 0.1, "V2": 0.2, "V4": 0.3, "MT": 0.45, "MST": 0.55,
        "TEO": 0.62, "FST": 0.5,  "V3a": 0.72, "V3d": 0.78,
        "FEF": 0.88, "PFC": 0.95,
    }
    TIER_Y: Dict[str, float] = {
        "V1": 0.1, "V2": 0.25, "V4": 0.35, "MT": 0.4, "MST": 0.5,
        "TEO": 0.55, "FST": 0.3, "V3a": 0.65, "V3d": 0.7,
        "FEF": 0.8, "PFC": 0.9,
    }

    if layout == "circular":
        angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
        node_x = [0.5 + 0.45 * np.cos(a) for a in angles]
        node_y = [0.5 + 0.45 * np.sin(a) for a in angles]
    else:
        node_x = [TIER_X.get(a, 0.5) for a in areas]
        node_y = [TIER_Y.get(a, 0.5) for a in areas]

    # ── Edge traces ──────────────────────────────────────────────────────────
    edge_traces = []
    for i in range(n):
        for j in range(i + 1, n):
            w = float(adj_matrix[i, j])
            if w < edge_threshold:
                continue
            opacity = min(1.0, (w - edge_threshold) / (1.0 - edge_threshold))
            width   = 1.0 + 4.0 * opacity
            edge_traces.append(go.Scatter(
                x=[node_x[i], node_x[j], None],
                y=[node_y[i], node_y[j], None],
                mode="lines",
                line=dict(color=edge_color, width=width),
                opacity=opacity,
                showlegend=False,
                hoverinfo="none",
            ))

    # ── Node trace ────────────────────────────────────────────────────────────
    node_size = []
    for i, area in enumerate(areas):
        # Node size = mean outgoing connectivity
        strengths = [adj_matrix[i, j] for j in range(n) if j != i and adj_matrix[i, j] > edge_threshold]
        node_size.append(16 + 20 * (np.mean(strengths) if strengths else 0))

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        text=areas,
        textposition="top center",
        textfont=dict(size=10, color=BLACK, family="Arial"),
        marker=dict(
            size=node_size,
            color=node_color,
            line=dict(color=BLACK, width=1.5),
        ),
        showlegend=False,
        hovertext=[f"{a}: {np.mean(adj_matrix[i]):.3f}" for i, a in enumerate(areas)],
    )

    fig = go.Figure(data=edge_traces + [node_trace])
    fig.update_layout(
        xaxis=dict(visible=False, range=[0, 1.05]),
        yaxis=dict(visible=False, range=[0, 1.05]),
        height=500, width=600,
    )
    return _apply_style(fig, title or f"{band_label} spectral network")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 6 (Poster 02 Section 5)
# plot_neuron_group_traces
# ─────────────────────────────────────────────────────────────────────────────

def plot_neuron_group_traces(
    group_traces: Dict[str, np.ndarray],
    group_sems: Dict[str, np.ndarray],
    time_ms: np.ndarray,
    group_ns: Optional[Dict[str, int]] = None,
    omission_cond: str = "RXRR",
    title: str = "Single Neuron Responses to Omission",
) -> go.Figure:
    """
    Poster 02 Section 5 — Three-panel figure showing firing rate traces for:
    - Group 1: Neurons excited by stimulus (large N, ~2071)
    - Group 2: Neurons inhibited by stimulus (~1382)
    - Group 3: Neurons correlated with omission (rare, N~20)

    Layout: 3 rows × 1 column, shared x-axis.

    Parameters
    ----------
    group_traces : dict {group_label: mean_array(n_times)}
        Mean firing rate (spikes/s, baseline-subtracted) per group.
        Keys: 'stim_excited', 'stim_inhibited', 'omission_selective'
    group_sems : dict {group_label: sem_array(n_times)}
    time_ms : np.ndarray — time axis in ms, p1=0.
    group_ns : dict {group_label: int} — neuron counts for subtitle (e.g. N=2071).
    omission_cond : str — which condition to draw the omission rectangle for.
    title : str

    Returns
    -------
    go.Figure — 3-row figure

    Group color coding (matches poster)
    ------------------------------------
    stim_excited     -> Gold with warm (+) fill
    stim_inhibited   -> Blue/Violet with cool (−) fill
    omission_selective -> Pink/PINK (the rare finding)

    Example
    -------
    >>> from codes.functions.spiking.omission_hierarchy_utils import extract_unit_traces
    >>> unit_traces = extract_unit_traces('230629', conds=['RRRR','RXRR'], sigma=20)
    >>> # Classify units by response type:
    >>> stim_resp = ...   # t-test stimulus vs baseline per unit
    >>> group_traces = {
    ...     'stim_excited':     np.mean(traces_excited, axis=0),
    ...     'stim_inhibited':   np.mean(traces_inhibited, axis=0),
    ...     'omission_selective': np.mean(traces_omission, axis=0),
    ... }
    """
    GROUP_COLORS = {
        "stim_excited":      GOLD,
        "stim_inhibited":    VIOLET,
        "omission_selective": PINK,
    }
    GROUP_LABELS = {
        "stim_excited":      "Excited by stimulus",
        "stim_inhibited":    "Inhibited by stimulus",
        "omission_selective": "Correlated to omission",
    }
    if group_ns is None:
        group_ns = {}

    group_keys = list(group_traces.keys())
    n_groups   = len(group_keys)

    fig = make_subplots(
        rows=n_groups, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        subplot_titles=[
            f"<b>{GROUP_LABELS.get(k, k)}</b>   N={group_ns.get(k, '?')}"
            for k in group_keys
        ],
    )

    for row_idx, key in enumerate(group_keys, start=1):
        mean_trace = np.nan_to_num(group_traces[key])
        sem_trace  = np.nan_to_num(group_sems.get(key, np.zeros_like(mean_trace)))
        color      = GROUP_COLORS.get(key, GOLD)
        rgba_fill  = _hex_to_rgba(color, 0.18)

        # SEM upper
        fig.add_trace(go.Scatter(
            x=time_ms, y=mean_trace + 2 * sem_trace,
            mode="lines", line=dict(width=0), showlegend=False,
        ), row=row_idx, col=1)
        # SEM lower fill
        fig.add_trace(go.Scatter(
            x=time_ms, y=mean_trace - 2 * sem_trace,
            fill="tonexty", mode="lines",
            line=dict(width=0), fillcolor=rgba_fill, showlegend=False,
        ), row=row_idx, col=1)
        # Mean trace
        fig.add_trace(go.Scatter(
            x=time_ms, y=mean_trace, mode="lines",
            line=dict(color=color, width=2.0),
            name=GROUP_LABELS.get(key, key), showlegend=True,
        ), row=row_idx, col=1)

        # Zero reference
        fig.add_hline(y=0, line_dash="dot", line_color=GRAY,
                      line_width=0.8, row=row_idx, col=1)
        fig.update_yaxes(title_text="Δ spikes/s", row=row_idx, col=1)

        # Event patches
        _add_sequence_patches(fig, omission_cond=omission_cond,
                              row=row_idx, col=1, x_range=(-1000, 1500))

    fig.update_xaxes(title_text="Time (ms)", range=[-1000, 1500], row=n_groups, col=1)
    fig.update_layout(height=280 * n_groups, width=750)
    return _apply_style(fig, title)


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 7 (Poster 02 Section 5)
# plot_omission_fraction_bars
# ─────────────────────────────────────────────────────────────────────────────

def plot_omission_fraction_bars(
    fractions: Dict[str, Dict[str, float]],
    areas: List[str] = AREA_ORDER,
    title: str = "Fraction of Omission-Selective Neurons per Area",
) -> go.Figure:
    """
    Poster 02 Section 5 — Grouped bar chart (one group per neuron classification),
    bars per brain area. Shows that omission-selective neurons (N~20) are concentrated
    in higher-order areas (FEF, PFC).

    Parameters
    ----------
    fractions : dict {group_label: {area: float}}
        Fraction of neurons in each group per area (value in [0, 1]).
        Keys should match: 'stim_excited', 'stim_inhibited', 'omission_selective'.
    areas : list — x-axis order.
    title : str

    Returns
    -------
    go.Figure — grouped bar chart

    Example
    -------
    >>> fractions = {
    ...     'stim_excited':     {a: n_excited[a] / n_total[a] for a in AREA_ORDER},
    ...     'stim_inhibited':   {a: n_inhib[a]   / n_total[a] for a in AREA_ORDER},
    ...     'omission_selective': {a: n_omit[a]  / n_total[a] for a in AREA_ORDER},
    ... }
    >>> fig = plot_omission_fraction_bars(fractions)
    """
    GROUP_COLORS = {
        "stim_excited":      GOLD,
        "stim_inhibited":    VIOLET,
        "omission_selective": PINK,
    }
    GROUP_LABELS = {
        "stim_excited":      "Excited by stimulus",
        "stim_inhibited":    "Inhibited by stimulus",
        "omission_selective": "Omission-selective",
    }

    x_areas = [a for a in areas if any(a in d for d in fractions.values())]
    fig = go.Figure()

    for group_key, area_dict in fractions.items():
        y_vals = [area_dict.get(a, 0.0) * 100 for a in x_areas]  # convert to %
        color  = GROUP_COLORS.get(group_key, GRAY)
        fig.add_trace(go.Bar(
            name=GROUP_LABELS.get(group_key, group_key),
            x=x_areas,
            y=y_vals,
            marker_color=color,
            marker_line_color=BLACK,
            marker_line_width=0.8,
            text=[f"{v:.1f}%" for v in y_vals],
            textposition="outside",
            textfont=dict(size=8),
        ))

    fig.update_layout(
        barmode="group",
        xaxis_title="Brain Area",
        yaxis_title="% of neurons",
        height=420, width=700,
        legend=dict(orientation="h", y=-0.2),
    )
    return _apply_style(fig, title)


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 8 (Poster 02 Section 6)
# plot_spectral_harmony_matrices
# ─────────────────────────────────────────────────────────────────────────────

def plot_spectral_harmony_matrices(
    corr_by_band_stim: Dict[str, np.ndarray],
    corr_by_band_omit: Dict[str, np.ndarray],
    areas: List[str] = AREA_ORDER,
    bands: Optional[List[str]] = None,
    title: str = "Spectral Harmony: Inter-area LFP Correlation per Band",
) -> go.Figure:
    """
    Poster 02 Section 6 — 2×4 grid of 11×11 inter-area LFP correlation heatmaps.
    Top row: stimulus window. Bottom row: omission window.
    Columns: Theta, Alpha, Beta, Gamma.

    Key finding: Beta correlations INCREASE during omission; Gamma correlations DECREASE.
    This is the "spectral harmony flip" — gamma → beta dominant network.

    Parameters
    ----------
    corr_by_band_stim : dict {band: ndarray(n_areas, n_areas)}
        Inter-area LFP power correlations during the STIMULUS window.
    corr_by_band_omit : dict {band: ndarray(n_areas, n_areas)}
        Same for the OMISSION window.
    areas : list of str — axis labels.
    bands : list of str — bands to plot (default: Theta, Alpha, Beta, Gamma).
    title : str

    Returns
    -------
    go.Figure — 2 rows × 4 columns subplot grid

    How to compute input matrices
    ------------------------------
    For each band, extract per-trial mean power in a time window per area,
    then compute across-trial Pearson correlation across areas:
    >>> power_in_window = {}  # {area: array(n_trials)}
    >>> for area in areas:
    ...     pwr = get_band_power(freqs, tfr_epochs[area], band=band_range)
    ...     power_in_window[area] = pwr[:, (t >= 0) & (t < 531)].mean(1)
    >>> corr_stim = np.corrcoef(np.stack([power_in_window[a] for a in areas]))
    """
    if bands is None:
        bands = ["Theta", "Alpha", "Beta", "Gamma"]

    n_bands = len(bands)
    fig = make_subplots(
        rows=2, cols=n_bands,
        subplot_titles=(
            [f"Stimulus — {b}" for b in bands] +
            [f"Omission — {b}" for b in bands]
        ),
        horizontal_spacing=0.04,
        vertical_spacing=0.12,
    )

    BAND_CMAPS = {
        "Theta": "Blues",
        "Alpha": "Oranges",
        "Beta":  "Purples",
        "Gamma": "YlOrBr",
    }

    for col_idx, band in enumerate(bands, start=1):
        for row_idx, (corr, label) in enumerate(
            [(corr_by_band_stim.get(band), "Stim"),
             (corr_by_band_omit.get(band), "Omit")],
            start=1
        ):
            if corr is None:
                continue
            cmap = BAND_CMAPS.get(band, "Viridis")
            corr_display = np.array(corr, dtype=float)
            np.fill_diagonal(corr_display, np.nan)

            show_cbar = (col_idx == n_bands)
            fig.add_trace(go.Heatmap(
                z=corr_display,
                x=areas, y=areas,
                colorscale=cmap,
                zmin=-1, zmax=1,
                showscale=show_cbar,
                colorbar=dict(title="r", len=0.4, y=0.75 if row_idx == 1 else 0.25,
                              thickness=10) if show_cbar else None,
                xgap=0.5, ygap=0.5,
            ), row=row_idx, col=col_idx)

            fig.update_xaxes(tickfont=dict(size=7), row=row_idx, col=col_idx)
            fig.update_yaxes(tickfont=dict(size=7), autorange="reversed",
                             row=row_idx, col=col_idx)

    fig.update_layout(height=650, width=300 * n_bands)
    return _apply_style(fig, title)


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 9 (Poster 02 Section 6)
# plot_beta_gamma_shift_bars
# ─────────────────────────────────────────────────────────────────────────────

def plot_beta_gamma_shift_bars(
    beta_corr: Dict[str, float],
    gamma_corr: Dict[str, float],
    conditions: Optional[List[str]] = None,
    areas: List[str] = AREA_ORDER,
    title: str = "Beta vs Gamma Network Strength: Stimulus vs Omission",
) -> go.Figure:
    """
    Poster 02 Section 6 — Side-by-side bar chart showing that:
    - During STIMULUS: gamma inter-area correlation >> beta
    - During OMISSION: beta inter-area correlation >> gamma
    This is the "spectral harmony shift" summary figure.

    Parameters
    ----------
    beta_corr : dict {window_or_condition: float}
        Mean inter-area beta-band correlation for each window.
        Keys: e.g. 'Stimulus', 'Omission' — or per-condition strings.
    gamma_corr : dict {window_or_condition: float}
        Same for gamma band.
    conditions : list — controls x-axis category order.
        Default: sorted(beta_corr.keys()).
    areas : list — (unused here, for reference only; values are area-averaged).
    title : str

    Returns
    -------
    go.Figure — grouped bar chart

    Example
    -------
    >>> # Compute mean off-diagonal correlation per band per window
    >>> mask = ~np.eye(n_areas, dtype=bool)
    >>> beta_corr = {
    ...     'Stimulus': float(np.mean(np.abs(corr_stim_beta[mask]))),
    ...     'Omission': float(np.mean(np.abs(corr_omit_beta[mask]))),
    ... }
    >>> gamma_corr = {
    ...     'Stimulus': float(np.mean(np.abs(corr_stim_gamma[mask]))),
    ...     'Omission': float(np.mean(np.abs(corr_omit_gamma[mask]))),
    ... }
    >>> fig = plot_beta_gamma_shift_bars(beta_corr, gamma_corr)
    """
    if conditions is None:
        conditions = sorted(beta_corr.keys())

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Beta network",
        x=conditions,
        y=[beta_corr.get(c, 0) for c in conditions],
        marker_color=VIOLET,
        marker_line_color=BLACK, marker_line_width=1.0,
        text=[f"{beta_corr.get(c, 0):.3f}" for c in conditions],
        textposition="outside", textfont=dict(size=10),
    ))
    fig.add_trace(go.Bar(
        name="Gamma network",
        x=conditions,
        y=[gamma_corr.get(c, 0) for c in conditions],
        marker_color=GOLD,
        marker_line_color=BLACK, marker_line_width=1.0,
        text=[f"{gamma_corr.get(c, 0):.3f}" for c in conditions],
        textposition="outside", textfont=dict(size=10),
    ))

    fig.update_layout(
        barmode="group",
        xaxis_title="Window",
        yaxis_title="Mean |Pearson r|",
        height=420, width=480,
        legend=dict(orientation="h", y=-0.2),
    )
    return _apply_style(fig, title)


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 10 (Poster 01 Section 6 — gamma-beta dissociation)
# plot_gamma_beta_dissociation
# ─────────────────────────────────────────────────────────────────────────────

def plot_gamma_beta_dissociation(
    gamma_corr_matrix: np.ndarray,
    beta_corr_matrix: np.ndarray,
    areas: List[str] = AREA_ORDER,
    title: str = "Gamma–Beta Dissociation during Omission Context",
) -> go.Figure:
    """
    Poster 01 Section 6 — Two-panel figure showing that gamma and beta networks
    are DISSOCIATED during omission: gamma correlation drops while beta rises.
    Shows the 2×2 contrasting heatmaps next to each other with a shared colorscale.

    Parameters
    ----------
    gamma_corr_matrix : ndarray (n_areas, n_areas) — gamma-band inter-area corr.
    beta_corr_matrix  : ndarray (n_areas, n_areas) — beta-band inter-area corr.
    areas : list of str — axis labels.
    title : str

    Returns
    -------
    go.Figure — 1 row × 2 subplot
    """
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["<b>Gamma correlation</b>", "<b>Beta correlation</b>"],
        horizontal_spacing=0.10,
    )

    pairs = [(gamma_corr_matrix, BAND_COLORS["Gamma"], 1),
             (beta_corr_matrix,  BAND_COLORS["Beta"],  2)]

    for corr, color, col_idx in pairs:
        corr_display = np.array(corr, dtype=float)
        np.fill_diagonal(corr_display, np.nan)
        # Custom colorscale: white → band color
        r, g, b = (int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        cscale = [[0.0, "white"],
                  [1.0, f"rgb({r},{g},{b})"]]
        fig.add_trace(go.Heatmap(
            z=corr_display, x=areas, y=areas,
            colorscale=cscale, zmin=0, zmax=1,
            showscale=(col_idx == 2),
            colorbar=dict(title="|r|", len=0.6),
            xgap=1, ygap=1,
        ), row=1, col=col_idx)
        fig.update_yaxes(autorange="reversed", tickfont=dict(size=8),
                         row=1, col=col_idx)
        fig.update_xaxes(tickfont=dict(size=8), row=1, col=col_idx)

    fig.update_layout(height=460, width=820)
    return _apply_style(fig, title)
