"""
lfp_laminar_mapping.py: Spectrolaminar mapping based on vFLIP2 logic.
Finds the Layer 4 crossover point by comparing Alpha/Beta and Gamma power profiles.
"""
from __future__ import annotations
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import welch
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List
import pandas as pd # Import pandas

# Configuration (constants for the module)
FS = 1000.0
BANDS_VFLIP2 = {
    'alpha_beta': (8, 30),
    'gamma': (35, 80)
}
CHANNEL_SPACING = 0.04  # 40um, used for plotting/depth conversion (in mm)

def compute_spectrolaminar_profiles(lfp_data_probe: np.ndarray, fs: float = FS) -> Dict[str, np.ndarray]:
    """
    Computes depth-resolved power profiles for Alpha/Beta and Gamma.
    
    Parameters
    ----------
    lfp_data_probe : np.ndarray
        LFP data for a single probe in (Trials, Channels, Samples) format.
    fs : float
        Sampling frequency.

    Returns
    -------
    Dict[str, np.ndarray]
        Dictionary with power profiles for 'alpha_beta' and 'gamma' bands.
        Each profile is a 1D array of shape (n_chans,).
    """
    if lfp_data_probe.ndim != 3:
        raise ValueError("lfp_data_probe must be a 3D array (Trials, Channels, Samples)")

    # Use samples 1000-6000 as per user instruction for analysis window
    data = lfp_data_probe[:, :, 1000:6000]
    n_trials, n_chans, n_samples = data.shape
    
    psd_profiles = {band: np.zeros(n_chans) for band in BANDS_VFLIP2}
    
    # Process channel by channel for memory efficiency and clarity
    for ch in range(n_chans):
        ch_data = data[:, ch, :] # (Trials, Samples)
        if ch_data.shape[0] == 0: # Handle empty trials
             for band_name in BANDS_VFLIP2:
                psd_profiles[band_name][ch] = np.nan
             continue

        # Compute Welch's PSD for each trial, then average
        f, pxx_trials = welch(ch_data, fs=fs, nperseg=512, axis=-1)
        mean_pxx = np.nanmean(pxx_trials, axis=0) # Average PSD across trials
        
        # Integrate power in bands
        for band_name, (f_min, f_max) in BANDS_VFLIP2.items():
            mask = (f >= f_min) & (f <= f_max)
            if np.sum(mask) == 0: # Handle cases where band is outside frequency range
                psd_profiles[band_name][ch] = np.nan
            else:
                psd_profiles[band_name][ch] = np.nanmean(mean_pxx[mask])
            
    # Spatial smoothing across electrodes
    for band_name in psd_profiles:
        # Only apply smoothing if there are non-nan values
        if not np.all(np.isnan(psd_profiles[band_name])):
            # Handle nans during smoothing: temporarily replace, smooth, then restore
            nan_mask = np.isnan(psd_profiles[band_name])
            smoothed_profile = gaussian_filter1d(np.nan_to_num(psd_profiles[band_name]), sigma=2.0)
            psd_profiles[band_name][~nan_mask] = smoothed_profile[~nan_mask]
            # If all were nan, they remain nan

    return psd_profiles


