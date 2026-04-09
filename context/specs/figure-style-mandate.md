# OMISSION REPO FIGURE STYLE MANDATE
Version: repo-aware, p1-locked, publication-facing
Applies to: codes/functions/visualization/*, codes/scripts/analysis/*, poster/manuscript exports

Purpose: Scientifically faithful, visually consistent figures aligned to canonical timing/area conventions.

──────────────────────────────────────────────────────────────────────
A. SOURCE OF TRUTH AND CONFLICT RESOLUTION
──────────────────────────────────────────────────────────────────────
1. Primary Source: codes/functions/lfp/lfp_constants.py, codes/functions/visualization/poster_figures.py, codes/functions/events/lfp_events.py.
2. Canonical Constants: Never redefine core constants (area order, condition list, timing windows) locally.
3. Timing Axis: Always use p1-relative time (p1=0ms) on axes. Export-array indices are for internal logic only.
4. Conflicts: Prioritize lfp_constants.py and poster_figures.py over stale scripts.

──────────────────────────────────────────────────────────────────────
B. CANONICAL SEMANTICS
──────────────────────────────────────────────────────────────────────
1. Area Order: V1, V2, V3d, V3a, V4, MT, MST, TEO, FST, FEF, PFC.
2. Timing (p1=0ms):
   fx: -500-0, p1: 0-531, d1: 531-1031, p2: 1031-1562, d2: 1562-2062, p3: 2062-2593, d3: 2593-3093, p4: 3093-3624, d4: 3624-4124.
3. Timing Conversion: If using 6000-sample export (p1 at 1000), `ms = sample - 1000`.
4. Shapes: [Trial x Channel/Unit x Time].
5. Summary: Default to session-balanced averaging unless inferring on units/channels.

──────────────────────────────────────────────────────────────────────
C. STYLE RULES
──────────────────────────────────────────────────────────────────────
1. Legibility: Readable without text. Axis labels, units, panel labels, legends/direct labels required.
2. Typography: Arial/Helvetica, black text. No outline.
3. Contrast: No color-only encoding. Use line style, markers, or labels.
4. Minimalism: No clutter (gradients, bevels, 3D, chartjunk). Avoid gridlines unless essential.
5. Uncertainty: Must define (SEM, SD, CI). Label axes N (replicates) vs n (observations).
6. Statistical Reporting: Test, statistic, df, p, N, correction.
7. Smoothing: State kernel width and method if applied.
8. Color System: 
   - Neutral: Black/Gray/White.
   - Patch: p1=GOLD, p2=VIOLET, p3=TEAL, p4=ORANGE, Omission=PINK.
   - Condition: AAAB=blue, BBBA=vermillion, RRRR=gold.
   - Families: p2(violet), p3(teal), p4(orange).
   - Bands: Theta(Red), Alpha(Orange), Beta(Violet), Gamma(Gold).
9. Consistency: Never change color semantics across figures.

──────────────────────────────────────────────────────────────────────
D. IMPLEMENTATION
──────────────────────────────────────────────────────────────────────
1. Helpers: Reuse poster_figures.py helpers.
2. Multi-panel: Vertical stacks V1(top) to PFC(bottom) unless inverse justified.
3. Export: 
   - Plotly: HTML(QC), SVG/PDF(Pub).
   - Matplotlib: SVG/PDF(Pub).
4. No raw sample indices on axes. Always convert to p1-relative ms.
