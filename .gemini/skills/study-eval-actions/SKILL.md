---
name: study-eval-actions
---
# study-eval-actions

## Purpose
Evaluates research papers against the 36-factor TcGLO Predictive Coding glossary using multi-agent LLM scoring (DeepSeek, Qwen, Gemini).

## Scoring Domains
| Hypothesis | Focus | Key Factor IDs |
|------------|-------|-----------------|
| H1: Predictive Suppression | SST/PV inhibition, activity suppression | 1, 2, 6, 12 |
| H2: FF Error Propagation | AMPA, ascending Gamma, L2/3 activity | 14, 16, 18, 22 |
| H3: Ubiquity | Canonical microcircuit, cross-modal | 25, 30-32, 33 |

## Workflow
1. Extract text from PDFs (via `neuroscience-actions`)
2. Score 0.0-1.0 per factor with ensemble of LLMs
3. Consensus = mean, Certainty = 1 - variance

## Files
- [hpc_table_260225.csv] — Reference dataset
- [glossary-reference.md] — TcGLO factor definitions
