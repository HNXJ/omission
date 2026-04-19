# beta
import numpy as np
import scipy.signal
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.analysis.lfp.sfc import select_top_units, get_matched_sfc_data

def analyze_cross_area_sfc(loader: DataLoader, src_area: str, tgt_area: str, condition="AXAB"):
    """
    Computes SFC between units in src_area and LFP in tgt_area.
    """
    log.info(f"Computing Cross-Area SFC: {src_area} (Units) -> {tgt_area} (LFP)")
    src_units = select_top_units(loader, src_area, mode="omission", top_n=5)
    
    # We need LFP from tgt_area for the SAME sessions/probes as src_units
    results = []
    for unit in src_units:
        # Load local unit and local LFP
        lfp_local, spk = get_matched_sfc_data(loader, unit)
        if lfp_local is None: continue
        
        # Load target LFP (same session, different area)
        # Use helper to get LFP for target area
        from src.analysis.lfp.lfp_pipeline import get_lfp_signal
        # This gets all sessions. We need session-matched.
        # For simplicity, let's assume we can get it from DataLoader mapping.
        mapping = [e for e in loader.area_map[tgt_area] if e["session"] == unit["session"]]
        if not mapping: continue
        
        entry = mapping[0]
        f_lfp = loader.data_dir / f"ses{unit['session']}-probe{entry['probe']}-lfp-{condition}.npy"
        if not f_lfp.exists(): continue
        
        lfp_full = np.load(f_lfp, mmap_mode='r')[:, entry["start_ch"]:entry["end_ch"], 2031:2562]
        lfp_tgt = np.mean(lfp_full, axis=1) # Target mean LFP
        
        # Coherence
        coh_trials = []
        for tr in range(lfp_tgt.shape[0]):
            f, Cxy = scipy.signal.coherence(lfp_tgt[tr], spk[tr], fs=1000, nperseg=256)
            coh_trials.append(Cxy)
        results.append(np.mean(coh_trials, axis=0))
        
    if results:
        return {
            "freqs": f,
            "coh_mean": np.mean(results, axis=0),
            "coh_sem": np.std(results, axis=0) / np.sqrt(len(results)),
            "pair": f"{src_area}->{tgt_area}"
        }
    return None
