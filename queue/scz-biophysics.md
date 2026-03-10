# Project: ScZ-Biophysics Modeling

## Finished Parts
- Implemented specific HH models for PV, SST, VIP, and Pyr cells.
- Implemented **AGSDR** (Adaptive GSDR) with dynamic variance-based alpha.
- Created 3-area laminar cortex architecture (V1 -> Mid -> PFC).
- Added **Physical Realisticity Barrier** for float32 stability.

## Ongoing Parts
- Initial AGSDR training of the V1 column (PID: 37567). [STATUS: UNDER PROCESS - LOCAL MAC]
- Fixed **sparse_connect** signature and registered synaptic conductances as trainable parameters.

## Todo
- Implement **Hierarchical Multiplicative Scaling**: Apply $g_{syn}^{(i)} = g_{syn}^{base} \cdot (1 \pm \delta \cdot H_i)$ where $H_i$ is hierarchy depth (V1=0, PFC=1).
- Implement **Leaky VIP Gate**: Reduce VIP $\to$ SST conductance by 35% in ScZ state.
- Implement **Multi-Area Connectivity**: 
  - Feedforward: L2/3 -> L4.
  - Feedback: L6 -> L1 & L6.
- Refine MEG Dipole Loss: Transition from simple axial current to vertical position-weighted sum of all transmembrane currents.
- Implement **Modular Network Merging** script to connect separately trained columns.
- Scale training to all 3 areas simultaneously using Apple Silicon GPU (Metal).

