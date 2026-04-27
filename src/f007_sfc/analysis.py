import numpy as np
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.analysis.lfp.sfc import get_plv_spectrum, apply_subsampling
from src.analysis.stats.tiers import get_significance_tier, run_permutation_test, run_frequency_wise_comparison

def analyze_sfc_plv(loader: DataLoader, areas: list):
    """
    Computes SFC (PLV) spectrum for top O+ and S+ units in each area.
    """
    results = {}
    for area in areas:
        print(f"[action] Computing SFC for {area}")
        
        # Load aligned signals
        spk_s = loader.get_signal(mode="spk", condition="AAAB", area=area, align_to="omission")
        lfp_s = loader.get_signal(mode="lfp", condition="AAAB", area=area, align_to="omission")
        
        spk_o = loader.get_signal(mode="spk", condition="AXAB", area=area, align_to="omission")
        lfp_o = loader.get_signal(mode="lfp", condition="AXAB", area=area, align_to="omission")
        
        if not spk_s or not lfp_s or not spk_o or not lfp_o:
            print(f"[warning] Missing data for {area}, skipping.")
            continue
        
        # Extract S+ top units
        s_unit_data = []
        for lfp_arr, spk_arr in zip(lfp_s, spk_s):
            if lfp_arr.size == 0 or spk_arr.size == 0: continue
            mean_lfp = np.mean(lfp_arr, axis=1) # (trials, time)
            fr = np.mean(spk_arr[:, :, 1000:1500], axis=(0, 2))
            for u_idx, val in enumerate(fr):
                if val > 0.001:
                    s_unit_data.append((val, mean_lfp, spk_arr[:, u_idx, :]))
                    
        s_unit_data.sort(key=lambda x: x[0], reverse=True)
        top_s_data = s_unit_data[:10]
        
        # Extract O+ top units
        o_unit_data = []
        for lfp_arr, spk_arr in zip(lfp_o, spk_o):
            if lfp_arr.size == 0 or spk_arr.size == 0: continue
            mean_lfp = np.mean(lfp_arr, axis=1)
            fr = np.mean(spk_arr[:, :, 1000:1500], axis=(0, 2))
            for u_idx, val in enumerate(fr):
                if val > 0.001:
                    o_unit_data.append((val, mean_lfp, spk_arr[:, u_idx, :]))
                    
        o_unit_data.sort(key=lambda x: x[0], reverse=True)
        top_o_data = o_unit_data[:10]
        
        if not top_s_data or not top_o_data:
            print(f"[warning] Not enough responsive units for {area}, skipping.")
            continue
        
        # Subsampling
        all_spks = [d[2] for d in top_s_data] + [d[2] for d in top_o_data]
        sub_spks = apply_subsampling(all_spks)
        
        # Calculate PLV spectra in the window 0-500ms post onset
        s_spectra = []
        for i, d in enumerate(top_s_data):
            lfp_full = d[1]
            spk_full = sub_spks[i].copy()
            spk_full[:, :1000] = 0
            spk_full[:, 1500:] = 0
            freqs, spec = get_plv_spectrum(lfp_full, spk_full)
            s_spectra.append(spec)
            
        o_spectra = []
        for i, d in enumerate(top_o_data):
            lfp_full = d[1]
            spk_full = sub_spks[len(top_s_data)+i].copy()
            spk_full[:, :1000] = 0
            spk_full[:, 1500:] = 0
            _, spec = get_plv_spectrum(lfp_full, spk_full)
            o_spectra.append(spec)
            
        results[area] = {'freqs': freqs, 's_plus': s_spectra, 'o_plus': o_spectra}
        
        # 3. STATISTICAL COMPARISON (Significance-Tier Standard)
        # Point-by-point Frequency Comparison
        p_corrected, rejected_mask = run_frequency_wise_comparison(np.array(o_spectra), np.array(s_spectra))
        
        # Gamma band window: 30-80 Hz for Global Star Rating
        g_mask = (freqs >= 30) & (freqs <= 80)
        plv_s_gamma = [np.mean(spec[g_mask]) for spec in s_spectra]
        plv_o_gamma = [np.mean(spec[g_mask]) for spec in o_spectra]
        
        p_val_gamma, _ = run_permutation_test(np.array(plv_o_gamma), np.array(plv_s_gamma))
        tier, k, stars = get_significance_tier(p_val_gamma)
        
        results[area]['stats'] = {
            'p': p_val_gamma, 
            'tier': tier, 
            'stars': stars, 
            'test': 'Permutation Test (Gamma PLV)',
            'p_spectrum': p_corrected,
            'rejected_mask': rejected_mask
        }
        print(f"[stats] SFC Area {area} | {tier} ({p_val_gamma:.2e}) | {stars}")
        
    return results
