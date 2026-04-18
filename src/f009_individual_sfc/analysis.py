# core
import numpy as np
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.analysis.lfp.sfc import get_plv_spectrum, apply_subsampling

def analyze_individual_sfc(loader: DataLoader, areas: list):
    """
    Computes individual unit SFC (PLV) for top S+ and O+ units.
    """
    results = {}
    for area in areas:
        log.info(f"Computing Individual SFC for {area}")
        area_entries = loader.area_map.get(area, [])
        if not area_entries: continue
        
        all_s = []; all_o = []
        for entry in area_entries:
            ses = entry["session"]; p = entry["probe"]; start_ch = entry["start_ch"]; end_ch = entry["end_ch"]
            
            try:
                spk_aaab_full = np.load(loader.data_dir / f"ses{ses}-units-probe{p}-spk-AAAB.npy", mmap_mode='r')
                lfp_aaab_full = np.load(loader.data_dir / f"ses{ses}-probe{p}-lfp-AAAB.npy", mmap_mode='r')
                spk_axab_full = np.load(loader.data_dir / f"ses{ses}-units-probe{p}-spk-AXAB.npy", mmap_mode='r')
                lfp_axab_full = np.load(loader.data_dir / f"ses{ses}-probe{p}-lfp-AXAB.npy", mmap_mode='r')
                
                lfp_aaab = lfp_aaab_full[:, start_ch:end_ch, :]; lfp_axab = lfp_axab_full[:, start_ch:end_ch, :]
                u_start = int(spk_aaab_full.shape[1] * (start_ch/128.0)); u_end = int(spk_aaab_full.shape[1] * (end_ch/128.0))
                spk_aaab = spk_aaab_full[:, u_start:u_end, :]; spk_axab = spk_axab_full[:, u_start:u_end, :]
                
                lfp_p1 = np.mean(lfp_aaab[:, :, 1000:1531], axis=1); lfp_p2 = np.mean(lfp_axab[:, :, 2031:2562], axis=1)
                
                fr_p1 = np.mean(spk_aaab[:, :, 1000:1531], axis=(0, 2))
                fr_p2 = np.mean(spk_axab[:, :, 2031:2562], axis=(0, 2))
                
                for u in range(spk_aaab.shape[1]):
                    if fr_p1[u] > 0.001: all_s.append({"score": fr_p1[u], "spk": spk_aaab[:, u, 1000:1531], "lfp": lfp_p1})
                    if fr_p2[u] > 0.001: all_o.append({"score": fr_p2[u], "spk": spk_axab[:, u, 2031:2562], "lfp": lfp_p2})
            except Exception: continue
            
        all_s.sort(key=lambda x: x["score"], reverse=True); all_o.sort(key=lambda x: x["score"], reverse=True)
        top_s = all_s[:20]; top_o = all_o[:20]
        
        if not top_s and not top_o: continue
        
        sub_spks = apply_subsampling([u["spk"] for u in top_s] + [u["spk"] for u in top_o])
        
        s_plvs = [get_plv_spectrum(top_s[i]["lfp"], sub_spks[i])[1] for i in range(len(top_s))]
        o_plvs = [get_plv_spectrum(top_o[i]["lfp"], sub_spks[len(top_s)+i])[1] for i in range(len(top_o))]
        freqs, _ = get_plv_spectrum(top_s[0]["lfp"], sub_spks[0]) if top_s else get_plv_spectrum(top_o[0]["lfp"], sub_spks[0])
        
        results[area] = {'freqs': freqs, 's_plus': s_plvs, 'o_plus': o_plvs}
    return results
