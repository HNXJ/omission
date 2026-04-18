# core
import numpy as np
import plotly.graph_objects as go
from src.analysis.visualization.plotting import OmissionPlotter
from src.analysis.io.logger import log
from src.analysis.io.loader import DataLoader
from src.analysis.lfp.sfc import get_plv_spectrum, apply_subsampling

def generate_figure_7(output_dir: str = "D:/drive/outputs/oglo-8figs/f007"):
    """
    Generates Figure 7: SFC (PLV) with ±SEM and Subsampling Correction.
    """
    log.progress(f"[action] Generating Figure 7: SFC PLV (11 Areas) in {output_dir}...")
    
    loader = DataLoader()
    
    for area in loader.CANONICAL_AREAS:
        log.progress(f"[action] Processing Area: {area} for SFC PLV")
        
        # We need to manually match session-probe pairs to ensure SPK and LFP alignment
        area_entries = loader.area_map.get(area, [])
        if not area_entries: continue
            
        all_s_plus = []
        all_o_plus = []
        
        for entry in area_entries:
            ses = entry["session"]; p = entry["probe"]; start_ch = entry["start_ch"]; end_ch = entry["end_ch"]
            
            # Load specific session files
            f_spk_aaab = loader.data_dir / f"ses{ses}-units-probe{p}-spk-AAAB.npy"
            f_lfp_aaab = loader.data_dir / f"ses{ses}-probe{p}-lfp-AAAB.npy"
            f_spk_axab = loader.data_dir / f"ses{ses}-units-probe{p}-spk-AXAB.npy"
            f_lfp_axab = loader.data_dir / f"ses{ses}-probe{p}-lfp-AXAB.npy"
            
            if not (f_spk_aaab.exists() and f_lfp_aaab.exists() and f_spk_axab.exists() and f_lfp_axab.exists()):
                continue
                
            try:
                # Use mmap for efficiency
                spk_aaab_full = np.load(f_spk_aaab, mmap_mode='r'); lfp_aaab_full = np.load(f_lfp_aaab, mmap_mode='r')
                spk_axab_full = np.load(f_spk_axab, mmap_mode='r'); lfp_axab_full = np.load(f_lfp_axab, mmap_mode='r')
                
                # Verify trial alignment within each condition
                if spk_aaab_full.shape[0] != lfp_aaab_full.shape[0] or spk_axab_full.shape[0] != lfp_axab_full.shape[0]:
                    log.warning(f"Trial mismatch in session {ses} probe {p}, skipping.")
                    continue
                
                # Slice area-specific channels/units
                lfp_aaab = lfp_aaab_full[:, start_ch:end_ch, :]; lfp_axab = lfp_axab_full[:, start_ch:end_ch, :]
                u_start = int(spk_aaab_full.shape[1] * (start_ch/128.0)); u_end = int(spk_aaab_full.shape[1] * (end_ch/128.0))
                spk_aaab = spk_aaab_full[:, u_start:u_end, :]; spk_axab = spk_axab_full[:, u_start:u_end, :]
                
                # Mean LFP for area
                mean_lfp_p1 = np.mean(lfp_aaab[:, :, 1000:1531], axis=1) # (trials, time)
                mean_lfp_p2 = np.mean(lfp_axab[:, :, 2031:2562], axis=1)
                
                # SNR Filtering
                fr_p1_mat = np.mean(spk_aaab[:, :, 1000:1531], axis=2); fr_fx_mat = np.mean(spk_aaab[:, :, 500:1000], axis=2)
                fr_p1 = np.mean(fr_p1_mat, axis=0); fr_fx = np.mean(fr_fx_mat, axis=0)
                std_fx = np.std(fr_fx_mat, axis=0) + 1e-5
                s_snr = (fr_p1 - fr_fx) / std_fx
                
                fr_p2_mat = np.mean(spk_axab[:, :, 2031:2562], axis=2); fr_d1_mat = np.mean(spk_axab[:, :, 1531:2031], axis=2)
                fr_p2 = np.mean(fr_p2_mat, axis=0); fr_d1 = np.mean(fr_d1_mat, axis=0)
                std_d1 = np.std(fr_d1_mat, axis=0) + 1e-5
                o_snr = (fr_p2 - fr_d1) / std_d1
                
                for u in range(spk_aaab.shape[1]):
                    if s_snr[u] > 1.0 and fr_p1[u] > 0.0005:
                        all_s_plus.append({"score": fr_p1[u]/(fr_fx[u]+1e-5), "spk": spk_aaab[:, u, 1000:1531], "lfp": mean_lfp_p1})
                    if o_snr[u] > 1.0 and fr_p2[u] > 0.0005:
                        all_o_plus.append({"score": fr_p2[u]/(fr_d1[u]+1e-5), "spk": spk_axab[:, u, 2031:2562], "lfp": mean_lfp_p2})
            except Exception as e:
                log.warning(f"Error processing session {ses}: {e}")
                continue
                
        all_s_plus.sort(key=lambda x: x["score"], reverse=True)
        all_o_plus.sort(key=lambda x: x["score"], reverse=True)
        top_10_s = all_s_plus[:10]; top_10_o = all_o_plus[:10]
        
        n_s = len(top_10_s); n_o = len(top_10_o)
        if n_s == 0 or n_o == 0: continue
            
        # Perform Subsampling to equate spike count across all identified neurons
        all_spks = [u["spk"] for u in top_10_s] + [u["spk"] for u in top_10_o]
        subsampled_spks = apply_subsampling(all_spks)
        
        # Split back
        sub_s = subsampled_spks[:n_s]
        sub_o = subsampled_spks[n_s:]
        
        s_spectra = [get_plv_spectrum(top_10_s[i]["lfp"], sub_s[i])[1] for i in range(n_s)]
        o_spectra = [get_plv_spectrum(top_10_o[i]["lfp"], sub_o[i])[1] for i in range(n_o)]
        freqs, _ = get_plv_spectrum(top_10_s[0]["lfp"], sub_s[0])
        
        plotter = OmissionPlotter(title=f"Figure 7: {area} SFC (PLV)", subtitle="Subsampling Corrected: Top 10 S+ vs O+")
        plotter.set_axes("Frequency", "Hz", "Phase-Locking Value", "PLV")
        
        for name, spectra, color in [("S+ (Stimulus)", s_spectra, "#CFB87C"), ("O+ (Omission)", o_spectra, "#9400D3")]:
            m = np.mean(spectra, axis=0); s = np.std(spectra, axis=0) / np.sqrt(len(spectra))
            rgba = f"rgba{tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.2,)}"
            plotter.add_trace(go.Scatter(x=freqs, y=m+s, mode='lines', line=dict(width=0), showlegend=False), name=f"{name}_up")
            plotter.add_trace(go.Scatter(x=freqs, y=m-s, mode='lines', line=dict(width=0), fill='tonexty', fillcolor=rgba, showlegend=False), name=f"{name}_down")
            plotter.add_trace(go.Scatter(x=freqs, y=m, mode='lines', line=dict(color=color, width=3)), name=name)
            
        plotter.fig.update_xaxes(type="log", tickvals=[4, 8, 13, 30, 80])
        plotter.save(output_dir, f"fig7_sfc_spectrum_{area}")
        
    log.progress(f"[action] Figure 7 complete.")

if __name__ == "__main__":
    generate_figure_7()