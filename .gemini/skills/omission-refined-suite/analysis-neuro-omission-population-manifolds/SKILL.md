# Population Manifold Analysis

Neural population activity can be viewed as a trajectory in a high-dimensional state space. We use dimensionality reduction (PCA, UMAP, t-SNE) to map these trajectories and understand the geometry of neural representations.

Geometries:
1. Stimulus Trajectories: Presentations of A and B drive the population into distinct regions of the state space.
2. Omission Trajectories: During an omission, the trajectory initially follows the expected stimulus path (The Ghost) before deviating into a 'Surprise' zone.
3. Stability: We measure the distance between trajectories (e.g., Euclidean distance or Mahalanobis distance) to quantify discriminability.

Technical Pipeline:
- Data Prep: Create a (N_Time, N_Neurons) matrix by averaging across trials.
- PCA: Reduce to top 3-10 components.
- Manifold Exploration: Use interactive 3D plots (Plotly) to visualize the evolution of the state over the 6000ms trial.

Code Example:
```python
from sklearn.decomposition import PCA
def plot_manifold(data_tensor):
    # data_tensor: (Time, Neurons)
    pca = PCA(n_components=3)
    coords = pca.fit_transform(data_tensor)
    # returns (Time, 3)
    return coords
```

Scientific Context:
Manifold analysis reveals how the brain maintains stable representations despite noise. The 'curvature' of the manifold during an omission can tell us about the speed and magnitude of the internal model update.

References:
1. Cunningham, J. P., & Yu, B. M. (2014). Dimensionality reduction for large-scale neural recordings. Nature Neuroscience.
2. Gallego, J. A., et al. (2017). Neural Manifolds for the Control of Movement. Neuron.
