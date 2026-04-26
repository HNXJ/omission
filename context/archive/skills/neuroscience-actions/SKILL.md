---
name: neuroscience-actions
---
# neuroscience-actions

## Purpose
Biophysical modeling knowledge base: PING/ING mechanisms, E/I balance (75E/25I), laminar motifs (Markov 2014), interneuron dynamics, literature extraction.

## Key Constants
| Parameter | Value |
|-----------|-------|
| E:I ratio | 75% Excitatory : 25% Inhibitory |
| FF pathway | Superficial → target L4/Soma |
| FB pathway | Deep → target L1/Dendrites |
| PV cells | Drive Gamma (30-80 Hz) |
| SST cells | Modulate Beta (15-25 Hz) |
| Vm bounds | [-120, +60] mV |

## Example
```python
# Axial current (primary MEG source)
ia = (v_distal - v_soma) / ra
# PING: E-cells drive PV, PV inhibits E rhythmically → Gamma
```

## Files
- [circuits.py](file:///D:/drive/omission/src/neuro/circuits.py) — 11-area circuit definitions
