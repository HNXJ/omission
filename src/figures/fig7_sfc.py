# core
import numpy as np
import scipy.signal
import plotly.graph_objects as go
from src.core.plotting import OmissionPlotter
from src.core.logger import log
from src.core.data_loader import DataLoader

def compute_ppc_spectrum(lfp_trials, spk_trials, fs=1000):
    """
    Computes Pairwise Phase Consistency (PPC) spectrum from 2 to 100 Hz.
    lfp_trials: (trials, time)
    spk_trials: (trials, time) for 1 unit
    """
    freqs = np.logspace(np.log10(2), np.log10(100), 30)
    ppc_vals = []
    
    for f in freqs:
        nyq = 0.5 * fs
        bw = max(2.0, f * 0.2) # min 2Hz bandwidth
        low = (f - bw/2) / nyq
        high = (f + bw/2) / nyq
        
        if high >= 1.0: high = 0.99
        if low <= 0.0: low = 0.01
        
        b, a = scipy.signal.butter(3, [low, high], btype='band')
        
        # Filter along time axis
        filtered = scipy.signal.filtfilt(b, a, lfp_trials, axis=1)
        analytic = scipy.signal.hilbert(filtered, axis=1)
        phase = np.angle(analytic)
        
        phase_flat = phase.flatten()
        spk_flat = spk_trials.flatten()
        
        # PPC formula: ( (sum w*cos)^2 + (sum w*sin)^2 - sum w^2 ) / ( (sum w)^2 - sum w^2 )
        sum_cos = np.sum(spk_flat * np.cos(phase_flat))
        sum_sin = np.sum(spk_flat * np.sin(phase_flat))
        sum_w = np.sum(spk_flat)
        sum_w2 = np.sum(spk_flat**2)
        
        denom = (sum_w**2 - sum_w2)
        if denom > 1e-5:
            p = ((sum_cos**2 + sum_sin**2) - sum_w2) / denom
        else:
            p = 0
        ppc_vals.append(p)
        
    return freqs, np.array(ppc_vals)

