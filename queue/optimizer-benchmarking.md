# Project: Optimizer-Benchmarking

## Finished Parts
- Refactored `AAE.gsdr.optimizers` to include **EMA-smoothed variance** for AGSDR.
- Implemented **Efficient Reset ('Reset + Step')** logic in both GSDR and AGSDR.
- Created a 10-neuron validity test network (8E, 2I) targeting 20Hz AFR and 0 Kappa.

## Ongoing Parts
- 1000-trial comparative sweep (GSDR vs AGSDR) on local M1 Max. [STATUS: UNDER PROCESS - LOCAL MAC]

## Todo
- Analyze final comparison plot (`gsdr_vs_agsdr_1000trials.png`).
- Benchmark speed improvements using Apple Silicon GPU (Metal) via `lax.scan` refactoring.
- Expand benchmark to multi-area (300+ neurons) networks.
