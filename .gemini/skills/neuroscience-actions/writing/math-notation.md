# Neuroscience Writing: Mathematical Notation & Formulas

Ensuring consistency in formal biophysical definitions.

## 1. Morphological Coupling (Axial Current)
Formally define the MEG source approximation:
$$ I_a = \frac{V_{dendrite} - V_{soma}}{r_a} $$
Where:
- $I_a$ is the axial current.
- $V_{d}$ and $V_{s}$ are dendritic and somatic voltages.
- $r_a$ is the axial resistance.

## 2. Gating Dynamics (Hodgkin-Huxley)
Use standard notation for state updates:
$$ \frac{dv}{dt} = - \frac{1}{C_m} \left( \sum I_{channels} + \sum I_{synapses} - I_{ext} \right) $$
Specify the solvers used for these stiff ODEs (e.g., Implicit Euler).

## 3. Optimization Logic (AGSDR)
Formally define the mixing parameter $\alpha$:
$$ \theta_{t+1} = \theta_t + \lambda \cdot [ \alpha \cdot \delta_{unsupervised} + (1 - \alpha) \cdot \delta_{supervised} ] $$
Where $\delta$ represents the update variance from each pathway.
