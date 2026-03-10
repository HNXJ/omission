# Neuroscience Writing: Code & Data Availability

Promoting transparency through GitHub and NWB standardization.

## 1. Code Availability (GitHub)
- **Repository**: Formally link to the `AAE` repository.
- **Organization**: Highlight the modular structure (e.g., "The `gsdr` package provides optimized biophysical solvers...").
- **Version**: Use Zenodo or GitHub Releases to create a persistent DOI for the specific code version used in the paper.

## 2. Data Availability (NWB)
- **Standard**: State that all raw and processed physiological data are stored in **Neurodata Without Borders (NWB)** format.
- **Repository**: Provide the location of the NWB files (e.g., DANDI Archive or private university server).
- **Access**: Explicitly state the method for data extraction (e.g., "Data were extracted using the modular `jnwb` tools included in the AAE repository").

## 3. Computational Environment
- Document the OS (macOS/Linux), hardware (Apple M1/M3 Max), and critical library versions (e.g., `jaxley==0.13.0`, `jax==0.4.x`).
- Provide a `requirements.txt` or `conda_env.yml` in the repository.
