
import numpy as np
import pandas as pd
import glob
import os
import re
from pynwb import NWBHDF5IO
from collections import defaultdict
from scipy.ndimage import gaussian_filter1d

# Constants
AREA_ORDER = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']
HIERARCHY = {
    'Low': ['V1', 'V2'],
    'Mid': ['V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST'],
    'High': ['FEF', 'PFC']
}
CHANNELS_PER_PROBE = 128
AREA_MAPPING = {'DP': 'V4', 'V3': ['V3d', 'V3a']}
SAMPLING_RATE = 1000 # Hz

def get_unit_to_area_map(nwb_path):
    """Maps (probe_id, local_idx) to brain area using standardized rules."""
    unit_map = {}
    try:
        with NWBHDF5IO(nwb_path, 'r', load_namespaces=True) as io:
            nwbfile = io.read()
            units_df = nwbfile.units.to_dataframe()
            elec_df = nwbfile.electrodes.to_dataframe()
            probe_units = defaultdict(list)
            for idx, unit in units_df.iterrows():
                p_id = int(float(unit['peak_channel_id']))
                probe_id = p_id // CHANNELS_PER_PROBE
                probe_units[probe_id].append((idx, p_id))
            for probe_id, units in probe_units.items():
                units.sort(key=lambda x: x[0])
                for local_idx, (global_idx, p_id) in enumerate(units):
                    elec = elec_df.loc[p_id]
                    raw = elec.get('location', elec.get('label', 'unknown'))
                    if isinstance(raw, bytes): raw = raw.decode('utf-8')
                    clean = raw.replace('/', ',')
                    raw_areas = [a.strip() for a in clean.split(',')]
                    mapped = []
                    for a in raw_areas:
                        m = AREA_MAPPING.get(a, a)
                        if isinstance(m, list): mapped.extend(m)
                        else: mapped.append(m)
                    sw = CHANNELS_PER_PROBE / len(mapped)
                    area = mapped[min(int((p_id % CHANNELS_PER_PROBE) // sw), len(mapped)-1)]
                    if area in AREA_ORDER:
                        unit_map[(probe_id, local_idx)] = area
    except Exception as e:
        print(f"Warning: Failed to map units in {nwb_path}: {e}")
    return unit_map

def extract_unit_traces(session_id, conds=['RRRR', 'RXRR', 'RRXR', 'RRRX'], sigma=20):
    """Extracts smoothed firing rate and variance traces for all units in a session."""
    nwb_path = glob.glob(f'data/sub-*_ses-{session_id}_rec.nwb')[0]
    u_map = get_unit_to_area_map(nwb_path)
    
    session_traces = {}
    
    for cond in conds:
        spk_files = glob.glob(f'data/ses{session_id}-units-probe*-spk-{cond}.npy')
        for f in spk_files:
            probe_id = int(re.search(r'probe(\d+)', f).group(1))
            data = np.load(f, mmap_mode='r')
            for u_idx in range(data.shape[1]):
                area = u_map.get((probe_id, u_idx))
                if area:
                    unit_spks = data[:, u_idx, :] # (trials, time)
                    
                    # Smoothed FR trace (Hz)
                    fr_trace = np.mean(unit_spks, axis=0) * 1000
                    fr_smooth = gaussian_filter1d(fr_trace, sigma=sigma)
                    
                    # Variance trace
                    var_trace = np.var(unit_spks, axis=0, ddof=1)
                    var_smooth = gaussian_filter1d(var_trace, sigma=sigma)
                    
                    unit_key = (session_id, probe_id, u_idx)
                    if unit_key not in session_traces:
                        session_traces[unit_key] = {'area': area, 'traces': {}}
                    
                    session_traces[unit_key]['traces'][cond] = {
                        'fr': fr_smooth,
                        'var': var_smooth
                    }
                    
    return session_traces

def classify_unit_types(nwb_path: Path):
    """
    Classify units as putative Excitatory (E) or Inhibitory (I) based on waveform duration.
    Assumes standard NWB unit columns: 'peak_to_trough', 'firing_rate'.
    """
    with NWBHDF5IO(nwb_path, 'r', load_namespaces=True) as io:
        nwb = io.read()
        units_df = nwb.units.to_dataframe()
    
    # Simple classification rule (duration threshold 0.4ms)
    # This threshold is project-specific; referencing canon as a policy
    is_inhibitory = units_df['peak_to_trough'] < 0.4
    units_df['putative_type'] = np.where(is_inhibitory, 'I', 'E')
    
    return units_df[['putative_type', 'peak_to_trough', 'firing_rate']]

def compute_area_mmff(all_unit_stats, areas=AREA_ORDER, conds=['RRRR', 'RXRR', 'RRXR', 'RRRX'], win_size=150, step=5):
    """
    Computes Mean-Matched Fano Factor across areas and conditions.
    all_unit_stats: dict mapping (session, probe, unit) -> { 'area': str, 'traces': { cond: { 'fr': [], 'var': [] } } }
    """
    time_bins = np.arange(0, 6000 - win_size, step)
    area_mmff = {area: {cond: [] for cond in conds} for area in areas}
    
    for area in areas:
        for cond in conds:
            print(f"  - Computing MMFF for {area} / {cond}...")
            # Collect all (mean, var) pairs for this area/cond across all units and time points
            means_all = []
            for t in time_bins:
                for unit_key, data in all_unit_stats.items():
                    if data['area'] == area and cond in data['traces']:
                        # Get mean and var in the win_size window
                        fr_trace = data['traces'][cond]['fr']
                        var_trace = data['traces'][cond]['var']
                        
                        # We use the smoothed traces as proxies for mean/var in the window
                        # Note: In a rigorous MMFF, we'd re-calculate count variance in the window.
                        # But since we have pre-smoothed traces, we'll use them at each time point.
                        mu = fr_trace[t] * (win_size / 1000.0)
                        v = var_trace[t] * (win_size / 1000.0) # Var scales linearly with time if Poisson-like
                        if mu > 0:
                            means_all.append(mu)
            
            if not means_all: continue
            
            # Target distribution of means (over all units and time)
            hist_bins = np.linspace(0, max(means_all), 20)
            target_counts, _ = np.histogram(means_all, bins=hist_bins)
            target_dist = target_counts / np.sum(target_counts)
            
            trace = []
            for t in time_bins:
                curr_ms = []
                curr_vs = []
                for unit_key, data in all_unit_stats.items():
                    if data['area'] == area and cond in data['traces']:
                        mu = data['traces'][cond]['fr'][t] * (win_size / 1000.0)
                        v = data['traces'][cond]['var'][t] * (win_size / 1000.0)
                        if mu > 0:
                            curr_ms.append(mu)
                            curr_vs.append(v)
                
                curr_ms = np.array(curr_ms)
                curr_vs = np.array(curr_vs)
                
                if len(curr_ms) < 5:
                    trace.append(np.nan)
                    continue
                
                # Match distribution
                curr_counts, _ = np.histogram(curr_ms, bins=hist_bins)
                valid = (curr_counts > 0) & (target_dist > 0)
                if not any(valid):
                    trace.append(np.nan)
                    continue
                    
                scale = np.min(curr_counts[valid] / target_dist[valid])
                
                matched_ms = []
                matched_vs = []
                for i in range(len(hist_bins)-1):
                    idx = np.where((curr_ms >= hist_bins[i]) & (curr_ms < hist_bins[i+1]))[0]
                    n_needed = int(np.floor(target_dist[i] * scale))
                    if len(idx) > 0 and n_needed > 0:
                        chosen = np.random.choice(idx, min(n_needed, len(idx)), replace=False)
                        matched_ms.extend(curr_ms[chosen])
                        matched_vs.extend(curr_vs[chosen])
                
                if matched_ms:
                    trace.append(np.mean(np.array(matched_vs) / np.array(matched_ms)))
                else:
                    trace.append(np.nan)
            
            area_mmff[area][cond] = trace
            
    return area_mmff, time_bins
