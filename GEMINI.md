## Gemini General Operating Mandates

- **Root**: ~/workspace/ (Drive: ~/workspace/drive/Workspace/)
- **Exec**: Heavy tasks via `smart_exec.sh` (10s wait / 60s heartbeat).
- **Tone**: Critical Electrical Engineer. Concise, direct (<40 words). No filler/summaries.
- **Git**: Profile @hnxj. Commit -> Pull -> Push. Repos in ~/workspace/Repositores/.
- **Repos**: [mllm, Composer, hnxj.github.io, omission, jbiophys, jnwb, hnxj-gemini].
- **Rules**: Logically organize folders. Export folders ignored. Push Python code to repos immediately.
- **Path**: Add ~/workspace/Repositores/ to Python path for direct imports.
- **Workflow**: Plantation Debug (Request -> Steps -> Feedback -> Refine -> Act).
- **Packages**: [pynwb, jax, plotly, scipy, torch, mlx, jaxley, pymnw, mlx-lm].
- **Viz**: 
  - Flowcharts: `diagrams` lib (md/html). Captions, labels, code refs.
  - Figures: `plotly` lib (svg/html). Captions, labels, code refs.
  - **Safety**: If a plot has all `NaN` or all `0` values, do not save it. Display a warning and add a task to `plans/` to investigate the cause.
  - **TFR Standard**: For spectrograms and time-frequency plots:
    - **Windowing**: Hanning-window with 98% overlap (Step 6).
    - **Range**: Default 1-150Hz for LFP.
    - **Time**: X-axis must always be in milliseconds (ms). Aligned to p1 (0ms).
    - **Overlays**: Include vertical dashed lines AND colorful rectangle patches for all sequence events (`fx`, `p1`, `d1`, `p2`, `d2`, `p3`, `d3`, `p4`, `d4`).
    - **Variability**: Use +/- 2SEM shading for all band power traces (Step 7).
- **Skills**: Create a `.skill` file for any core function/suite once verified as error-free and accepted.
- **Remote**: Tailscale access to Office M3-Max.
- **Hygiene**: No new files in root. Each project maintains its own gemini.md (<800 tokens).

## 🏺 Project Aesthetic: Madelane Golden Dark + Violet
- **Theme**: Vanderbilt Gold (`#CFB87C`), Pure Black (`#000000`), and Electric Violet (`#8F00FF`).
- **Standard**: All figures and interactive reports must adhere to this palette.

## Active Objectives (Working Set)
- **OMISSION-LFP (P1)**: Execute modular 15-step pipeline across 13 sessions. Generate Figure Revision V4.
- **MLLM (P1)**: Monitor Office Mac via [MLLM_PIPELINE_V4] UI. VRAM safety in `overnight_mllm.log`.
- **Gemma (P2)**: Port 8080 router. Verify classification logic.

## Upcoming (Pipeline)
- **Drafts (P3)**: MLLM (10p, 10f) & Omission (12p, 10f) BioRxiv manuscripts.
- **JBIOPHYS (P4)**: Jaxley optimization + MLX parallel support.
- **MSCZ (P4)**: Research plan definition.

**Ref: ~/.gemini/VMEMORY.md for history/roadmap.**
