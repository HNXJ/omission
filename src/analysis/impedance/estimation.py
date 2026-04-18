# beta
import jax
import jax.numpy as jnp
import numpy as np
from src.analysis.io.logger import log

def compute_dz2_jax(n_channels: int, dz: float = 0.04):
    """JAX version of the Laplacian matrix."""
    main_diag = -2.0 / (dz**2)
    off_diag = 1.0 / (dz**2)
    
    D = jnp.diag(jnp.full(n_channels, main_diag))
    D = D + jnp.diag(jnp.full(n_channels - 1, off_diag), k=1)
    D = D + jnp.diag(jnp.full(n_channels - 1, off_diag), k=-1)
    return D

@jax.jit
def compute_csd_batch(s_batch, c_batch):
    """
    Computes Psc and Pss for a batch of windows.
    s_batch: (n_windows, n_channels, n_fft)
    c_batch: (n_windows, n_channels, n_fft)
    """
    s_fft = jnp.fft.rfft(s_batch, axis=-1)
    c_fft = jnp.fft.rfft(c_batch, axis=-1)
    
    # Cross-spectral density: S * C_conj
    psc = s_fft * jnp.conj(c_fft)
    # Auto-spectral density: S * S_conj
    pss = s_fft * jnp.conj(s_fft)
    
    # Average over windows
    psc_mean = jnp.mean(psc, axis=0)
    pss_mean = jnp.mean(pss, axis=0)
    
    return psc_mean, pss_mean

def estimate_impedance_tensor(
    lfp: np.ndarray, 
    spk_muae: np.ndarray, 
    fs: float = 1000.0, 
    dz: float = 0.04,
    nperseg: int = 512,
    noverlap: int = 256
):
    """
    Core Wiener-Hopf estimator for effective impedance Z_eff.
    
    Parameters
    ----------
    lfp : np.ndarray
        (Trials, Channels, Time)
    spk_muae : np.ndarray
        (Trials, Channels, Time) - MUAe proxy
    fs : float
        Sampling rate.
    dz : float
        Channel spacing (mm).
        
    Returns
    -------
    Z_eff : jnp.ndarray
        Complex impedance tensor (Channels, Frequencies)
    freqs : np.ndarray
        Frequency axis.
    """
    log.action(f"""Estimating Impedance Tensor (Z_eff) via JAX-accelerated Wiener-Hopf""")
    
    n_trials, n_chans, n_time = lfp.shape
    D = compute_dz2_jax(n_chans, dz=dz)
    
    # Convert to JAX arrays
    L = jnp.array(lfp)
    S = jnp.array(spk_muae)
    
    # Compute naive current source C = -D @ L
    # L is (trials, channels, time)
    C = -jnp.einsum('ij,tjm->tim', D, L)
    
    # Windowing for Welch's method
    # Flatten trials and time if needed, or process trial-by-trial
    # Let's reshape to (N_windows, Channels, nperseg)
    def segment_signal(x, nperseg, noverlap):
        step = nperseg - noverlap
        n_windows = (x.shape[-1] - noverlap) // step
        windows = []
        for i in range(n_windows):
            start = i * step
            windows.append(x[..., start:start+nperseg])
        return jnp.stack(windows, axis=0) # (n_windows, trials, channels, nperseg)

    S_win = segment_signal(S, nperseg, noverlap)
    C_win = segment_signal(C, nperseg, noverlap)
    
    # Flatten windows and trials into a single batch dimension
    S_flat = S_win.reshape(-1, n_chans, nperseg)
    C_flat = C_win.reshape(-1, n_chans, nperseg)
    
    # Apply Hanning window
    window = jnp.hanning(nperseg)
    S_flat = S_flat * window
    C_flat = C_flat * window
    
    # Compute spectral densities
    psc, pss = compute_csd_batch(S_flat, C_flat)
    
    # Z_eff = Psc / Pss
    # Add epsilon to avoid division by zero
    z_eff = psc / (pss + 1e-12)
    
    freqs = np.fft.rfftfreq(nperseg, d=1.0/fs)
    
    return z_eff, freqs
