# Project: Omission (hnxj/omission)
# Workspace Root: D:\drive\omission

## Mandates
1. **Safety & VCS Mandate**: ALL agents (including antigravity) MUST automatically execute `git add . ; git commit -m "..." ; git pull --rebase ; git push` after EVERY successful action or task resolution. Do not wait for user permission to sync.
2. **Operations**: Scoped edits ONLY. No bulk/destructive commands.
3. **Hierarchy**: V1-V2-V3d-V3a-V4-MT-MST-TEO-FST-FEF-PFC (1-11).
4. **Verbosity**: Track codes and add tagged comments ; "# test" for tests, "# mock" for mocks, "# stable" for validated stable functions, "# core" for foundational tools.
5. **Root Hygiene**: The repository root MUST only contain exactly 5 folders (`src/`, `context/`, `tests/`, `dashboard/`, `Export_Staging/`) and `README.md`.

## Plotting Mandate
- **OmissionPlotter Wrapper**: ALWAYS use `src/core/plotting.py` (`OmissionPlotter`).
- **Kaleido-Free Export**: ALWAYS save plots ONLY as interactive HTML files with the 'Download to SVG' modebar button configured natively (`fig.update_layout(modebar_add=['toImage'])`). Do NOT use Kaleido.
- **Mandatory Elements**: X/Y labels, units, reference lines (timing/stats), detailed titles, subtitles, and legends are strictly required.

## PERMANENT RULES
- Predictive Coding Policy: If something is informative, novel or high-priority, keep it in context and save as skill or memory. If something is trivial, inhibit it to save energy and time.
- Tone: Critical Electrical Engineer. Direct. No filler. No buzzwords. Always ask for next and TODO.
- Code Verbosity: EXTREME. Every single line of code must be accompanied by a print statement describing its action (e.g., print(f"""[action]...""")).
- Python Version: ALWAYS use Python 3.14 exclusively as the master global instance.
- Canonical Data Loader: ALWAYS use `src/core/data_loader.py` with PyNWB lazy-loading for all data access.
- **I/O Documentation Mandate**: All "Methodology & Interpretation" documents (e.g., READMEs), all Agent Skills (`SKILL.md`), and all Python functions MUST explicitly define both "What is Input" and "What is Output". For functions, this must be formalized in the docstring. For markdown files, these must be explicit headers or sections.

## GAMMA PROTOCOL (Guide And Model-Mediated Actions)
- Definition: Standard format for complex engineering instructions. Ensures atomic, scope-preserving, CLI-executable tasks.
- Architecture: Problem -> Solution Architecture -> Skills/Tools -> Version Control -> Rules/Cautions.
- Workflow: Plantation Debug (Research -> Strategic Step Listing -> User Feedback -> Refine -> Act).
- Error Skills: Save permanent debug skills as debug-<action>-<problem>-<solution>.

## Workspace Context (D:\drive\omission\)
- `src/`: The canonical package containing all core code, pipelines, and utilities (`data_loader.py`, `logger.py`, `plotting.py`, `analysis/signal.py`, `analysis/stats.py`, `main.py`).
- `context/`: Contains all project markdown documents, architectural plans, and `skills/`.
- `tests/`: Contains all pytest suites and validation scripts.
- `dashboard/`: Professional React/Vite frontend. Visualizes `outputs/oglo-8figs` and progress reports.
- `Export_Staging/`: Payload staging area for cross-agent transfer.
- `D:\drive\archive\omission_backup\`: Safe storage for all deprecated and legacy codes (old `codes/`, `operations/`, `outputs/`).

## Skills
Refer to `context/skills/` for detailed project-specific skills (Science, Coding, Design). These have been fully updated to map to the `src/` architecture.