---
name: study-eval-actions
description: Framework for evaluating research papers against a structured factor glossary. Includes the 36-factor TcGLO predictive coding glossary, AI-driven scoring, and multi-dimensional visualizations (3D scatter, 2D comparison).
---

# Study Evaluation Actions Skill

Consolidated framework for systematic research paper evaluation and comparative analysis.

## 1. Evaluation Domain: TcGLO Predictive Coding
Evaluates predictive coding mechanisms across three primary hypotheses (H1, H2, H3) and two contexts (LO, GO).

### Contexts
- **LO (Local Oddball)**: Short-term sensory deviance (adaptation-heavy).
- **GO (Global Oddball)**: Long-term/Sequence deviance (expectation-driven).

### Theory Groups (Hypotheses)
- **H1 — Suppression**: Predictive inhibition of surprise.
- **H2 — Propagation**: Feedforward error signal transmission.
- **H3 — Ubiquitousness**: Cross-scale and cross-area conservation.

## 2. Core Workflows

### A. Evaluating a Research Paper
1. **Extract Text**: Use `PyPDF2` or similar to extract full text from the PDF.
2. **Score Factors**: Map text evidence to the 36-factor glossary using AI scoring (-1.0 to +1.0, or NaN).
3. **Log Reasoning**: Capture the qualitative logic behind each score.

### B. Visualization & Analysis
- **3D Scatter Plot**: Visualize studies in the H1-H2-H3 space for a specific context.
- **2D Hypothesis Comparison**: Stacked subplots comparing LO vs. GO scores for each hypothesis.
- **Study-to-Study MSE**: Compare a target paper against the existing literature database using Mean Squared Error.
- **Agent Agreement**: Analyze consensus between different AI models (Agents).

## 3. Key Resources
- **Literature Database**: `/Users/hamednejat/workspace/HPC/HPC/Data/hpc_table_260225.csv`
- **Glossary Definition**: [glossary.json](references/glossary.json)
- **Detailed Reference**: [glossary-reference.md](references/glossary-reference.md)
- **Main Analysis Notebook**: `/Users/hamednejat/General/Works/4thYear/HPC/HPC/GLO_HPC_A.ipynb`

## 4. Usage Guidelines
- Always ensure context independence: Score LO and GO factors separately based on distinct evidence.
- Maintain standardized column naming: `{context}_{factor_name}`.
- Use `np.nan` for factors not addressed in the study.
