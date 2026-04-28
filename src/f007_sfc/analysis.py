import numpy as np
import scipy.signal as signal
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.analysis.lfp.sfc import get_plv_spectrum, apply_subsampling
from src.analysis.stats.tiers import get_significance_tier, run_permutation_test

def get_band_phases(lfp, freqs, fs=1000):
    """
    Filters LFP and extracts instantaneous phase using Hilbert transform.
    """
    phases = {}
    bands = {
        'Theta': (4, 8),
        'Alpha': (8, 12),
        'Beta': (13, 30),
        'Gamma': (30, 80)
    }
    for name, (low, high) in bands.items():
        # Bandpass filter
        nyq = 0.5 * fs
        b, a = signal.butter(3, [low/nyq, high/nyq], btype='band')
        filtered = signal.filtfilt(b, a, lfp, axis=-1)
        # Hilbert for phase
        z = signal.hilbert(filtered, axis=-1)
        phases[name] = np.angle(z)
    return phases

def analyze_circular_sfc(loader: DataLoader, areas: list):
    """
    Computes circular phase distributions for top units.
    """
    results = {}
    for area in areas:
        print(f"[action] Computing Circular SFC for {area}")
        
        # Load aligned signals (omission window)
        spk_s = loader.get_signal(mode="spk", condition="AAAB", area=area, align_to="omission")
        lfp_s = loader.get_signal(mode="lfp", condition="AAAB", area=area, align_to="omission")
        
        spk_o = loader.get_signal(mode="spk", condition="AXAB", area=area, align_to="omission")
        lfp_o = loader.get_signal(mode="lfp", condition="AXAB", area=area, align_to="omission")
        
        if not spk_s or not lfp_s or not spk_o or not lfp_o: continue
        
        # Area Results structure
        results[area] = {'bands': {}}
        
        # 1. ANALYZE S+ (Top 5 units)
        s_unit_data = []
        for lfp_arr, spk_arr in zip(lfp_s, spk_s):
            if lfp_arr.size == 0: continue
            mean_lfp = np.mean(lfp_arr, axis=1) # (trials, time)
            fr = np.mean(spk_arr[:, :, 1000:1500], axis=(0, 2))
            for u_idx, val in enumerate(fr):
                if val > 0.1: s_unit_data.append((val, mean_lfp, spk_arr[:, u_idx, :]))
        s_unit_data.sort(key=lambda x: x[0], reverse=True)
        top_s = s_unit_data[:5]
        
        # 2. ANALYZE O+ (Top 5 units)
        o_unit_data = []
        for lfp_arr, spk_arr in zip(lfp_o, spk_o):
            if lfp_arr.size == 0: continue
            mean_lfp = np.mean(lfp_arr, axis=1)
            fr = np.mean(spk_arr[:, :, 1000:1500], axis=(0, 2))
            for u_idx, val in enumerate(fr):
                if val > 0.1: o_unit_data.append((val, mean_lfp, spk_arr[:, u_idx, :]))
        o_unit_data.sort(key=lambda x: x[0], reverse=True)
        top_o = o_unit_data[:5]
        
        if not top_s or not top_o: continue

        # 3. PHASE EXTRACTION
        for name in ['Theta', 'Alpha', 'Beta', 'Gamma']:
            results[area]['bands'][name] = {'s_phases': [], 'o_phases': []}
            
            # Extract phases for S+
            for _, lfp_mat, spk_mat in top_s:
                phase_mat = get_band_phases(lfp_mat, None)[name] # (trials, time)
                # Spike indices in window 1031-1531 (relative to omission)
                t_mask = slice(1031, 1531)
                unit_phases = phase_mat[:, t_mask][spk_mat[:, t_mask] > 0]
                results[area]['bands'][name]['s_phases'].extend(unit_phases.tolist())
                
            # Extract phases for O+
            for _, lfp_mat, spk_mat in top_o:
                phase_mat = get_band_phases(lfp_mat, None)[name]
                unit_phases = phase_mat[:, t_mask][spk_mat[:, t_mask] > 0]
                results[area]['bands'][name]['o_phases'].extend(unit_phases.tolist())

        # 4. STATS (Rayleigh-ish proxy via Vector Strength)
        def get_vs(phases):
            if not phases: return 0
            phases = np.array(phases)
            return np.abs(np.mean(np.exp(1j * phases)))
            
        vs_s = get_vs(results[area]['bands']['Beta']['s_phases'])
        vs_o = get_vs(results[area]['bands']['Beta']['o_phases'])
        
        # Permutation test for Beta-band VS difference
        p_val, _ = run_permutation_test(
            np.array(results[area]['bands']['Beta']['o_phases']),
            np.array(results[area]['bands']['Beta']['s_phases']),
            metric=lambda x, y: np.abs(np.mean(np.exp(1j * x))) - np.abs(np.mean(np.exp(1j * y)))
        )
        tier, k, stars = get_significance_tier(p_val)
        
        results[area]['stats'] = {
            'p': p_val, 'tier': tier, 'stars': stars,
            'vs_s': vs_s, 'vs_o': vs_o,
            'test': 'Circular VS Permutation'
        }
        
    return results
