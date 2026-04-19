# beta
import os
import numpy as np
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.analysis.impedance.muae import extract_muae
from src.analysis.impedance.estimation import estimate_impedance_tensor

def analyze_impedance(loader: DataLoader, session="230629", probe=0, condition="AAAB"):
    """
    Estimates the complex impedance tensor Z_eff(f, z).
    """
    lfp_path = loader.data_dir / f"ses{session}-probe{probe}-lfp-{condition}.npy"
    spk_path = loader.data_dir / f"ses{session}-units-probe{probe}-spk-{condition}.npy"
    
    if not lfp_path.exists() or not spk_path.exists():
        return None
        
    lfp = np.load(lfp_path, mmap_mode='r')
    spk = np.load(spk_path, mmap_mode='r')
    
    n_chans = lfp.shape[1]
    n_units = spk.shape[1]
    
    # Proxy: Bin units into channels
    spk_ch = np.zeros((spk.shape[0], n_chans, spk.shape[2]))
    unit_to_ch = np.linspace(0, n_chans-1, n_units).astype(int)
    for u in range(n_units):
        spk_ch[:, unit_to_ch[u], :] += spk[:, u, :]
        
    muae = extract_muae(spk_ch, fs=1000.0)
    z_eff, freqs = estimate_impedance_tensor(lfp, muae, fs=1000.0, dz=0.04)
    
    return {
        'z_eff': z_eff,
        'freqs': freqs,
        'depths': np.arange(n_chans) * 0.04,
        'session': session,
        'probe': probe
    }