def find_crossover(profiles: Dict[str, np.ndarray]) -> Tuple[float, np.ndarray, np.ndarray]:
    """
    Finds the crossover point where Gamma power begins to dominate Alpha/Beta.
    
    Parameters
    ----------
    profiles : Dict[str, np.ndarray]
        Power profiles for 'alpha_beta' and 'gamma' bands.

    Returns
    -------
    Tuple[float, np.ndarray, np.ndarray]
        - crossover_idx: Interpolated channel index of the crossover.
        - ab_norm: Normalized Alpha/Beta profile.
        - ga_norm: Normalized Gamma profile.
    """
    ab = profiles['alpha_beta']
    ga = profiles['gamma']
    
    # Handle cases where profiles might be all NaNs or empty
    if np.all(np.isnan(ab)) or np.all(np.isnan(ga)) or ab.size == 0 or ga.size == 0:
        return np.nan, ab, ga # Return NaNs for crossover, original profiles
    
    # Normalize both to their max to handle different power scales
    # Add a small epsilon to avoid division by zero if all values are zero
    ab_norm = ab / (np.nanmax(ab) + 1e-12)
    ga_norm = ga / (np.nanmax(ga) + 1e-12)
    
    # Find the intersection (Gamma - Alpha/Beta)
    diff = ga_norm - ab_norm
    
    crossover_idx = np.nan
    # We look for a zero-crossing from positive to negative as we go from top to bottom
    # (Gamma > Alpha/Beta then Alpha/Beta > Gamma)
    for i in range(len(diff) - 1):
        if diff[i] > 0 and diff[i+1] < 0:
            # Interpolate for a more precise crossover point
            crossover_idx = i + (0 - diff[i]) / (diff[i+1] - diff[i])
            break
            
    return crossover_idx, ab_norm, ga_norm


def get_laminar_crossover(
    lfp_data_probe: np.ndarray,
    fs: float = FS,
    output_dir: Optional[Path] = None,
    session_id: Optional[str] = None,
    probe_id: Optional[str] = None,
) -> float:
    """
    Performs spectrolaminar mapping for a single probe and returns the L4 crossover index.
    Optionally saves a diagnostic plot.

    Parameters
    ----------
    lfp_data_probe : np.ndarray
        LFP data for a single probe in (Trials, Channels, Samples) format.
    fs : float
        Sampling frequency.
    output_dir : Optional[Path]
        Directory to save diagnostic plots. If None, no plot is saved.
    session_id : Optional[str]
        Session ID for plot filename.
    probe_id : Optional[str]
        Probe ID for plot filename.

    Returns
    -------
    float
        The interpolated channel index corresponding to the L4 crossover.
        Returns np.nan if crossover cannot be determined.
    """
    if lfp_data_probe.size == 0 or lfp_data_probe.shape[1] < 2: # Need at least 2 channels for bipolar ref/crossover
        warnings.warn("LFP data for probe is empty or has too few channels for laminar mapping. Returning NaN.", RuntimeWarning)
        return np.nan

    profiles = compute_spectrolaminar_profiles(lfp_data_probe, fs=fs)
    crossover, ab_norm, ga_norm = find_crossover(profiles)

    # Optional Plotting for validation
    if output_dir and session_id and probe_id and not np.isnan(crossover):
        import matplotlib.pyplot as plt
        output_dir.mkdir(parents=True, exist_ok=True)
        
        plt.figure(figsize=(6, 10))
        chans = np.arange(len(ab_norm))
        plt.plot(ab_norm, chans, 'b', label='Alpha/Beta (8-30Hz)')
        plt.plot(ga_norm, chans, 'r', label='Gamma (35-80Hz)')
        plt.axhline(crossover, color='k', linestyle='--', label=f'Crossover (ch={crossover:.1f})')
        plt.gca().invert_yaxis() # Assuming channel 0 is superficial
        plt.title(f"vFLIP2 Mapping: Ses {session_id} Probe {probe_id}")
        plt.xlabel("Normalized Power")
        plt.ylabel(f"Channel Number (Spacing: {CHANNEL_SPACING*1000} um)")
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plot_path = output_dir / f"vflip2_ses{session_id}_probe{probe_id}.png"
        plt.savefig(plot_path)
        plt.close()
        
    return crossover


