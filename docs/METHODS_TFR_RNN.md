## Methods: TFR Pipeline and RNN Modeling

### Time-Frequency Analysis
Spectral power was computed via moving-window spectrograms. Windows were sized at 200 ms with a 98% overlap (196 ms) to ensure smooth band-power trajectories. Baseline normalization was performed using the late pre-omission delay (-250 to -50 ms) as the reference, applying $10 \cdot \log_{10}(P / P_{baseline})$ to obtain decibel power changes.

### RNN Modeling
A Reservoir Computing RNN (Echo State Network) with 1000 hidden nodes was utilized. The reservoir was randomly initialized with a spectral radius of 0.95. Readout layers were trained using FORCE learning on AAAB and AXAB sequence structures, minimizing the mean squared error between the RNN output and empirical population firing rate averages.