def generate_figure_7(output_dir: str = "D:/drive/outputs/oglo-8figs/f007"):
    """
    Generates Figure 7: Spike-Field Coupling (SFC) for 11 areas.
    Identifies Top 10 S+ and Top 10 O+ neurons, then computes PPC spectrum (1-100Hz).
    """
    log.progress(f"[action] Generating Figure 7: Spike-Field Coupling in {output_dir}...")
    
    loader = DataLoader()
    
    # Timing indices
    # fx: 500 to 1000
    # p1: 1000 to 1531
    # d1: 1531 to 2031
    # p2: 2031 to 2562
    
    for area in loader.CANONICAL_AREAS:
        log.progress(f"[action] Processing Area: {area} for SFC Spectrum")
        
        area_entries = loader.area_map.get(area, [])
        if not area_entries:
            continue
            
        all_s_plus_spk = []
        all_o_plus_spk = []
        
        # Load matched pairs safely
        for entry in area_entries:
            ses = entry["session"]
            p = entry["probe"]
            start_ch = entry["start_ch"]
            end_ch = entry["end_ch"]
            
            f_spk_aaab = loader.data_dir / f"ses{ses}-units-probe{p}-spk-AAAB.npy"
            f_lfp_aaab = loader.data_dir / f"ses{ses}-probe{p}-lfp-AAAB.npy"
            f_spk_axab = loader.data_dir / f"ses{ses}-units-probe{p}-spk-AXAB.npy"
            f_lfp_axab = loader.data_dir / f"ses{ses}-probe{p}-lfp-AXAB.npy"
            
            if not (f_spk_aaab.exists() and f_lfp_aaab.exists() and f_spk_axab.exists() and f_lfp_axab.exists()):
                continue
                
            try:
                spk_aaab_full = np.load(f_spk_aaab, mmap_mode='r')
                lfp_aaab_full = np.load(f_lfp_aaab, mmap_mode='r')
                spk_axab_full = np.load(f_spk_axab, mmap_mode='r')
                lfp_axab_full = np.load(f_lfp_axab, mmap_mode='r')
                
                # Slice
                lfp_aaab = lfp_aaab_full[:, start_ch:end_ch, :]
                lfp_axab = lfp_axab_full[:, start_ch:end_ch, :]
                
                total_units = spk_aaab_full.shape[1]
                u_start = int(total_units * (start_ch / 128.0))
                u_end = int(total_units * (end_ch / 128.0))
                
                spk_aaab = spk_aaab_full[:, u_start:u_end, :]
                spk_axab = spk_axab_full[:, u_start:u_end, :]
                
                # Check for trial mismatch just in case
                if spk_aaab.shape[0] != lfp_aaab.shape[0] or spk_axab.shape[0] != lfp_axab.shape[0]:
                    continue
                    
                # Slice LFP windows
                mean_lfp_p1 = np.mean(lfp_aaab[:, :, 1000:1531], axis=1) # (trials, time)
                mean_lfp_p2 = np.mean(lfp_axab[:, :, 2031:2562], axis=1)
                
                # Slice SPK windows for scoring
                fr_p1 = np.mean(spk_aaab[:, :, 1000:1531], axis=(0, 2)) 
                fr_fx = np.mean(spk_aaab[:, :, 500:1000], axis=(0, 2))
                s_score = fr_p1 / (fr_fx + 1e-5)
                
                fr_p2 = np.mean(spk_axab[:, :, 2031:2562], axis=(0, 2))
                fr_d1 = np.mean(spk_axab[:, :, 1531:2031], axis=(0, 2))
                o_score = fr_p2 / (fr_d1 + 1e-5)
                
                for u in range(spk_aaab.shape[1]):
                    all_s_plus_spk.append((s_score[u], spk_aaab[:, u, 1000:1531], mean_lfp_p1))
                    all_o_plus_spk.append((o_score[u], spk_axab[:, u, 2031:2562], mean_lfp_p2))
            except Exception as e:
                log.warning(f"Error processing session {ses} probe {p}: {e}")
                continue
                
        # Sort and take top 10
        all_s_plus_spk.sort(key=lambda x: x[0], reverse=True)
        all_o_plus_spk.sort(key=lambda x: x[0], reverse=True)
        
        top_10_s = all_s_plus_spk[:10]
        top_10_o = all_o_plus_spk[:10]
        
        if not top_10_s or not top_10_o:
            continue
            
        s_ppc_spectra = []
        for _, spk_w, lfp_w in top_10_s:
            freqs, ppc = compute_ppc_spectrum(lfp_w, spk_w)
            s_ppc_spectra.append(ppc)
            
        o_ppc_spectra = []
        for _, spk_w, lfp_w in top_10_o:
            freqs, ppc = compute_ppc_spectrum(lfp_w, spk_w)
            o_ppc_spectra.append(ppc)
            
        s_ppc_mean = np.mean(s_ppc_spectra, axis=0)
        o_ppc_mean = np.mean(o_ppc_spectra, axis=0)
        
        plotter = OmissionPlotter(
            title=f"Figure 7: {area} Spike-Field Coupling (PPC)",
            subtitle="Top 10 S+ (Stimulus p1) vs. Top 10 O+ (Omission p2)"
        )
        
        plotter.set_axes("Frequency", "Hz", "Pairwise Phase Consistency", "PPC")
        
        plotter.add_trace(go.Scatter(x=freqs, y=s_ppc_mean, line=dict(color="#CFB87C", width=3)), "S+ Neurons (Stimulus Window)")
        plotter.add_trace(go.Scatter(x=freqs, y=o_ppc_mean, line=dict(color="#9400D3", width=3)), "O+ Neurons (Omission Window)")
        
        plotter.fig.update_xaxes(type="log", tickvals=[2, 4, 8, 15, 30, 50, 100])
        plotter.save(output_dir, f"fig7_sfc_spectrum_{area}")
        
    log.progress(f"[action] Figure 7 complete for all areas.")

if __name__ == "__main__":
    generate_figure_7()