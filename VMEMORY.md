# VMEMORY: Analytical Evolution & Methodology Standards

## 🧠 Core Methodology (The 4-Pillar Pipeline)

### Pillar 1: Spiking Dynamics & Decoding
- **Logic**: Identify the "Neural Surprise" latency and information content (Identity vs Context).
- **Standards**: 50ms sliding window, SVM (Linear) 5-fold cross-validation, 1000ms pre-stimulus alignment.
- **Key Finding**: PFC leads V1 in surprise detection by ~38ms.

### Pillar 2: Spectral Field Coordination
- **Logic**: Quantify regional field changes and functional connectivity.
- **Standards**: Hanning-window TFR, 98% overlap, 1-150Hz range.
- **Normalization**: Relative dB change $10 \times \log_{10}(P / P_{baseline})$ using serial delay windows (~1531ms window surrounding omission).

### Pillar 3: Multi-Scale Representational Geometry (RSA/CKA)
- **Logic**: Bridge heterogeneous modalities (LFP vs Spikes) and contexts (Stimulus vs Omission).
- **Standards**: Linear Centered Kernel Alignment (CKA) for second-order similarity. 11x11 Area matrices with bicubic upsampling (`zsmooth='best'`).
- **Contexts**: Delay, Omission, Stimulus, and All-Time profiles.

### Pillar 4: Behavioral Precision Scaling
- **Logic**: Direct audit of the internal model via oculomotor stabilization.
- **Standards**: Raw BHV (.mat) source for maximum DVA precision.
- **Metrics**: XY Variance, Microsaccade density, and high-frequency jitter within the omission window.

## 🏺 Aesthetic & Technical Mandates
- **Theme**: Madelane Golden Dark (#CFB87C, #000000, #8F00FF).
- **Vault**: Structured in `figures/part01/`. Traceability via `FIGURE_LOG.md`.
- **Safety**: Never save empty (NaN/0) plots; log investigation task immediately.
- **Skills**: Treat `.skill` files as "Delta-Only" expert instructions, modularized by functional domain.

---
*Updated: March 24, 2026 | Analytical Hierarchy Hardened.*
