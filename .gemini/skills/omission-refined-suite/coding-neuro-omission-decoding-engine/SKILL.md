# Neural Decoding Engine

The decoding engine uses machine learning to quantify the information content of neural populations. We primarily use Support Vector Machines (SVM) with linear kernels.

Pipeline:
1. Feature Matrix: (Trials x Neurons) for a specific time bin.
2. Labels: Condition IDs (e.g., A vs B).
3. Cross-Validation: 5-fold or 10-fold stratified CV to ensure robust results.
4. Scoring: Accuracy or Percent Explained Variance (PEV).

Applications:
- Identity Decoding: Can we tell if the stimulus was A or B?
- Omission Detection: Can we tell if a stimulus was present or missing?
- Generalization: Training on stimulus periods and testing on omission periods (and vice versa).

Code Example:
```python
from sklearn.svm import LinearSVC
from sklearn.model_selection import StratifiedKFold
import numpy as np

def run_decoding(X, y):
    skf = StratifiedKFold(n_splits=5)
    accuracies = []
    for train_idx, test_idx in skf.split(X, y):
        clf = LinearSVC(max_iter=10000)
        clf.fit(X[train_idx], y[train_idx])
        accuracies.append(clf.score(X[test_idx], y[test_idx]))
    return np.mean(accuracies)
```

PEV Calculation:
PEV = (SS_between) / (SS_total). It provides a continuous measure of how much variance in firing rate is explained by the task variables.

References:
1. Pedregosa, F., et al. (2011). Scikit-learn: Machine Learning in Python. Journal of Machine Learning Research.
2. King, J. R., & Dehaene, S. (2014). Characterizing the dynamics of mental representations: the temporal generalization method. Trends in Cognitive Sciences.
