---
name: science-neuro-omission-identity-coding
description: "Omission analysis skill focusing on science neuro omission identity coding."
---

# Ternary Identity Encoding

The brain's ability to distinguish between different stimuli (A vs B) and their absence (Random-R or Omission-X) is central to our study. We investigate how identity information is represented across the hierarchy using ternary encoding (A vs B vs R).

Encoding Properties:
1. Stimulus A (45°): Activates specific orientation columns.
2. Stimulus B (135°): Activates orthogonal orientation columns.
3. Random R: A baseline state where the identity is unpredictable.

Precision Hierarchy:
- V1/V2: High precision for A vs B based on orientation. Minimal distinction between R and A/B in terms of population state.
- V4/MT: Integration of features. Identity becomes more robust to noise.
- PFC: Abstract identity coding. The PFC maintains the 'Concept' of A or B even during the 531ms delay periods and omissions.

Information Theory:
We use Percent Explained Variance (PEV) and Mutual Information to quantify identity coding. We find that identity information in PFC persists significantly longer than in V1, where it decays rapidly after stimulus offset.

Technical Implementation:
```python
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score
import numpy as np

def decode_identity(X, y):
    # X: (trials, neurons), y: labels (0=A, 1=B, 2=R)
    clf = SVC(kernel='linear')
    scores = cross_val_score(clf, X, y, cv=5)
    return np.mean(scores)

# Ternary decoding (Chance = 33%)
```

Scientific Context:
Ternary encoding allows us to dissociate simple sensory detection from categorical identification. In high-order areas, the representation of 'A' during an omission is closer to the representation of 'A' during a stimulus than it is to 'B', proving the existence of an internal identity model.

References:
1. Meyers, E. M., et al. (2008). Dynamic Population Coding of Working Memory. Journal of Neurophysiology.
2. Miller, E. K., & Cohen, J. D. (2001). An Integrative Theory of Prefrontal Cortex Function. Annual Review of Neuroscience.
