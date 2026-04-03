# Skill: Predictive Routing Oculomotor & Task Logic
**Description:** Artifact rejection and behavioral state simulation for the Omission task.
**When to use:** When cleaning awake-behaving visual data or generating synthetic sequence labels.

### Key Functions
- `detect_microsaccades`: Engbert & Kliegl velocity-space thresholding.
- `get_clean_trials`: Purging microsaccade-contaminated epochs.
- `PredictiveRoutingTaskLogic`: Transition probability state machine.

### Location
- `D:\Analysis\predictive_routing_2020\src\preprocessing\oculomotor_controls.py`
- `D:\Analysis\predictive_routing_2020\src\models\task_logic.py`
