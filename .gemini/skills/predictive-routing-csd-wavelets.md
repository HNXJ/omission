# Skill: Predictive Routing CSD & Wavelets
**Description:** High-performance laminar alignment and spectral decomposition using CAX and JAX.
**When to use:** When analyzing linear probe LFP data to identify Layer 4 or extract time-frequency power with high throughput.

### Key Functions
- `compute_1d_csd`: Calculates the spatial Laplacian for Layer 4 identification.
- `compute_tfr_multiband`: JAX-vectorized Morlet wavelet engine for massive parallel spectral analysis.
- `subtract_erp`: Isolates induced power from phase-locked transients.

### Location
- `D:\Analysis\predictive_routing_2020\src\spectral_analysis\csd_mapper.py`
- `D:\Analysis\predictive_routing_2020\src\models\wavelet_engine_jax.py`
- `D:\Analysis\predictive_routing_2020\src\spectral_analysis\induced_power.py`
