# Neuroscience Writing: Statistical Reporting (R², Kappa, Shift)

Quantifying biological validity and model convergence through standardized metrics.

## 1. Synchrony Metrics (Kappa)
- **Calculation**: Use Fleiss' Kappa to quantify population-level spike synchrony.
- **Target**: Differentiate between **Baseline** vs. **Stimulus** synchrony.
- **Reporting**: Report Mean $\pm$ SEM across trials. Target $K < 0.1$ for biologically realistic asynchrony.

## 2. Spectral Trends (Shift)
- **Trend Line**: Apply Least Mean Squares (LMS) fit to trial-by-trial PSD peaks.
- **Total Shift**: Report the delta between the fit at the first and last trial (e.g., "$+2.5$ Hz Shift over 190 trials").
- **Goodness of Fit**: Include R² and p-values for all frequency drift claims.

## 3. Modeling Diagnostics
- **Convergence**: Report the loss trajectory and final loss value.
- **Adaptive Mix**: For AGSDR, report the final Alpha ($\alpha$) distribution to justify the supervised vs. unsupervised balance.
- **Firing Rates**: Ensure Average Firing Rate (AFR) remains within physiological bounds (e.g., 5-40 Hz for excitatory neurons).
