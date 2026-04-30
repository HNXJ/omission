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
    Utility to identify repetition-scaling and omission-selectivity profiles.
    
    Scientific Mandates:
    - Separate SPK, MUAe, and LFP branches.
    - Use matched full-sequence controls for omission contrast.
    - Maintain family-specific (p2, p3, p4) resolution.
    """
    
    OMISSION_FAMILIES = {
        'p2': {
            'omission': ["AXAB", "BXBA", "RXRR"],
            'control': ["AAAB", "BBBA", "RRRR"],
            'onset': 1031.0
        },
        'p3': {
            'omission': ["AAXB", "BBXA", "RRXR"],
            'control': ["AAAB", "BBBA", "RRRR"],
            'onset': 2062.0
        },
        'p4': {
            'omission': ["AAAX", "BBBX", "RRRX"],
            'control': ["AAAB", "BBBA", "RRRR"],
            'onset': 3093.0
        }
    }

    def __init__(self, loader=None):
        self.loader = loader or DataLoader()
        self.BASE_OFFSET = 1000 # 0ms in arrays

    def _get_windows(self, onset_ms):
        """Returns slices for omission and matched pre-omission baseline."""
        # Omission window: 0 to 515ms post-onset
        # Baseline window: -515 to 0ms pre-onset
        om_start = self.BASE_OFFSET + int(onset_ms)
        return {
            'omission': slice(om_start, om_start + 515),
            'baseline': slice(om_start - 515, om_start)
        }

    def search_omission_profiles(self, mode="spk", areas=None):
        """
        Identifies omission sensitivity by comparing omission trials to matched controls.
        Separates by signal mode (spk/lfp).
        """
        areas = areas or self.loader.CANONICAL_AREAS
        results = []
        
        for area in areas:
            print(f"""[action] Profiling {mode} omission sensitivity in {area}...""")
            
            if mode == "spk":
                units = self.loader.get_units_by_area(area)
                for uid in units:
                    unit_res = self._profile_unit_omission(uid, area)
                    if unit_res: results.extend(unit_res)
            else:
                # LFP logic per area-band
                area_res = self._profile_lfp_omission(area)
                if area_res: results.extend(area_res)
                
        return pd.DataFrame(results)

    def _profile_unit_omission(self, uid, area):
        """Internal logic for single-unit omission contrast."""
        unit_results = []
        for family, cfg in self.OMISSION_FAMILIES.items():
            wins = self._get_windows(cfg['onset'])
            
            # 1. Load Omission conditions
            om_rates = []
            for cond in cfg['omission']:
                spk = self.loader.load_unit_spikes(uid, condition=cond)
                if spk is not None:
                    # Rate in Hz
                    om_rates.append(np.mean(spk[:, wins['omission']]) * 1000)
            
            # 2. Load Matched Controls
            ctrl_rates = []
            for cond in cfg['control']:
                spk = self.loader.load_unit_spikes(uid, condition=cond)
                if spk is not None:
                    ctrl_rates.append(np.mean(spk[:, wins['omission']]) * 1000)
            
            if not om_rates or not ctrl_rates: continue
            
            avg_om = np.mean(om_rates)
            avg_ctrl = np.mean(ctrl_rates)
            
            # Omission Effect: Om - Ctrl
            effect = avg_om - avg_ctrl
            
            unit_results.append({
                'type': 'spk', 'id': uid, 'area': area, 'family': family,
                'omission_rate': avg_om, 'control_rate': avg_ctrl,
                'effect_size': effect,
                'is_omission_positive': effect > 2.0 and avg_om > 1.0 # Heuristic for now
            })
        return unit_results

    def _profile_lfp_omission(self, area):
        """Internal logic for LFP band omission contrast."""
        bands = ['Theta', 'Alpha', 'Beta', 'Gamma']
        lfp_results = []
        
        for family, cfg in self.OMISSION_FAMILIES.items():
            wins = self._get_windows(cfg['onset'])
            
            # Compute power for Omission vs Control
            for b_name in bands:
                om_powers = []
                for cond in cfg['omission']:
                    lfp_list = self.loader.get_signal("lfp", condition=cond, area=area)
                    if not lfp_list: continue
                    for arr in lfp_list:
                        seg_mean = np.mean(arr, axis=(0, 1))
                        om_powers.append(list(get_band_power(seg_mean[wins['omission']].reshape(1, -1))[b_name])[0])
                
                ctrl_powers = []
                for cond in cfg['control']:
                    lfp_list = self.loader.get_signal("lfp", condition=cond, area=area)
                    if not lfp_list: continue
                    for arr in lfp_list:
                        seg_mean = np.mean(arr, axis=(0, 1))
                        ctrl_powers.append(list(get_band_power(seg_mean[wins['omission']].reshape(1, -1))[b_name])[0])
                
                if not om_powers or not ctrl_powers: continue
                
                avg_om = np.mean(om_powers)
                avg_ctrl = np.mean(ctrl_powers)
                ratio = avg_om / avg_ctrl if avg_ctrl > 0 else 1.0
                
                lfp_results.append({
                    'type': 'lfp', 'id': f"{area}_{b_name}", 'area': area, 'family': family, 'band': b_name,
                    'omission_power': avg_om, 'control_power': avg_ctrl,
                    'ratio': ratio,
                    'is_suppressed': ratio < 0.8
                })
        return lfp_results

    def search_repetition_profiles(self, mode="spk", areas=None):
        """Auxiliary descriptive metrics for sequence position scaling (x/y)."""
        areas = areas or self.loader.CANONICAL_AREAS
        results = []
        
        # p1 and p3 windows for AXAB style repetition (1031ms cycle)
        p1_win = slice(self.BASE_OFFSET, self.BASE_OFFSET + 515)
        p3_win = slice(self.BASE_OFFSET + 2062, self.BASE_OFFSET + 2577)
        
        for area in areas:
            print(f"""[action] Profiling repetition scaling in {area}...""")
            if mode == "spk":
                units = self.loader.get_units_by_area(area)
                for uid in units:
                    spk = self.loader.load_unit_spikes(uid, condition="AXAB")
                    if spk is not None:
                        y = np.mean(spk[:, p1_win]) * 1000
                        x = np.mean(spk[:, p3_win]) * 1000
                        results.append({'type': 'spk', 'id': uid, 'area': area, 'x': x, 'y': y, 'ratio': x/y if y>0 else 0})
            else:
                # Basic LFP Gamma repetition for demo
                for cond in ["AXAB"]:
                    lfp_list = self.loader.get_signal("lfp", condition=cond, area=area)
                    if not lfp_list: continue
                    for arr in lfp_list:
                        seg = np.mean(arr, axis=(0, 1))
                        y = list(get_band_power(seg[p1_win].reshape(1, -1))['Gamma'])[0]
                        x = list(get_band_power(seg[p3_win].reshape(1, -1))['Gamma'])[0]
                        results.append({'type': 'lfp', 'id': f"{area}_Gamma", 'area': area, 'x': x, 'y': y, 'ratio': x/y if y>0 else 0})
        return pd.DataFrame(results)
