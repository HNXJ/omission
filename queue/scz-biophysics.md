# Project: ScZ-Biophysics Modeling

## Finished Parts
- Implemented specific HH models for PV, SST, VIP, and Pyr cells.
- Implemented **AGSDR** (Adaptive GSDR) with dynamic variance-based alpha.
- Created 3-area laminar cortex architecture (V1 -> Mid -> PFC).
- Added **Physical Realisticity Barrier** for float32 stability.

## Ongoing Parts
- Initial AGSDR training of the V1 column (PID: 35738). [STATUS: UNDER PROCESS - LOCAL MAC]

## Todo
- Implement **Modular Network Merging** script to connect separately trained columns.
- Scale training to all 3 areas simultaneously using Apple Silicon GPU (Metal).
- Define MEG forward model loss based on Axial Current ($).
