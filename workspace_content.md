# 🏺 Workspace Chandelier (Structural Overview)

## 1. Root Architecture (6 Pillars)
The workspace is organized into 6 primary pillars to maximize navigation speed and structural clarity.

- **Analysis/**: Empirical data processing and research assets.
- **Computational/**: Biophysical modeling and ScZ project.
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
│   ├── core_tools/
│   ├── jbiophysics/
│   ├── jschizophrenia/
│   ├── mllm/
│   ├── mscz/
│   └── src/
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

*Note: Every directory follows the 5-folder limit (excluding hnxj-gemini and root) and contains a 'misc/' vault.*
