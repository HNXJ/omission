# Skill: NWB Read Guardrails (Lazy I/O)

This protocol defines the strict requirements for accessing NWB datasets using PyNWB to ensure memory efficiency, I/O speed, and logical correctness.

## 🏁 Core Directive
**NEVER return lazy data handles (e.g., `ElectricalSeries`, `Units`) outside of the IO context manager that opened them.**

---

## 🏗️ Implementation Standards

### 1. Encapsulated IO
All NWB access must occur within the `get_nwb_io` context manager.
- **Good**: `with get_nwb_io(path) as (io, nwb): ... extract data ... return array`
- **Bad**: `return nwb.acquisition['lfp']` (The handle becomes closed/invalid after the function returns).

### 2. Metadata/Data Separation
- Use `load_session_metadata()` for lightweight queries (trial counts, electrode maps, unit lists).
- Metadata does NOT require keeping the HDF5 handle open once converted to a DataFrame.

### 3. Block-Reading (Vectorized Access)
Instead of looping over trials and performing hundreds of small HDF5 slices, use vectorized indexing where possible.
- **Pattern**: `data_block = handle.data[sample_starts : sample_starts + length, :]`
- **Optimization**: Minimized disk seek time by grouping requests by probe.

### 4. Deterministic Area Mapping
Always use the `electrodes` table `location` column as the source of truth for area assignment.
- Map global electrode IDs to probe-local indices before slicing the `ElectricalSeries`.

---

## 🛠️ Canonical Accessors
- **`lfp_io.get_nwb_io(path)`**: The standard context manager.
- **`lfp_pipeline.get_signal_conditional(...)`**: The high-level gateway for extracting epoched signals (LFP, MUAe, SPK) with built-in IO management.

---

## ⚠️ Common Failure Modes
- **Closed Context**: "AttributeError: 'NoneType' object has no attribute 'data'" (Occurs when a handle is accessed after `io.close()`).
- **Memory Overflow**: `data[:]` or `timestamps[:]` on a 1.5GB series will crash the agent's RAM.
- **Hardcoded Paths**: Never use `D:\` directly. Use `codes.config.paths` constants.

---
*Transferred-From: Antigravity*
*Status: Validated for 13 sessions (OGLO set).*
