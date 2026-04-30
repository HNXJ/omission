# Omission Artifact Contract (v1.0)

## 1. Definition
An **Artifact** is a self-contained directory within `outputs/` that represents a scientific result or visualization.

## 2. Directory Structure
```
artifact_id/
├── index.html        # REQUIRED: The primary interactive visualization
├── meta.json         # OPTIONAL: Machine-readable metadata (title, phase, tags)
├── thumbnail.png     # OPTIONAL: Dashboard preview image
└── assets/           # OPTIONAL: Sub-directory for data/scripts/styles
```

## 3. Metadata Specification (meta.json)
```json
{
  "title": "Figure Title",
  "phase": 5,
  "category": "Modeling",
  "description": "Short summary of findings",
  "dependencies": ["nwb_file_v1.nwb"]
}
```

## 4. UI Rendering Contract
The Dashboard UI MUST:
1. Scan the `manifest.json` emitted by the builder.
2. Render each entry as an `<iframe>` pointing to the artifact's `index.html`.
3. Fallback to `meta.json` for labeling if the Registry is unavailable.
