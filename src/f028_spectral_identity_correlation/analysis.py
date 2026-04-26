import numpy as np
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f027_identity_coding.analysis import decode_omission_identity
from src.analysis.lfp.lfp_pipeline import get_lfp_signal
from src.analysis.lfp.lfp_tfr import compute_band_power_efficiently

def analyze_spectral_identity_correlation(areas: list):
    """
    Correlates Band Power Dynamics with Identity Decoding Accuracy.
    Only Stable-Plus units, trial-matched.
    """
    loader = DataLoader()
    results = {}

    for area in areas:
        log.progress(f"Correlating Spectral-Identity for {area}")
        
        # 1. Get Decoding Accuracy (f027 logic)
        # AXAB vs BXBA
        spk_ax = loader.get_signal(mode="spk", condition="AXAB", area=area)
        spk_bx = loader.get_signal(mode="spk", condition="BXBA", area=area)
        
        if not spk_ax or not spk_bx: 
            log.warning(f"Missing spike data for {area}")
            continue
            
        # Find min units across sessions to allow concatenation
        min_units_ax = min(arr.shape[1] for arr in spk_ax)
        min_units_bx = min(arr.shape[1] for arr in spk_bx)
        min_units = min(min_units_ax, min_units_bx)
        
        # Trim units and concatenate
        final_spk_ax = np.concatenate([arr[:, :min_units, :] for arr in spk_ax], axis=0)
        final_spk_bx = np.concatenate([arr[:, :min_units, :] for arr in spk_bx], axis=0)
        
        # Filter for Stable-Plus (FR > 1Hz in omission window)
        # Omission window in get_signal(align_to='p1') depends on pre/post.
        # Identity decoding usually uses a wide window.
        fr_ax = np.mean(final_spk_ax, axis=(0, 2)) * 1000
        stable_plus_idx = np.where(fr_ax > 1.0)[0]
        
        if len(stable_plus_idx) < 2:
            log.warning(f"Not enough Stable-Plus units in {area} ({len(stable_plus_idx)})")
            continue
            
        final_spk_ax = final_spk_ax[:, stable_plus_idx, :]
        final_spk_bx = final_spk_bx[:, stable_plus_idx, :]
        
        # Decode (AXAB vs BXBA identity)
        # Decoding returns (times, accuracies)
        # We use a 200ms window, 50ms step for identity decoding
        dec_times, dec_acc = decode_omission_identity(final_spk_ax, final_spk_bx, win_ms=200, step_ms=50)
        
        # 2. Get Band Power for the same trials (AXAB)
        lfp_ax = get_lfp_signal(area, "AXAB", align_to="omission", pre_ms=2000, post_ms=2000)
        if lfp_ax.size == 0: continue
        
        # We focus on the omission window [0, 1000] ms
        # lfp_ax is (trials, channels, time), time=4000ms, centered at 2000ms
        freqs, times_ms, band_dict = compute_band_power_efficiently(lfp_ax)
        times_local = times_ms - 2000.0
        
        # Filter for omission window [0, 1000]
        mask = (times_local >= 0) & (times_local <= 1000)
        
        area_spectral = {}
        for band, data in band_dict.items():
            # data shape: (trials, channels, time)
            # Average over trials and channels for pop-level spectral trace
            area_spectral[band] = np.mean(data[:, :, mask], axis=(0, 1))
            
        # 3. Resample Decoding to match Spectral (or vice-versa)
        # Spectral sampling is usually 1ms (if not downsampled)
        # Decoding is 50ms step.
        # Let's interpolate decoding accuracy to spectral times.
        spec_times_window = times_local[mask]
        dec_acc_interp = np.interp(spec_times_window, dec_times, dec_acc)
        
        # 4. Compute Correlation (Pearson)
        band_corrs = {}
        for band, spec_trace in area_spectral.items():
            if len(spec_trace) == len(dec_acc_interp):
                # We correlate the temporal evolution of power vs decoding
                c = np.corrcoef(spec_trace, dec_acc_interp)[0, 1]
                band_corrs[band] = c
                
        results[area] = {
            "correlations": band_corrs,
            "dec_acc": dec_acc,
            "dec_times": dec_times,
            "spectral": area_spectral,
            "spec_times": spec_times_window
        }
        log.info(f"Area {area} Corrs: {band_corrs}")

    return results
