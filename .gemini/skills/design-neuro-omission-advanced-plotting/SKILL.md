---
name: design-neuro-omission-advanced-plotting
description: "Omission analysis skill focusing on design neuro omission advanced plotting."
---

# Advanced Plotting Suite

Our analysis requires complex visualizations to capture multi-dimensional data.

Specialized Plots:
1. 2x4 Polar Density: Used to show the distribution of eye movement directionality across conditions.
2. Rose Plots: Circular histograms showing the preference of saccades/microsaccades for specific orientations (45° vs 135°).
3. Spectro-laminar MUAe: Depth plots showing the intensity of neural activity across cortical layers over time.
4. Manifold Exploration: 3D interactive plots showing population state space trajectories.

Technical Snippet (Rose Plot):
```python
import matplotlib.pyplot as plt
def plot_rose(angles, bins=36):
    ax = plt.subplot(111, projection='polar')
    ax.hist(angles, bins=bins, color='#CFB87C', alpha=0.7)
    plt.show()
```

Laminar Mapping:
We use vFLIP2 and MUAe sequence responses to align probes across sessions. Depth is plotted on the Y-axis (Channels) and time on the X-axis.

References:
1. Hunter, J. D. (2007). Matplotlib: A 2D Graphics Environment. Computing in Science & Engineering.
2. Waskom, M. L. (2021). seaborn: statistical data visualization. Journal of Open Source Software.
