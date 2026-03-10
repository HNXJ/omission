# 🏺 Workspace Chandelier (Structural Overview)

## 1. Root Architecture (6 Pillars)
The workspace is organized into 6 primary categories to maximize navigation speed and structural clarity.

- **Analysis/**: Empirical data processing (NWB, EEG, MEG, etc.)
- **Computational/**: Biophysical modeling, library core, and ScZ project.
- **HNXJ/**: Administrative vault, portfolio (hnxj_gio), and Gemini bridge.
- **Repositories/**: Local mirrors of GitHub projects (AAE, GSDR).
- **Research_Assets/**: Publication drafts, media (figures/pdfs), and data exports.
- **misc/**: Temporary vault for root-level files.

## 2. Hierarchical Tree (Level 2)
```text
workspace/
├── Analysis/
│   ├── ecog/
│   ├── eeg/
│   ├── HPC/
│   ├── meg/
│   ├── misc/
│   └── nwb/
├── Computational/
│   ├── core_tools/ (jlmlx, lib)
│   ├── jbiophysics/
│   ├── jschizophrenia/
│   ├── media/
│   ├── misc/
│   ├── ScZ_Modeling/
│   └── src/
├── HNXJ/
│   ├── admin/ (docs, archive, office_mac_files)
│   ├── hnxj_gio/
│   ├── hnxj-gemini/ [EXEMPT]
│   ├── misc/
│   ├── new_skills/
│   └── skills/
├── Repositories/
│   ├── AAE/
│   ├── GSDR_repo/
│   ├── drive/
│   └── misc/
├── Research_Assets/
│   ├── _figures/
│   ├── drafts/
│   ├── media/
│   └── misc/
└── misc/
```

*Note: Every directory follows the 5-folder limit (excluding hnxj-gemini) and contains a 'misc/' vault.*
