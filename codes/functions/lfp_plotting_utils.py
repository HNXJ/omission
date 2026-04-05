"""
lfp_plotting_utils.py
Utilities for generating Plotly figures according to OMISSION 2026 GAMMA plan rules.
Includes functions for TFR heatmaps, band power summaries, and general plot styling.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from typing import Dict, Tuple, List, Optional, Any

from codes.functions.lfp_constants import (
    GOLD, BLACK, VIOLET, PINK, TEAL, ORANGE, GRAY, WHITE, SLATE,
    TIMING_MS, SEQUENCE_TIMING, ALL_CONDITIONS, BANDS,
    OMISSION_PATCHES, TARGET_AREAS # New imports
)


def _get_time_axis_labels(time_ms: np.ndarray) -> np.ndarray:
    """Generates time axis labels aligning with p1 onset = 0ms."""
    # This is a simplified example; actual NWB time metadata might be more complex.
    # Assuming time_ms is relative to p1 onset.
    return time_ms

def _save_figure(fig: go.Figure, output_dir: Path, filename_prefix: str) -> None:
    """Saves Plotly figure in HTML and SVG formats."""
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.write_html(output_dir / f"{filename_prefix}.html")
    fig.write_image(output_dir / f"{filename_prefix}.svg")
    print(f"  Saved {filename_prefix}.html/.svg to {output_dir}")

def smooth_fr(data: np.ndarray, window_size: int = 50) -> np.ndarray:
    """
    Smooths firing rate data using a simple moving average.

    Parameters
    ----------
    data : np.ndarray
        Input firing rate data (1D array).
    window_size : int, optional
        Size of the smoothing window in data points, by default 50.

    Returns
    -------
    np.ndarray
        Smoothed firing rate data.
    """
    if len(data) < window_size:
        return data # Cannot smooth if data is smaller than window
    kernel = np.ones(window_size) / window_size
    return np.convolve(data, kernel, mode='same')

def create_tfr_figure_per_condition(
    session_id: str,
    area: str,
    condition: str,
    tfr_data: np.ndarray, # (freqs, times)
    freqs: np.ndarray,
    times: np.ndarray,
    output_dir: Path,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Generates and saves a TFR heatmap figure for a specific area and condition.
    Aligned with GAMMA plan Figure 05 style.

    Parameters
    ----------
    session_id : str
        Current session ID.
    area : str
        Brain area for the plot.
    condition : str
        Experimental condition for the plot.
    tfr_data : np.ndarray
        Time-frequency representation data (freqs, times).
    freqs : np.ndarray
        Array of frequencies.
    times : np.ndarray
        Array of time points.
    output_dir : Path
        Directory to save the figure.
    metadata : Optional[Dict[str, Any]]
        Additional metadata to include in the plot title/caption.
    """
    fig = go.Figure(data=go.Heatmap(
        z=tfr_data,
        x=times,
        y=freqs,
        colorscale='Jet', # Or another appropriate colormap
        zmin=-3, zmax=3, # Example dB range, adjust as needed
        colorbar=dict(title="Power (dB)", thickness=20)
    ))

    # Add omission patches
    for pres_key, pres_timing in SEQUENCE_TIMING.items():
        # This condition check is specific to "omission" events (RXRR, RRXR, RRRX)
        # For full TFR, we might want to highlight all relevant presentation timings.
        if pres_key in condition and 'X' in condition: # Example: RXRR and pres_key=='RXRR'
            start_ms = TIMING_MS.get(pres_key, np.nan)
            end_ms = SEQUENCE_TIMING[pres_key]['end'] if pres_key in SEQUENCE_TIMING else np.nan
            
            if not np.isnan(start_ms) and not np.isnan(end_ms):
                 fig.add_vrect(
                    x0=start_ms, x1=end_ms,
                    fillcolor=PINK, opacity=0.3, layer="below", line_width=0
                )
    
    # Add vertical lines for presentation timings
    for pres_key, start_time in TIMING_MS.items():
        fig.add_vline(x=start_time, line_width=1, line_dash="dash", line_color=GRAY,
                      annotation_text=pres_key, annotation_position="top left",
                      annotation_font_size=10, annotation_font_color=GRAY)

    fig.update_layout(
        title=f"<b>TFR: Session {session_id}, Area {area}, Condition {condition}</b>",
        xaxis_title="Time (ms)",
        yaxis_title="Frequency (Hz)",
        template="plotly_white",
        font=dict(family="Arial", size=12, color=BLACK),
        plot_bgcolor=WHITE,
        paper_bgcolor=WHITE,
        xaxis_range=[times.min(), times.max()],
        yaxis_range=[freqs.min(), freqs.max()]
    )

    # Naming convention: [condition]_[sequence]_[analysis]
    # Here, sequence is implicitly 'full' or 'windowed', analysis is 'tfr'
    filename_prefix = f"{condition}_full_tfr_{area}_{session_id}"
    _save_figure(fig, output_dir, filename_prefix)


