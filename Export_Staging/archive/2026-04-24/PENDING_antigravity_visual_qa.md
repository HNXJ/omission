# Task: Comprehensive Visual QA & Grading of All Figures

**Target:** `antigravity`
**Priority:** High

## Objective
Please perform a rigorous visual inspection of all figures currently available in the dashboard (`localhost:5173`) and exported HTML files. We need to identify any visualization artifacts or quality degradations before final manuscript assembly.

## Audit Directives (Pass/Fail Grading)
For **every single figure** inspected, you must explicitly assign a status of **[PASS]** or **[FAIL]**, accompanied by either an approval justification or a detailed criticism.

You must flag any figure exhibiting the following issues as a **[FAIL]**:
1. **Noisy/Spaghetti Data:** Lines or trajectories that are visually chaotic or lack proper smoothing (e.g., unsmoothed PSTHs or PCA space).
2. **Empty/Missing:** Figures that fail to render, contain zero data, or show empty bounds.
3. **Excessive Whitespace:** Layouts where the plot area is cramped and surrounded by unnecessary empty space.
4. **Bad Formatting:** Improper scaling, squished aspect ratios, or UI overflow.
5. **Bad Labels/Legends:** Overlapping labels, cut-off text, massive legends taking up plot space, or unreadable font sizes.
6. **Factually Wrong:** Values outside physiological bounds, missing axes references, or flatlined data.
7. **Overall Low Quality:** Anything that does not meet the "Madelane Golden Dark" standard for publication readiness.

## Output Required
Please return a structured audit report with the following format for each figure:

### Figure ID: [Name/Number]
*   **Status:** `[PASS]` or `[FAIL]`
*   **Critique/Approval:** Provide a 1-2 sentence criticism of why it failed (referencing the criteria above), or a brief approval stating it meets the quality standards.
*   **Proposed Fix (If Failed):** Actionable technical steps to resolve the issue (e.g., "Add 50ms Gaussian smoothing to the traces", "Move legend to horizontal layout").

Include visual proof (screenshots) where possible, especially for critical failures. Do not skip any figures in your report.