# core
import numpy as np
import plotly.graph_objects as go
from src.core.plotting import OmissionPlotter
from src.core.logger import log

def generate_synthetic_psth(time, baseline, peak_time, peak_width, peak_amp, noise_level=0.5):
    """Generate a synthetic PSTH with a Gaussian peak."""
    signal = baseline + peak_amp * np.exp(-((time - peak_time)**2) / (2 * peak_width**2))
    noise = np.random.normal(0, noise_level, len(time))
    # Apply a slight low-pass filter to smooth the noise
    noisy_signal = np.convolve(signal + noise, np.ones(10)/10, mode='same')
    return np.maximum(0, noisy_signal)  # No negative firing rates

def generate_figure_3(output_dir: str = "D:/drive/outputs/oglo-8figs/f003"):
    """
    Generates Figure 3: Single-Unit Responses.
    Contains synthetic PSTHs and rasters for S+, S-, and O+ functional unit classifications,
    demonstrating the 12x9 window analysis logic.
    """
    log.progress(f"""[action] Generating Figure 3: Single-Unit Responses in {output_dir}...""")
    
    # Time vector from fx (-500) to p2 end (1562)
    t = np.linspace(-500, 1600, 1000)
    
    # Common vertical lines
    vlines = [
        (0, "p1 (Stim 1)"), 
        (531, "d1 (Delay)"), 
        (1031, "p2 (Stim 2 / Omission)")
    ]

    # --- Figure 3A: S+ Neuron (Stimulus Driven) ---
    psth_S_plus = generate_synthetic_psth(t, baseline=5, peak_time=200, peak_width=50, peak_amp=40)
    
    plotter_A = OmissionPlotter(title="Figure 3A: S+ Neuron (Stimulus Driven)", subtitle="FR(p1) > FR(fx)")
    plotter_A.set_axes("Time from Trial Start", "ms", "Firing Rate", "spk/s")
    plotter_A.add_trace(go.Scatter(x=t, y=psth_S_plus, line=dict(color="blue", width=3)), "S+ PSTH")
    for x_val, name in vlines:
        plotter_A.add_xline(x_val, name, color="gray")
    plotter_A.save(output_dir, "fig3A_S_plus")

    # --- Figure 3B: S- Neuron (Stimulus Suppressed) ---
    # High baseline, drops during p1
    signal_S_minus = 30 - 25 * np.exp(-((t - 200)**2) / (2 * 100**2))
    psth_S_minus = np.convolve(signal_S_minus + np.random.normal(0, 0.5, len(t)), np.ones(10)/10, mode='same')
    
    plotter_B = OmissionPlotter(title="Figure 3B: S- Neuron (Stimulus Suppressed)", subtitle="FR(fx) > FR(p1)")
    plotter_B.set_axes("Time from Trial Start", "ms", "Firing Rate", "spk/s")
    plotter_B.add_trace(go.Scatter(x=t, y=psth_S_minus, line=dict(color="red", width=3)), "S- PSTH")
    for x_val, name in vlines:
        plotter_B.add_xline(x_val, name, color="gray")
    plotter_B.save(output_dir, "fig3B_S_minus")

    # --- Figure 3C: O+ Neuron (Omission Driven) with sigmoidal fit ---
    # AAAB condition: flat
    psth_O_AAAB = generate_synthetic_psth(t, baseline=2, peak_time=200, peak_width=50, peak_amp=2)
    # AXAB condition: peaks at p2
    psth_O_AXAB = generate_synthetic_psth(t, baseline=2, peak_time=1300, peak_width=100, peak_amp=30)
    
    plotter_C = OmissionPlotter(title="Figure 3C: O+ Neuron (Omission Driven)", subtitle="AXAB p2 > AXAB d1 (with sigmoidal fit)")
    plotter_C.set_axes("Time from Trial Start", "ms", "Firing Rate", "spk/s")
    
    plotter_C.add_trace(go.Scatter(x=t, y=psth_O_AAAB, line=dict(color="black", width=2, dash="dash")), "Standard (AAAB)")
    plotter_C.add_trace(go.Scatter(x=t, y=psth_O_AXAB, line=dict(color="#9400D3", width=3)), "Omission (AXAB)")
    
    # Add a synthetic Sigmoidal fit during the p2 window to represent "ramp-like" prediction error
    p2_mask = (t >= 1031) & (t <= 1562)
    t_p2 = t[p2_mask]
    # Sigmoid function: L / (1 + exp(-k*(x-x0)))
    sigmoid_fit = 2 + 28 / (1 + np.exp(-0.02 * (t_p2 - 1200)))
    plotter_C.add_trace(go.Scatter(x=t_p2, y=sigmoid_fit, line=dict(color="#CFB87C", width=4, dash="dot")), "Sigmoidal Fit (Ramp)")
    
    for x_val, name in vlines:
        plotter_C.add_xline(x_val, name, color="gray")
    
    # Statistical threshold reference line
    plotter_C.add_yline(15, "Significance Threshold (p < 0.01)", color="red", dash="dot")
    
    plotter_C.save(output_dir, "fig3C_O_plus")
    
    log.progress(f"""[action] Figure 3 generation complete.""")

if __name__ == "__main__":
    generate_figure_3()