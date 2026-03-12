# Research Summary: Neural Mechanisms of Predictive Processing (OpenScope)
**Source**: Aizenbud, Audette, Bastos, ..., Nejat, et al. (2025). *Neural mechanisms of predictive processing: a collaborative community experiment through the OpenScope program.*

## 1. Executive Overview
This collaborative review provides a comprehensive synthesis of the current state of predictive processing (PP) research, bridging the gap between theoretical frameworks and experimental implementation. It establishes a set of "computational primitives" and identifies critical knowledge gaps that prevent a unified understanding of how the brain generates and updates statistical expectations. The work culminates in a detailed experimental proposal to be carried out through the Allen Institute's OpenScope program, utilizing standardized NWB data formats for community-wide model validation.

## 2. Key Computational Primitives
The paper identifies six biophysical pillars that sustain predictive processing in the sensory cortex:
1. **Stimulus Adaptation**: Local mechanisms that reduce responses to redundant inputs.
2. **Dendritic Computation**: The role of apical dendrites in integrating top-down feedback and bottom-up sensory drive.
3. **E/I Balance**: The interplay between excitatory neurons and inhibitory subtypes (PV, SST, VIP) in gating signal propagation.
4. **Hierarchical Processing**: The multi-scale flow of information from primary sensory areas to high-order association cortex.
5. **Recurrent Connectivity**: Local and long-range loops that maintain the internal model of the world.
6. **Synaptic Plasticity**: The rules (e.g., STDP, BTSP) by which prediction errors drive model updates.

## 3. Convergences and Theoretical Conflicts
While the field agrees on the involvement of top-down feedback and interneuron diversity, several significant conflicts remain:
* **Laminar Specificity**: There is no consensus on which layers (L2/3 vs. L5) are the primary loci of prediction error computation. Rodents show a shallower hierarchy than primates, raising questions about the scalability of certain models.
* **Mechanism Generality**: It remains unclear if different forms of mismatch (sensory, motor, omission) rely on a single unified circuit algorithm or distinct, specialized mechanisms.
* **Interpretation of Oscillations**: The role of specific frequency bands (Gamma for error, Alpha/Beta for prediction) is supported by some studies but challenged by others, particularly concerning their dependence on local spiking activity.

## 4. The OpenScope Roadmap
The authors propose a standardized community experiment to resolve these conflicts. By recording from V1, LM, and PFC using both Neuropixels and two-photon imaging, the study aims to compare responses to multiple mismatch types in the same animal. This dataset will enable researchers to test whether prediction errors are "additive," "subtractive," or "multiplicative" and to validate mechanistic models (like the "cellular" vs. "dendritic" hypotheses).

## 5. Clinical and Pathological Implications
The review highlights how PP failure provides a powerful framework for understanding neuropsychiatric disorders. Schizophrenia, in particular, is linked to the dysfunction of SOM (SST) neurons and the disruption of corollary discharge, leading to an imbalance between top-down internal models and bottom-up sensory evidence. This provides a formal biophysical basis for the "ScZ-51" glossary and the hierarchical modeling objectives of the mscz project.

## 6. Synthesis for the mllm Project
For the "Wisdom of Crowd" (mllm) project, this paper serves as the definitive reference for the TcGLO glossary. It codifies the formal definitions of "Computation," "Internal Model," and "Precision-Weighting" that our multi-agent ensemble uses to score the literature. The inclusion of co-author Hamed Nejat underscores the project's direct lineage from this community effort to our current algorithmic meta-analysis framework.
