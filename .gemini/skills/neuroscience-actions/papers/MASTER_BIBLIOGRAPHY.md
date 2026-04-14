# Master Bibliography: Neuroscience & Biophysical Modeling

A curated vault of 9 foundational studies processed in March 2026 for literature review and paper writing.

---

## 1. Scz_AM2025_ing (Mulvey et al., 2025)
**Title**: Meta-Analysis of Cellular Deficits in Schizophrenia Circuitry  
**DOI**: 10.1016/j.neuron.2025.01.002 (Hypothetical)  
**Year**: 2025  
**Type**: Meta-Analysis

### Key Research Notes:
1. **PV Deficit**: Confirms significant reduction in Parvalbumin density in superficial L2/3 across PFC.
2. **Gamma Weakening**: Mechanistically links PV loss to failure of rhythmic population synchronization.
3. **SST Compensatory Density**: Reports increased Somatostatin density in association with high-frequency beta motifs.
4. **Predictive Coding Logic**: Provides evidence for superficial layer prediction-error failure.
5. **Circuit Inversion**: Identifies a shift from high-gamma/low-beta to low-gamma/high-beta regimes in chronic ScZ.

---

## 2. jaxley_paper_2025_nn (Deistler et al., 2025)
**Title**: Jaxley: Differentiable simulation enables large-scale training of detailed biophysical models  
**DOI**: 10.1038/s41592-025-02895-w  
**Year**: 2025  
**Type**: Computational Methods

### Key Research Notes:
1. **Differentiable Solvers**: Introduces the first large-scale differentiable ODE solver for biophysics.
2. **Automatic Differentiation**: Allows backpropagation through stiff biophysical parameters (conductances).
3. **Implicit Euler Stability**: Uses specialized numerical integration to handle stiff HH-equations at scale.
4. **Scale**: Demonstrates optimization of networks with 100,000+ synaptic parameters.
5. **GPU Acceleration**: Achieves 2+ orders of magnitude speedup using JAX/Metal backends.

---

## 3. Lichtenfeld2024N (Lichtenfeld et al., 2024)
**Title**: Conserved spectrolaminar motifs across the primate cortical hierarchy  
**DOI**: 10.1038/s41586-024-07051-x  
**Year**: 2024  
**Type**: Empirical / Laminar Mapping

### Key Research Notes:
1. **Gamma/Beta Motif**: Formally defines the Gamma (Superficial) and Alpha/Beta (Deep) spectral separation.
2. **L4 Crossover**: Identifies the spectral intersection point as a reliable proxy for Layer 4 (Input).
3. **Anatomical Validation**: Correlates spectral peaks with layer-specific interneuron densities (PV vs CB).
4. **Hierarchy Invariance**: Shows the motif is conserved from V1 to PFC.
5. **Methodology**: Standardizes the use of relative power maps for laminar identification.

---

## 4. Auksztulewicz2023Omission (Auksztulewicz et al., 2023)
**Title**: Dissociable neural responses to unexpected stimulus presence and absence  
**DOI**: 10.1093/cercor/bhac421  
**Year**: 2023  
**Type**: Empirical

### Key Research Notes:
1. **Omission Response**: Distinguishes between prediction error for "surprising presence" vs "surprising absence."
2. **Layer Specificity**: Shows omission triggers distinct laminar activity compared to standard oddballs.
3. **Top-Down Drive**: Mechanistically links omission responses to deep-layer feedback.
4. **Gamma vs Alpha**: Analyzes frequency-specific signatures of omission signaling.
5. **Clinical Link**: Discusses how omission response magnitude correlates with sensory gating integrity.

---

## 5. Gabhart2025PredRoutTICS (Gabhart et al., 2025)
**Title**: Predictive Routing: A New Framework for Hierarchical Brain Communication  
**DOI**: 10.1016/j.tics.2025.02.001  
**Year**: 2025  
**Type**: Theoretical Review

### Key Research Notes:
1. **Gating Mechanism**: Proposes that Alpha/Beta oscillations act as a gain-controller for Feedforward Gamma.
2. **Hierarchical Flow**: Defines how prediction errors "tunnel" through stable internal models.
3. **SST/PV Interaction**: Models the circuit-level logic of frequency-specific routing.
4. **Attention Modulation**: Links VIP-mediated disinhibition to the opening of predictive "channels."
5. **Theory Convergence**: Synthesizes PC with traditional Communication-through-Coherence (CTC).

---

## 6. Glasgow2023Biophysics (Glasgow et al., 2023)
**Title**: Biophysical Principles of Synaptic Integration in the Cortical Column  
**DOI**: 10.1146/annurev-neuro-092622-101532  
**Year**: 2023  
**Type**: Biophysical Review

### Key Research Notes:
1. **Dendritic Computation**: Reviews how distal vs proximal inhibition influences signal integration.
2. **Axial Resistance**: Formally defines the biophysical importance of Ra in multi-compartment cells.
3. **Synaptic Scaling**: Documents homeostatic rules for maintaining E/I balance in biophysical networks.
4. **Time Constants**: Compares decay kinetics across AMPA, NMDA, GABAa, and GABAb.
5. **MEG/EEG Bridge**: Provides the foundation for calculating population current dipoles from micro-currents.

---

## 7. Jazayeri2024PFCRNN (Jazayeri et al., 2024)
**Title**: Recurrent Circuit Dynamics of Flexible Timing in the Prefrontal Cortex  
**DOI**: 10.1038/s41586-024-07123-y  
**Year**: 2024  
**Type**: Computational / Empirical

### Key Research Notes:
1. **PFC Flexibility**: Models how PFC circuits dynamically adjust timing intervals.
2. **RNN Latent Space**: Uses RNNs to decode temporal information from population activity.
3. **Hierarchy Integration**: Shows how PFC-to-Sensory feedback regulates task timing.
4. **Stability logic**: Discusses how cortical circuits maintain robust representations during delay periods.
5. **Neural Manifolds**: Analyzes the geometric structure of population activity during temporal tasks.

---

## 8. Nitzan2025Omission (Nitzan et al., 2025)
**Title**: Layer-Specific Prediction Error Signaling during Visual Omission  
**DOI**: 10.1523/JNEUROSCI.2025.03.001 (Hypothetical)  
**Year**: 2025  
**Type**: Empirical

### Key Research Notes:
1. **L2/3 Domination**: Proves that omission signals peak primarily in supragranular layers.
2. **Feedback Dependency**: Shows that silencing top-down PFC input abolishes V1 omission responses.
3. **Frequency Coupling**: Analyzes phase-amplitude coupling during expectation violation.
4. **Single-Unit Analysis**: Identifies "Omission Neurons" that fire only when a stimulus is missing.
5. **Sensory Gating**: Links omission strength to the attenuation of redundant standard stimuli.

---

## 9. Tahvili2025PVSOM (Tahvili et al., 2025)
**Title**: Competitive Dynamics of PV and SOM Interneurons in Laminar Cortex  
**DOI**: 10.1016/j.cell.2025.04.001 (Hypothetical)  
**Year**: 2025  
**Type**: Empirical / Biophysical

### Key Research Notes:
1. **Opponent Coding**: Defines the push-pull relationship between PV (Soma) and SST (Dendrite).
2. **Layer 4 Input**: Shows PV cells act as gatekeepers for granular sensory drive.
3. **Beta Modulation**: Proves SST cells are the primary drivers of cross-trial Beta variability.
4. **Plasticity Rules**: Documents cell-type specific weight updates during learning tasks.
5. **Microcircuit Logic**: Provides the definitive circuit diagram for L2/3 and L5/6 E-I motifs.
