---
name: study-eval-actions
description: Framework for evaluating research papers against the 36-factor TcGLO Predictive Coding glossary. Includes AI-driven scoring and consensus mapping.
---

# Study Eval Actions Skill

This skill guides the systematic evaluation of neuroscience literature using the **TcGLO (Predictive Coding) Glossary**.

## 1. The TcGLO Glossary (36 Factors)
Evaluations are performed across three core biophysical hypotheses:

### H1: Predictive Suppression (Mechanisms of Expectation)
- Focus: How predictable stimuli are dampened via inhibition.
- Key IDs: 1 (SST), 2 (PV), 6 (Activity Suppression), 12 (Omission Response).

### H2: Feedforward Error Propagation (Surprise Transmission)
- Focus: The generation and ascending flow of prediction errors.
- Key IDs: 14 (AMPA), 16 (Ascending Gamma), 18 (L2/3 Activity), 22 (Latency Shift).

### H3: Ubiquity (Universal Motifs)
- Focus: Consistency across areas, modalities, and species.
- Key IDs: 25 (Canonical Microcircuit), 30-32 (V1/V4/PFC Presence), 33 (Cross-Modal).

## 2. Multi-Agent Scoring Workflow
1. **Extraction**: Extract text evidence from PDFs (via `neuroscience-actions`).
2. **Evaluation**: Deploy an ensemble of LLMs (DeepSeek, Qwen, Gemini) to score the paper (0.0 to 1.0) against each of the 36 factors.
3. **Consensus**: Calculate the mean score across agents to determine the "Consensus Score."
4. **Certainty**: Calculate the variance between agents to determine the "Certainty Index."

## 3. Reference Data
- **Dataset**: `General/Works/4thYear/HPC/HPC/hpc_table_260225.csv`.
- **Glossary Details**: See `HPC/Skills/study-eval-neuro/glossary-reference.md`.
