# core
import numpy as np
import scipy.signal
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log

def analyze_laminar_coherence(loader: DataLoader, session: str, probe: int, condition="AXAB"):
    """
    Computes iCOH matrix across 8 laminar depths.
    Focus band: Beta (13-30Hz)
    """
    log.info(f"Analyzing Laminar Coherence for Session {session}, Probe {probe}")
    
    f_lfp = loader.data_dir / f"ses{session}-probe{probe}-lfp-{condition}.npy"
    if not f_lfp.exists():
        log.warning(f"LFP file missing: {f_lfp}")
        return None
        
    lfp = np.load(f_lfp, mmap_mode='r')
    n_trials, n_ch, n_times = lfp.shape
    
    n_layers = 8
    ch_per_layer = n_ch // n_layers
    
    layer_signals = []
    for i in range(n_layers):
        sig = np.mean(lfp[:, i*ch_per_layer : (i+1)*ch_per_layer, :], axis=1)
        layer_signals.append(sig)
        
    win = slice(1031, 1562)
    fs = 1000.0
    
    # 2. Compute iCOH Matrix
    icoh_matrix = np.zeros((n_layers, n_layers))
    for i in range(n_layers):
        for j in range(n_layers):
            if i == j: 
                icoh_matrix[i, j] = 0.0
                continue
            
            s1 = layer_signals[i][:, win].flatten()
            s2 = layer_signals[j][:, win].flatten()
            
            f, Pxy = scipy.signal.csd(s1, s2, fs=fs, nperseg=256)
            f, Pxx = scipy.signal.welch(s1, fs=fs, nperseg=256)
            f, Pyy = scipy.signal.welch(s2, fs=fs, nperseg=256)
            
            # iCOH spectrum
            coh_spec = np.imag(Pxy) / np.sqrt(Pxx * Pyy)
            
            # Mean in Beta band (13-30Hz)
            beta_idx = (f >= 13) & (f <= 30)
            icoh_matrix[i, j] = np.mean(np.abs(coh_spec[beta_idx]))
            
    return {
        "icoh_matrix": icoh_matrix,
        "layers": [f"L{i+1}" for i in range(n_layers)]
    }
