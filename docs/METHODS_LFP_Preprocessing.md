## Methods: LFP Preprocessing

Local field potential (LFP) signals were extracted from the 30 kHz raw broadband data by applying a low-pass filter (cutoff 300 Hz) and downsampling to 1 kHz. 

### Bipolar Derivation
To isolate local oscillatory activity and reduce the influence of volume-conducted signals across cortical layers, we employed a bipolar derivation (nearest-neighbor laminar differencing). For a channel $i$, the bipolar LFP $L_{i, bipolar}$ was calculated as:
$$L_{i, bipolar} = L_i - L_{i+1}$$
This transformation effectively highlights local synaptic input and rhythm generation specific to the cortical depth, essential for inter-areal spectral comparison.

### Spectral Decomposition
All spectral analyses utilized moving-window spectrograms with high temporal overlap (~98%). Baseline normalization was applied at each frequency by computing the power relative to a late pre-omission delay baseline (-250 to -50 ms). Relative power change was quantified in decibels ($10 \cdot \log_{10}(P / P_{baseline})$). Canonical frequency bands were defined as:
- **Theta**: 4–8 Hz
- **Alpha**: 8–12 Hz
- **Beta**: 12–30 Hz
- **Low Gamma**: 40–60 Hz
- **High Gamma**: 60–100+ Hz

All spectral averages were computed at the session level before grand averaging across sessions to ensure consistency in population-level estimates.
