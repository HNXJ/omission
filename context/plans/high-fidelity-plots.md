# Plan: High-Fidelity Omission Visualizations (Phase 3)

## 🎯 Objective
Generate a definitive set of publication-quality plots characterizing firing rates, MUA, variability, and causality across 11 brain areas and 4 specific omission conditions.

## 🛠️ Implementation Steps

### Phase 1: Condition-Specific Firing Rates (Task 1)
1. **Data Loading**: Load 3D arrays for RRRR, RXRR, RRXR, RRRX.
2. **Color Mapping**: 
   - RRRR: Brown
   - RXRR: Red
   - RRXR: Blue
   - RRRX: Green
3. **Stat Engine**: Compute Mean and SEM across all identified units per area.
4. **Plotting**: 11 figures (one per area) with 4 lines + SEM shades. Save as .html and .svg.

### Phase 2: MUA Activity Profiles (Task 2)
1. **Aggregation**: Sum/Average all spiking activity per probe to generate MUA traces.
2. **Analysis**: Repeat Phase 1 logic for MUA data.
3. **Plotting**: 11 figures. Save as .html and .svg.

### Phase 3: Neural Variability (Task 3)
1. **Algorithm**: Compute across-trial variance (time-resolved) for each area/condition.
2. **Stat Engine**: Compute SEM of the variance (bootstrapping or trial-grouping).
3. **Plotting**: 11 figures. Save as .html and .svg.

### Phase 4: Advanced Granger (Task 4)
1. **Selection**: Use Session 230818 (PFC-MT-MST) and 230831 (FEF-MT-MST).
2. **Causality**: Compute time-resolved Granger Causality using `nitime`.
3. **Visualization**: 
   - 4-subplot layout (Direction Graph, Strength-Time, Strength-Freq, Information Flow).
   - Save as .html and .svg.

## ✅ Verification
- Verify 11 area figures exist for Tasks 1, 2, and 3.
- Confirm color coding matches user specifications.
- Ensure Granger plots accurately reflect directionality and strength.