def create_band_summary_figure(
    data_to_plot: Dict[str, Dict[str, Dict[str, np.ndarray]]], # {area: {band: {'mean': array, 'sem': array}}}
    session_id: str,
    times: np.ndarray,
    output_dir: Path,
    metadata: Optional[Dict[str, Any]] = None,
    # Additional parameters for Figure 06 specifics: merging omission, sorted ranking etc.
) -> None:
    """
    Generates and saves a band power summary figure with mean +/- SEM.
    Aligned with GAMMA plan Figure 06 style.

    Parameters
    ----------
    data_to_plot : Dict[str, Dict[str, Dict[str, np.ndarray]]]
        Nested dictionary with power data.
        {area: {band_name: {'mean': np.ndarray, 'sem': np.ndarray}}}
        The 'mean' and 'sem' arrays should have the same length as 'times'.
    session_id : str
        Current session ID.
    times : np.ndarray
        Array of time points (x-axis for plotting).
    output_dir : Path
        Directory to save the figure.
    metadata : Optional[Dict[str, Any]]
        Additional metadata.
    """
    bands_to_plot = list(BANDS.keys())
    areas_to_plot = sorted(data_to_plot.keys()) # Ensure consistent ordering for colors

    fig = make_subplots(rows=len(bands_to_plot), cols=1,
                        shared_xaxes=True, vertical_spacing=0.08,
                        subplot_titles=[f"{b} Band Power" for b in bands_to_plot])
    
    area_colors = {
        'V1': GOLD, 'V2': GOLD, # Low
        'V4': VIOLET, 'MT': VIOLET, # Mid
        'FEF': TEAL, 'PFC': TEAL # High
    }

    for i, band_name in enumerate(bands_to_plot):
        for area_idx, area in enumerate(areas_to_plot):
            if band_name in data_to_plot[area]:
                mean_trace = data_to_plot[area][band_name].get('mean')
                sem_trace = data_to_plot[area][band_name].get('sem')
                
                if mean_trace is None or sem_trace is None or mean_trace.size == 0:
                    continue
                
                # Filter out NaNs to prevent plotting issues for error bands
                valid_indices = ~np.isnan(mean_trace) & ~np.isnan(sem_trace)
                if not np.any(valid_indices): continue

                times_valid = times[valid_indices]
                mean_trace_valid = mean_trace[valid_indices]
                sem_trace_valid = sem_trace[valid_indices]
                
                upper_bound = mean_trace_valid + sem_trace_valid
                lower_bound = mean_trace_valid - sem_trace_valid

                color = area_colors.get(area, GRAY) # Default to GRAY if area not in dict

                # Plot shaded SEM region
                fig.add_trace(go.Scatter(
                    x=np.concatenate([times_valid, times_valid[::-1]]),
                    y=np.concatenate([upper_bound, lower_bound[::-1]]),
                    fill='toself',
                    fillcolor=color.replace(')', ', 0.2)').replace('rgb', 'rgba'), # 20% opacity
                    line=dict(width=0),
                    hoverinfo='skip',
                    showlegend=False,
                    name=f'{area} {band_name} SEM'
                ), row=i+1, col=1)

                # Plot mean line
                fig.add_trace(go.Scatter(
                    x=times_valid,
                    y=mean_trace_valid,
                    mode='lines',
                    line=dict(color=color, width=2),
                    name=f'{area} {band_name} Mean',
                    showlegend=True if i == 0 else False # Show legend only for the first subplot
                ), row=i+1, col=1)

        # Add vertical lines for presentation timings
        for pres_key, start_time in TIMING_MS.items():
            fig.add_vline(x=start_time, line_width=1, line_dash="dash", line_color=GRAY,
                        annotation_text=pres_key, annotation_position="top left",
                        annotation_font_size=10, annotation_font_color=GRAY, row=i+1, col=1)

    fig.update_layout(
        title=f"<b>Band Power Summary: Session {session_id}</b>",
        xaxis_title="Time (ms)",
        yaxis_title="Normalized Power",
        template="plotly_white",
        font=dict(family="Arial", size=12, color=BLACK),
        plot_bgcolor=WHITE,
        paper_bgcolor=WHITE,
        height=len(bands_to_plot) * 300,
        showlegend=True
    )
    
    filename_prefix = f"ALL_band_summary_{session_id}" # Simplified for now
    _save_figure(fig, output_dir, filename_prefix)


