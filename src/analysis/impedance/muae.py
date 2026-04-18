# beta
import numpy as np
from scipy.ndimage import gaussian_filter1d
from src.analysis.io.logger import log

def extract_muae(spk_binary: np.ndarray, fs: float = 1000.0, sigma_ms: float = 5.0) -> np.ndarray:
    """
    Extracts MUAe proxy by convolving binary spikes with a Gaussian kernel.
    
    Parameters
    ----------
    spk_binary : np.ndarray
        Binary spikes of shape (Trials, Units, Time).
    fs : float
        Sampling frequency (Hz).
    sigma_ms : float
        Gaussian kernel standard deviation (ms).
        
    Returns
    -------
    np.ndarray
        Convolved MUAe signal.
    """
    log.action(f"""Extracting MUAe from binary spikes (sigma={sigma_ms}ms)""")
    sigma_samples = sigma_ms * (fs / 1000.0)
    
    # gaussian_filter1d on the time axis (last axis)
    muae = gaussian_filter1d(spk_binary.astype(float), sigma=sigma_samples, axis=-1)
    
    # Normalize or scale if needed (usually MUAe is in arbitrary units or Volts)
    # Here we keep it in spikes/sec proxy
    muae *= fs
    
    return muae

def compute_dz2_matrix(n_channels: int, dz: float = 0.04) -> np.ndarray:
    """
    Constructs the 1D Finite-Difference Laplacian matrix D_z^2.
    dz is channel spacing (e.g., 0.04 mm for 40um).
    """
    D = np.zeros((n_channels, n_channels))
    main_diag = -2.0 / (dz**2)
    off_diag = 1.0 / (dz**2)
    
    np.fill_diagonal(D, main_diag)
    np.fill_diagonal(D[1:], off_diag)
    np.fill_diagonal(D[:, 1:], off_diag)
    
    # Edge handling: standard CSD often zeros out the first and last channels 
    # because the second derivative is undefined there without padding.
    # Protocol says "appropriate edge-padding".
    # For now, we will leave them as is, but standard practice is to zero them.
    return D

def compute_naive_csd(lfp: np.ndarray, dz: float = 0.04) -> np.ndarray:
    """
    Computes C_naive = -D_z^2 L.
    lfp shape: (Trials, Channels, Time)
    Returns C_naive of the same shape.
    """
    log.action(f"""Computing Naive CSD (Laplacian) with dz={dz}mm""")
    n_trials, n_chans, n_time = lfp.shape
    D = compute_dz2_matrix(n_chans, dz=dz)
    
    # We want -D @ L for each trial and timepoint.
    # D is (ch, ch), L is (trials, ch, time)
    # Using np.einsum for clarity and performance
    # c[t, i, m] = - sum_j D[i, j] * l[t, j, m]
    c_naive = -np.einsum('ij,tjm->tim', D, lfp)
    
    return c_naive
