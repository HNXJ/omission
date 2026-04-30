import numpy as np
import pandas as pd
from pathlib import Path
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
import scipy.signal as signal

def get_band_power(lfp, fs=1000):
    """Computes power in canonical bands."""
    bands = {
        'Theta': (4, 8),
        'Alpha': (8, 12),
        'Beta': (13, 30),
        'Gamma': (30, 80)
    }
    powers = {}
    nyq = 0.5 * fs
    for name, (low, high) in bands.items():
        b, a = signal.butter(3, [low/nyq, high/nyq], btype='band')
        filtered = signal.filtfilt(b, a, lfp, axis=-1)
        # Power = mean of squared amplitude (Hilbert envelope squared or just squared signal for narrowband)
        powers[name] = np.mean(np.square(filtered), axis=-1)
    return powers

class ProfileSearcher:
    """
    Utility to find neurons or spectral bands matching specific activity profiles.
    x: p3, y: p1
    z: d3, w: d1
    """
    def __init__(self, loader=None):
        self.loader = loader or DataLoader()
        # Timing constants (ms)
        self.P_DUR = 515
        self.CYCLE = 1031
        self.BASE_OFFSET = 1000
        
        self.slices = {
            'p1': slice(self.BASE_OFFSET, self.BASE_OFFSET + self.P_DUR),
            'd1': slice(self.BASE_OFFSET + self.P_DUR, self.BASE_OFFSET + self.CYCLE),
            'p3': slice(self.BASE_OFFSET + 2*self.CYCLE, self.BASE_OFFSET + 2*self.CYCLE + self.P_DUR),
            'd3': slice(self.BASE_OFFSET + 2*self.CYCLE + self.P_DUR, self.BASE_OFFSET + 3*self.CYCLE)
        }

    def search_neurons(self, areas=None, conditions=None):
        """Searches all units for profile matches."""
        areas = areas or self.loader.CANONICAL_AREAS
        conditions = conditions or ["AXAB", "BXBA", "RXRR"]
        
        results = []
        for area in areas:
            print(f"""[action] Profiling neurons in {area}...""")
            units = self.loader.get_units_by_area(area)
            for uid in units:
                profiles = []
                for cond in conditions:
                    spk = self.loader.load_unit_spikes(uid, condition=cond)
                    if spk is not None:
                        profiles.append({
                            'y': np.mean(spk[:, self.slices['p1']]) * 1000,
                            'w': np.mean(spk[:, self.slices['d1']]) * 1000,
                            'x': np.mean(spk[:, self.slices['p3']]) * 1000,
                            'z': np.mean(spk[:, self.slices['d3']]) * 1000
                        })
                
                if not profiles: continue
                
                # Mean across conditions
                avgs = {k: np.mean([p[k] for p in profiles]) for k in ['x', 'y', 'z', 'w']}
                if avgs['y'] < 0.5 and avgs['x'] < 0.5: continue # Filter inactive
                
                results.append({
                    'type': 'neuron', 'id': uid, 'area': area,
                    **avgs,
                    'ratio_xy': avgs['x'] / avgs['y'] if avgs['y'] > 0 else 0,
                    'ratio_zw': avgs['z'] / avgs['w'] if avgs['w'] > 0 else 0
                })
        return pd.DataFrame(results)

    def search_lfp_bands(self, areas=None, conditions=None):
        """Searches spectral bands (per area average LFP) for profile matches."""
        areas = areas or self.loader.CANONICAL_AREAS
        conditions = conditions or ["AXAB", "BXBA", "RXRR"]
        bands = ['Theta', 'Alpha', 'Beta', 'Gamma']
        
        results = []
        for area in areas:
            print(f"""[action] Profiling LFP bands in {area}...""")
            for cond in conditions:
                lfp_list = self.loader.get_signal("lfp", condition=cond, area=area)
                if not lfp_list: continue
                
                # Collect power values for each band across all data segments
                # Structure: power_samples[band][period] = [val1, val2, ...]
                power_samples = {b: {p: [] for p in self.slices.keys()} for b in bands}
                
                for arr in lfp_list:
                    # Average over channels and trials
                    seg_mean = np.mean(arr, axis=(0, 1))
                    
                    for b_name in bands:
                        for p_name, p_slice in self.slices.items():
                            segment = seg_mean[p_slice]
                            p_val = list(get_band_power(segment.reshape(1, -1))[b_name])[0]
                            power_samples[b_name][p_name].append(p_val)

                # Aggregate results for this area/cond
                for b_name in bands:
                    p_means = {p: np.mean(vals) if vals else 0 for p, vals in power_samples[b_name].items()}
                    
                    results.append({
                        'type': 'lfp_band', 'id': f"{area}_{b_name}", 'area': area, 'band': b_name,
                        'x': p_means['p3'], 'y': p_means['p1'], 'z': p_means['d3'], 'w': p_means['d1'],
                        'ratio_xy': p_means['p3'] / p_means['p1'] if p_means['p1'] > 0 else 0,
                        'ratio_zw': p_means['d3'] / p_means['d1'] if p_means['d1'] > 0 else 0
                    })
        
        # Aggregate across conditions for LFP
        df = pd.DataFrame(results)
        if df.empty: return df
        # Drop string columns that shouldn't be averaged
        agg_df = df.groupby(['id', 'area', 'band']).mean(numeric_only=True).reset_index()
        agg_df['type'] = 'lfp_band'
        return agg_df
