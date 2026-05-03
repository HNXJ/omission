import os

class FigureRegistry:
    # CANONICAL REPOSITORY TOPOLOGY
    FIGURE_DATA = [
        {"id": "f001", "title": "Theory Schematic", "module": "src/f001_theory", "phase": 1, "x": "Time", "y": "Area Hierarchy"},
        {"id": "f002", "title": "Omission PSTH", "module": "src/f002_psth", "phase": 1, "x": "Time", "y": "Firing Rate"},
        
        {"id": "f003", "title": "Surprise Dynamics", "module": "src/f003_surprise", "phase": 2, "x": "Time", "y": "FR Delta"},
        {"id": "f004", "title": "Unit Coding Suite", "module": "src/f004_coding", "phase": 2, "x": "Time", "y": "FR / Trials"},
        
        {"id": "f005", "title": "Time-Frequency Representation", "module": "src/f005_tfr", "phase": 3, "x": "Time", "y": "Frequency"},
        {"id": "f006", "title": "Band-Specific Power", "module": "src/f006_band_power", "phase": 3, "x": "Time", "y": "Power (dB)"},
        
        {"id": "f007", "title": "Spike-Field Coherence", "module": "src/f007_sfc", "phase": 4, "x": "Frequency", "y": "Coherence"},
        {"id": "f008", "title": "Cross-Area Coordination", "module": "src/f008_coordination", "phase": 4, "x": "Time", "y": "Correlation"},
        {"id": "f009", "title": "Individual SFC Units", "module": "src/f009_individual_sfc", "phase": 4, "x": "Frequency", "y": "Coherence"},
        {"id": "f010", "title": "SFC Delta (Surprise)", "module": "src/f010_sfc_delta", "phase": 4, "x": "Frequency", "y": "Delta Coh"},
        
        {"id": "f011", "title": "Laminar Mapping", "module": "src/f011_laminar", "phase": 5, "x": "Time", "y": "Depth"},
        {"id": "f012", "title": "CSD Profiling", "module": "src/f012_csd_profiling", "phase": 5, "x": "Time", "y": "Sink/Source Intensity"},
        {"id": "f013", "title": "Rhythmic Evolution", "module": "src/f013_rhythmic_evolution", "phase": 5, "x": "Time", "y": "Frequency"},
        {"id": "f014", "title": "Spiking Granger", "module": "src/f014_spiking_granger", "phase": 5, "x": "Frequency", "y": "Causality (GC)"},
        {"id": "f015", "title": "Spectral Granger", "module": "src/f015_spectral_granger", "phase": 5, "x": "Frequency", "y": "Causality (GC)"},
        {"id": "f016", "title": "Impedance Profiles", "module": "src/f016_impedance_profiles", "phase": 5, "x": "Frequency", "y": "Impedance (kOhm)"},
        {"id": "f017", "title": "Prediction Error Scaling", "module": "src/f017_prediction_errors", "phase": 5, "x": "Surprise Level", "y": "Response Amplitude"},
        {"id": "f018", "title": "Ghost Signals", "module": "src/f018_ghost_signals", "phase": 5, "x": "Time", "y": "LFP (uV)"},
        {"id": "f019", "title": "PAC Analysis", "module": "src/f019_pac_analysis", "phase": 5, "x": "Phase Freq", "y": "Amp Freq"},
        {"id": "f020", "title": "Effective Connectivity", "module": "src/f020_effective_connectivity", "phase": 5, "x": "Area 1", "y": "Area 2"},
        
        {"id": "f021", "title": "MaDeLaMo Schematic", "module": "src/f021_madelamo", "phase": 5, "x": "Latent State", "y": "Area Activity"},
        {"id": "f022", "title": "MaDeLaNe Projection", "module": "src/f022_madelane", "phase": 5, "x": "Component 1", "y": "Component 2"},
        {"id": "f023", "title": "Spectral Fingerprints", "module": "src/f023_spectral_fingerprints", "phase": 5, "x": "Frequency", "y": "Power"},
        {"id": "f024", "title": "Fano Factor", "module": "src/f024_fano_factor", "phase": 5, "x": "Time", "y": "Fano Factor"},
        {"id": "f025", "title": "State Decoding", "module": "src/f025_state_decoding", "phase": 5, "x": "Time", "y": "Accuracy"},
        {"id": "f026", "title": "State Latency", "module": "src/f026_state_latency", "phase": 5, "x": "Area", "y": "Latency (ms)"},
        {"id": "f027", "title": "Identity Coding", "module": "src/f027_identity_coding", "phase": 5, "x": "Time", "y": "Information"},
        {"id": "f028", "title": "State Manifolds", "module": "src/f028_state_manifolds", "phase": 5, "x": "Dim 1", "y": "Dim 2"},
        {"id": "f029", "title": "Info Bottleneck", "module": "src/f029_info_bottleneck", "phase": 5, "x": "Complexity", "y": "Informativeness"},
        {"id": "f030", "title": "Recurrence Dynamics", "module": "src/f030_recurrence_dynamics", "phase": 5, "x": "Time", "y": "Recurrence"},
        {"id": "f031", "title": "Spike Phase Locking", "module": "src/f031_spike_phase_locking", "phase": 5, "x": "Phase", "y": "Count"},
        {"id": "f032", "title": "Spike Triggered Average", "module": "src/f032_spike_triggered_average", "phase": 5, "x": "Time", "y": "LFP (uV)"},
        {"id": "f033", "title": "Spike Field Coherence", "module": "src/f033_spike_field_coherence", "phase": 5, "x": "Frequency", "y": "Coherence"},
        {"id": "f034", "title": "PEV Analysis", "module": "src/f034_pev_analysis", "phase": 5, "x": "Time", "y": "% Variance"},
        {"id": "f035", "title": "Deviance Scaling", "module": "src/f035_deviance_scaling", "phase": 5, "x": "Surprise", "y": "Deviance"},
        {"id": "f036", "title": "Interneuron Dynamics", "module": "src/f036_interneuron_dynamics", "phase": 5, "x": "Time", "y": "FR (Hz)"},
        {"id": "f037", "title": "Selectivity Index", "module": "src/f037_selectivity_index", "phase": 5, "x": "Area", "y": "SI"},
        {"id": "f038", "title": "Layer Granger", "module": "src/f038_layer_granger", "phase": 5, "x": "Frequency", "y": "GC"},
        {"id": "f039", "title": "Spike-Field Coherence (PPC)", "module": "src/f039_spike_field_coherence", "phase": 5, "x": "Frequency", "y": "PPC"},
        {"id": "f040", "title": "Population Sync Index", "module": "src/f040_onset_latency", "phase": 5, "x": "Time", "y": "Sync"},
        {"id": "f044", "title": "Laminar PAC", "module": "src/f044_laminar_pac", "phase": 5, "x": "Phase Freq", "y": "Amp Freq"},
        {"id": "f045", "title": "Laminar Coherence", "module": "src/f045_laminar_coherence", "phase": 5, "x": "Frequency", "y": "Coherence"},
        {"id": "f046", "title": "State-Space Trajectories", "module": "src/f046_state_space_trajectories", "phase": 5, "x": "PC1", "y": "PC2"},
        
        {"id": "f047", "title": "Pipeline Stability Audit", "module": "src/f047_stability_audit", "phase": 6, "x": "Test Case", "y": "Pass/Fail"},
        {"id": "f048", "title": "Profile Search Utility", "module": "src/f048_profile_analysis", "phase": 6, "x": "Effect Size", "y": "Count"},
        {"id": "f049", "title": "Omission Profile Figures", "module": "src/f049_omission_profiles", "phase": 6, "x": "Time (ms)", "y": "Firing Rate (Hz)"},
        {"id": "f050", "title": "Conjunction Profiles", "module": "src/f050_conjunction_profiles", "phase": 6, "x": "Time (ms)", "y": "Firing Rate (Hz)"}
    ]

    # SCIENTIFIC CALIBRATION: Processing latencies per area
    AREA_LATENCY = {
        "V1": 31,
        "V2": 45,
        "V3": 50,
        "V4": 60,
        "FEF": 80,
        "PFC": 100,
        "DEFAULT": 31
    }

    # POLICY LAYER: Centralized semantic rules
    STALE_PATTERNS = {
        "f007": [r"^fig7_.*", r".*spectrum.*"]
    }

    @classmethod
    def get_all(cls):
        return cls.FIGURE_DATA

    @classmethod
    def get_by_id(cls, fid):
        for fig in cls.FIGURE_DATA:
            if fig['id'] == fid:
                return fig
        return None

    @classmethod
    def get_by_phase(cls, phase_num):
        return [f for f in cls.FIGURE_DATA if f['phase'] == phase_num]

    @classmethod
    def should_include_file(cls, fig_id, filename):
        """
        Policy enforcement for artifact inclusion.
        Returns False if the file matches a stale pattern for the figure.
        """
        import re
        patterns = cls.STALE_PATTERNS.get(fig_id, [])
        for pattern in patterns:
            if re.match(pattern, filename):
                return False
        return True
