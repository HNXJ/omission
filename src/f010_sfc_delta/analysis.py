# core
import numpy as np
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.analysis.lfp.sfc import get_plv_spectrum, apply_subsampling

def analyze_sfc_delta(loader: DataLoader, areas: list):
    """
    Computes SFC Delta (Omission - Stimulus) for top units.
    """
    results = {}
    for area in areas:
        log.info(f"Computing SFC Delta for {area}")
        area_entries = loader.area_map.get(area, [])
        if not area_entries: continue
        
        all_units = []
        for entry in area_entries:
            ses = entry["session"]; p = entry["probe"]; start_ch = entry["start_ch"]; end_ch = entry["end_ch"]
            try:
                spk_aaab = np.load(loader.data_dir / f"ses{ses}-units-probe{p}-spk-AAAB.npy", mmap_mode='r')
                lfp_aaab = np.load(loader.data_dir / f"ses{ses}-probe{p}-lfp-AAAB.npy", mmap_mode='r')
                spk_axab = np.load(loader.data_dir / f"ses{ses}-units-probe{p}-spk-AXAB.npy", mmap_mode='r')
                lfp_axab = np.load(loader.data_dir / f"ses{ses}-probe{p}-lfp-AXAB.npy", mmap_mode='r')
                
                lfp_p1 = np.mean(lfp_aaab[:, start_ch:end_ch, 1000:1531], axis=1)
                lfp_p2 = np.mean(lfp_axab[:, start_ch:end_ch, 2031:2562], axis=1)
                
                u_start = int(spk_aaab.shape[1] * (start_ch/128.0)); u_end = int(spk_aaab.shape[1] * (end_ch/128.0))
                fr_p2 = np.mean(spk_axab[:, u_start:u_end, 2031:2562], axis=(0, 2))
                
                for u in range(u_end - u_start):
                    if fr_p2[u] > 0.001:
                        all_units.append({
                            "score": fr_p2[u],
                            "spk_stim": spk_aaab[:, u_start+u, 1000:1531], "lfp_stim": lfp_p1,
                            "spk_omit": spk_axab[:, u_start+u, 2031:2562], "lfp_omit": lfp_p2
                        })
            except Exception: continue
            
        all_units.sort(key=lambda x: x["score"], reverse=True)
        top_units = all_units[:20]
        if not top_units: continue
        
        deltas = []
        for unit in top_units:
            sub = apply_subsampling([unit["spk_stim"], unit["spk_omit"]])
            freqs, plv_s = get_plv_spectrum(unit["lfp_stim"], sub[0])
            freqs, plv_o = get_plv_spectrum(unit["lfp_omit"], sub[1])
            deltas.append(plv_o - plv_s)
            
        results[area] = {'freqs': freqs, 'deltas': deltas}
    return results
