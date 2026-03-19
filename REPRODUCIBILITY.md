# Omission Project Reproducibility Index

This document maps all figures and key analytical checkpoints to the Python scripts that generate them.

## 📊 Behavioral & Classification Suite (Step 1)
| Artifact | Description | Generating Script |
| :--- | :--- | :--- |
| **FIG_01** | Pupil Identity Decoding (A vs B) | `scripts/run_figure_01_classification.py` |
| **FIG_02** | Omission Detection (Pupil vs Combined) | `scripts/run_figure_02_classification_combined.py` |
| **FIG_03** | Neural Decoding (Identity & Omit) | `scripts/run_figure_03_classification_neural.py` |
| **FIG_04** | Oddball Effect (P4 vs P2/P3) | `scripts/run_figure_04_oddball_decoding.py` |

## 🧬 Population Dynamics & Stability (Step 2)
| Artifact | Description | Generating Script |
| :--- | :--- | :--- |
| **FIG_07** | MMFF Quenching & Stability | `scripts/plot_mmff_hierarchy.py` |
| **FIG_FR** | Firing Rate Stats | `scripts/plot_firing_rates_full_stats.py` |

## 🌀 Manifolds & Functional Categories (Step 3)
| Artifact | Description | Generating Script |
| :--- | :--- | :--- |
| **FIG_05** | PCA/UMAP/tSNE Manifolds | `scripts/plot_manifold_suite.py` |
| **FIG_05_V2** | Manifolds with Centroids | `scripts/plot_manifold_suite.py` |
| **Latencies** | Surprise Latency Hierarchy | `scripts/run_surprise_latency_hierarchy.py` |

## 🔗 Multi-Scale Connectivity (Step 4)
| Artifact | Description | Generating Script |
| :--- | :--- | :--- |
| **FIG_06** | V1-PFC Directionality (CCG/Granger) | `scripts/run_figure_06_directionality.py` |
| **FIG_09** | LFP Spectrograms | `scripts/run_lfp_spectrograms.py` |
| **FIG_10** | Theta-Gamma PAC | `scripts/run_lfp_pac.py` |
| **FIG_11** | Inter-Area Gamma Coherence | `scripts/run_lfp_coherence.py` |

## 🛠️ Core Utilities & Metadata
| Artifact | Description | Generating Script |
| :--- | :--- | :--- |
| **VFlip3** | Spectro-laminar Mapping | `scripts/vflip2_mapping_v3.py` |
| **Categories** | Neuron Classification | `scripts/classify_neurons_paper.py` |
| **Decoding Ind** | Individual Unit/LFP Decoding | `scripts/run_individual_decoding.py` |

---
*All scripts are located in the `scripts/` directory. Modular utility functions are stored in `functions/`.*