def create_population_firing_figure(
    session_id: str,
    data_to_plot: Dict[str, Dict[str, Dict[str, Any]]], # {area: {unit_id: {'firing_rate_ts': array, 'time_bins_ms': array}}}
    condition: str,
    output_dir: Path,
    smooth_window_size: int = 50,
    sem_multiplier: int = 2,
    window_ms: Tuple[int, int] = (-500, 4000), # New parameter for x-axis range
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Generates and saves a population firing rate figure for a specific session and condition.
    Aligned with GAMMA plan Figure 03 style.

    Parameters
    ----------
    session_id : str
        Current session ID.
    data_to_plot : Dict[str, Dict[str, Dict[str, Any]]]
        Nested dictionary with firing rate data.
        {area: {layer: {unit_id: {'firing_rate_ts': np.ndarray, 'time_bins_ms': np.ndarray}}}}
        'firing_rate_ts' is the trial-averaged firing rate time series for a unit.
        'time_bins_ms' is the corresponding time axis.
    condition : str
        Experimental condition for the plot.
    output_dir : Path
        Directory to save the figure.
    smooth_window_size : int, optional
        Window size for smoothing firing rate, by default 50.
    sem_multiplier : int, optional
        Multiplier for SEM band (e.g., 1 for 1 SEM, 2 for 2 SEM), by default 2.
    metadata : Optional[Dict[str, Any]]
        Additional metadata to include in the plot title/caption.
    """
    
    # Filter for areas that actually have data for this condition
    active_areas_for_condition = [
        area for area in TARGET_AREAS # Use TARGET_AREAS for consistent order and filtering
        if area in data_to_plot and any(
            unit_data_dict.get(condition, {}).get('firing_rate_ts', np.array([])).size > 0
            for unit_layer_dict in data_to_plot[area].values()
            for unit_data_dict in unit_layer_dict.values() # Iterate through layers
        )
    ]

    if not active_areas_for_condition:
        print(f"No valid unit data found for Figure 03, session {session_id}, condition {condition}. Skipping.")
        return

    n_areas = len(active_areas_for_condition)
    fig = make_subplots(rows=n_areas, cols=1,
                        subplot_titles=active_areas_for_condition,
                        shared_xaxes=True, vertical_spacing=0.03)

    total_units_in_plot = 0
    time_bins_ms = np.array([]) # Will be populated from the first unit's data

    for i, area in enumerate(active_areas_for_condition):
        all_unit_frs_in_area: List[np.ndarray] = []
        
        # Collect firing rates for all units in this area (across all layers)
        for unit_layer_dict in data_to_plot[area].values(): # Iterate through layers in this area
            for unit_id, unit_data_by_cond in unit_layer_dict.items(): # Iterate through units in this layer
                if condition in unit_data_by_cond:
                    fr_ts = unit_data_by_cond[condition].get('firing_rate_ts', np.array([]))
                    unit_times = unit_data_by_cond[condition].get('time_bins_ms', np.array([]))

                    if fr_ts.size > 0:
                        all_unit_frs_in_area.append(fr_ts)
                        if time_bins_ms.size == 0: # Get time axis from first valid unit
                            time_bins_ms = unit_times
        
        if not all_unit_frs_in_area:
            continue
            
        units_fr_array = np.vstack(all_unit_frs_in_area) # (n_units, n_timepoints)
        n_units_in_area = units_fr_array.shape[0]
        total_units_in_plot += n_units_in_area

        mean_fr = np.nanmean(units_fr_array, axis=0)
        sem_fr = np.nanstd(units_fr_array, axis=0) / np.sqrt(n_units_in_area) if n_units_in_area > 1 else np.full_like(mean_fr, np.nan)
        
        # Apply smoothing
        mean_fr_s = smooth_fr(mean_fr, smooth_window_size)
        sem_fr_s = smooth_fr(sem_fr, smooth_window_size) # Smooth SEM as well for consistent visual

        row_idx = i + 1
        
        # Plot +/- SEM Shading
        upper_bound = mean_fr_s + sem_multiplier * sem_fr_s
        lower_bound = mean_fr_s - sem_multiplier * sem_fr_s

        # Ensure bounds are not negative
        lower_bound[lower_bound < 0] = 0
        
        fig.add_trace(go.Scatter(
            x=np.concatenate([time_bins_ms, time_bins_ms[::-1]]),
            y=np.concatenate([upper_bound, lower_bound[::-1]]),
            fill='toself',
            fillcolor='rgba(128,128,128,0.3)', # Light gray shading
            line=dict(width=0),
            hoverinfo='skip',
            showlegend=False,
            name=f'{area} {condition} SEM'
        ), row=row_idx, col=1)

        # Plot Mean Firing Rate
        fig.add_trace(go.Scatter(
            x=time_bins_ms, y=mean_fr_s,
            mode='lines',
            line=dict(color=BLACK, width=2), # Black mean line
            name=f'{area} {condition} Mean',
            showlegend=True if i == 0 else False # Show legend only for the first subplot
        ), row=row_idx, col=1)
        
        # Add omission patch if applicable
        if condition in OMISSION_PATCHES:
            start_ms, end_ms = OMISSION_PATCHES[condition]
            fig.add_vrect(
                x0=start_ms, x1=end_ms,
                fillcolor=PINK, opacity=0.2, # Pink omission patch
                layer="below", line_width=0,
                row=row_idx, col=1
            )
            
        # Add vertical lines for event timings (only if time_bins_ms is not empty)
        if time_bins_ms.size > 0:
            for pres_key, start_time in TIMING_MS.items():
                if time_bins_ms.min() <= start_time <= time_bins_ms.max():
                    fig.add_vline(x=start_time, line_width=1, line_dash="dash", line_color=GRAY,
                                annotation_text=pres_key, annotation_position="top left",
                                annotation_font_size=10, annotation_font_color=GRAY,
                                row=row_idx, col=1)

    fig.update_layout(
        title=f"<b>Fig 03: Population Firing Rate (Session {session_id}, Condition {condition})</b><br><sup>N = {total_units_in_plot} units | Mean ± {sem_multiplier}SEM | Template: White</sup>",
        height=max(600, 250 * n_areas), # Adjust height dynamically
        template="plotly_white",
        font=dict(family="Arial", size=12, color=BLACK),
        plot_bgcolor=WHITE,
        paper_bgcolor=WHITE,
        showlegend=True # Show legend at the top
    )
    
    # Update axes
    fig.update_xaxes(title_text="Time [ms]", row=n_areas, col=1)
    for i, area_name in enumerate(active_areas_for_condition):
        fig.update_yaxes(title_text="Firing Rate [Hz]", row=i+1, col=1)
        fig.update_xaxes(range=[window_ms[0], window_ms[1]], row=i+1, col=1)

    filename_prefix = f"{condition}_population_firing_rate_{session_id}"
    _save_figure(fig, output_dir, filename_prefix)
