# DIRECTIVE: PENDING_GEMINI_MASS_STATS
**Status**: PENDING AGENTIC ACTION
**Priority**: SOVEREIGN (GPA-PROTOCOL)
**Target**: Phase 1-3 (f001-f020)

## 1. Problem Statement
The current Core Hierarchy is structurally compliant (GPA 70) but scientifically "thin" (lack of statistical proof). Figures f004-f020 contain multi-condition data but do not report significance tiers, resulting in an Excellence GPA deficit.

## 2. Solution Architecture: Mass Statistical Injection
We will systematically refactor the analysis/plotting pipeline for all 20 core modules to enforce the **Significance-Tier Standard ($S_k$)**.

### A. Analysis Patch (inference.py)
Inject `scipy.stats` comparisons into the following modules:
- **f004 (Coding)**: Rank-sum between Target vs. Omission FR.
- **f005 (TFR)**: Permutation testing on Power heatmaps.
- **f007-f010 (SFC)**: Frequency-wise comparison of coherence.
- **f014-f015 (Granger)**: Bootstrapped causality significance.

### B. Plotting Patch (OmissionPlotter Integration)
Update all `plot.py` scripts to:
1. Import `get_significance_tier` from `src.analysis.stats.tiers`.
2. Update `OmissionPlotter(title=...)` to include the star-rating strings ($k*$).
3. Display full test parameters (p-value, test type, N-counts) in the subtitle.

## 3. Success Criteria (GPA 95+)
- [ ] 20/20 modules report valid p-values in `scoreboard.json`.
- [ ] Every figure title manifests a non-null significance tier ($S_k$ or n.s.).
- [ ] READMEs updated with methodology for the specific statistical tests used.

## 4. Execution Workflow
1. **Node Antigravity**: Perform mass source code refactor.
2. **Node Antigravity**: Execute Reproduction Run (Batch Phase 1-3).
3. **Node Gemini CLI**: Run Sentinel Audit V2 to verify GPA 95+.
4. **Human Review**: Visual QA of HTML figures in `Export_Staging`.