def map_channels_to_layers(
    electrode_df_probe: pd.DataFrame, # Changed to electrode_df_probe
    crossover_idx: float,
    channel_spacing_mm: float = CHANNEL_SPACING,
) -> pd.DataFrame:
    """
    Assigns a cortical layer to each channel in the electrode_df_probe based on the
    crossover index (L4 boundary).

    Parameters
    ----------
    electrode_df_probe : pd.DataFrame
        DataFrame containing electrode information for a SINGLE PROBE.
        Must include a 'depth' column (in mm).
        The index should be the channel_id.
    crossover_idx : float
        The interpolated channel index identified as the L4 crossover.
        This is an index relative to the *sorted* channels of this probe.
    channel_spacing_mm : float
        The physical spacing between channels in mm.

    Returns
    -------
    pd.DataFrame
        The input electrode_df_probe with an added 'layer' column.
    """
    if 'depth' not in electrode_df_probe.columns:
        raise ValueError("electrode_df_probe must contain a 'depth' column for layer mapping.")
    
    if np.isnan(crossover_idx):
        electrode_df_probe['layer'] = 'Unknown'
        return electrode_df_probe

    # Ensure the DataFrame is sorted by depth (deepest is usually highest depth value)
    # This aligns the channel indices with physical depth progression
    sorted_df = electrode_df_probe.sort_values(by='depth', ascending=True).copy() # Superficial to deep

    # Calculate the depth corresponding to the crossover_idx
    # The crossover_idx is an interpolated channel index.
    # Assuming channels are uniformly spaced and sorted by depth.
    # depth at crossover = depth of first channel + crossover_idx * channel_spacing
    
    # Get the depth of the first channel in the sorted list
    if not sorted_df.empty:
        # Assuming sorted_df.index.tolist() gives original channel IDs in sorted order
        # And depth corresponds to these original channel IDs.
        
        # Calculate depths relative to the first channel in the sorted array
        # This implicitly assumes the first channel in the sorted_df is the most superficial.
        # This logic needs to be robust, using actual depth values from the DataFrame
        
        # Let's directly calculate a 'relative_channel_idx' for each channel in the sorted_df
        # This maps the channels back to 0, 1, 2... for easy comparison with crossover_idx
        relative_channel_indices = pd.Series(
            data=np.arange(len(sorted_df)),
            index=sorted_df.index
        )
        
        # Now apply the layer logic based on relative_channel_indices
        crossover_depth_relative_idx = crossover_idx
        
        # Heuristic for layer boundaries based on relative channel index
        # These are rough estimates and might need refinement based on biological data.
        # These values represent *offsets* from the crossover_depth_relative_idx
        # For example, L4_start is 1 channel *superficial* to crossover_idx
        # L4_end is 1 channel *deep* to crossover_idx
        # L2/3: channels with relative_channel_idx < L4_start
        # L4: channels with L4_start <= relative_channel_idx < L4_end
        # L5: channels with L4_end <= relative_channel_idx < L5_end
        # L6: channels with relative_channel_idx >= L5_end
        
        # Example offsets (can be adjusted)
        L4_upper_offset_channels = -1 # channels at crossover_idx - 1 are still L4
        L4_lower_offset_channels = 1  # channels at crossover_idx + 1 are still L4
        L5_lower_offset_channels = 4  # channels at crossover_idx + 4 are L5/L6 boundary
        
        for ch_id in sorted_df.index:
            rel_idx = relative_channel_indices.loc[ch_id]
            
            if rel_idx < crossover_depth_relative_idx + L4_upper_offset_channels:
                sorted_df.loc[ch_id, 'layer'] = 'L2/3'
            elif rel_idx < crossover_depth_relative_idx + L4_lower_offset_channels:
                sorted_df.loc[ch_id, 'layer'] = 'L4'
            elif rel_idx < crossover_depth_relative_idx + L5_lower_offset_channels:
                sorted_df.loc[ch_id, 'layer'] = 'L5'
            else:
                sorted_df.loc[ch_id, 'layer'] = 'L6'
    else:
        # If sorted_df is empty, no layers can be assigned
        sorted_df['layer'] = 'Unknown'

    return sorted_df # Return the modified sorted_df for this probe