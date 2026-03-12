# 🏺 Workspace Chandelier (Structural Overview)

## 1. Root Architecture (6 Pillars)
The workspace is organized into 6 primary pillars to maximize navigation speed and structural clarity.

- **Analysis/**: Empirical data processing, research assets, and NWB data.
- **Computational/**: Biophysical modeling (jbiophysics, mscz, mllm) and core tools.
- **drive/**: Synced Google Drive (ReadOnly and Workspace folders).
- **HNXJ/**: Administrative vault, portfolio, media, and Gemini bridge.
- **Repositories/**: Local mirrors of GitHub projects (AAE, GSDR, jbiophys).
- **misc/**: Temporary vault for root-level files.

## 2. Hierarchical Tree (Level 2)
```text
workspace/
├── Analysis/
│   ├── ecog/
│   ├── eeg/
│   ├── meg/
│   ├── nwb/
│   └── Research_Assets/
├── Computational/
│   ├── core_tools/ (jlmlx, lib, src)
│   ├── jbiophysics/
│   ├── mllm/
│   ├── mscz/
│   └── misc/
├── drive/ (Google Drive)
├── HNXJ/
│   ├── admin/
│   ├── hnxj_gio/
│   ├── hnxj-gemini/ [EXEMPT]
│   ├── media/
│   └── skills/
├── Repositories/
│   ├── AAE/
│   ├── GSDR_repo/
│   └── jbiophys/
└── misc/
```

*Note: Every directory follows the 5-folder limit (excluding hnxj-gemini and root). All loose data files (.npy, .nwb, .txt) are categorized into local 'data/' subdirectories.*
