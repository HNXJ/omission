# core
import numpy as np
from sklearn.decomposition import PCA
from sklearn.mixture import GaussianMixture
from sklearn.cluster import KMeans
from ..core.logger import log

def compute_statistics(data: any, stat_type: str, **kwargs):
    """
    Canonical signal-agnostic statistics computation.
    
    Args:
        data: The extracted features or raw data.
        stat_type: The type of statistic to compute (e.g., 'fano', 'zscore', 'kmeans', 'gmm').
        kwargs: Additional parameters for the statistical method.
    """
    log.action(f"[action] Computing statistics for type: {stat_type} with args {kwargs}")
    
    if stat_type == "fano":
        log.progress(f"[action] Computing Fano Factor...")
        return _compute_fano(data, **kwargs)
    elif stat_type == "zscore":
        log.progress(f"[action] Computing Z-Score...")
        return _compute_zscore(data, **kwargs)
    elif stat_type == "kmeans":
        log.progress(f"[action] Computing KMeans Clustering...")
        return _compute_kmeans(data, **kwargs)
    elif stat_type == "gmm":
        log.progress(f"[action] Computing Gaussian Mixture Model Clustering...")
        return _compute_gmm(data, **kwargs)
    elif stat_type == "pca":
        log.progress(f"[action] Computing Principal Component Analysis...")
        return _compute_pca(data, **kwargs)
    else:
        log.error(f"[action] Invalid stat_type: {stat_type}")
        raise ValueError(f"Unsupported stat_type: {stat_type}")

def _compute_fano(data, **kwargs):
    """Internal Fano Factor logic."""
    log.action(f"[action] _compute_fano invoked")
    if isinstance(data, np.ndarray):
        # Assuming shape (trials, time)
        var = np.var(data, axis=0)
        mean = np.mean(data, axis=0) + 1e-10
        return var / mean
    return None

def _compute_zscore(data, **kwargs):
    """Internal Z-Score logic."""
    log.action(f"[action] _compute_zscore invoked")
    if isinstance(data, np.ndarray):
        mean = np.mean(data, axis=kwargs.get('axis', 0), keepdims=True)
        std = np.std(data, axis=kwargs.get('axis', 0), keepdims=True) + 1e-10
        return (data - mean) / std
    return None

def _compute_kmeans(data, n_clusters=4, **kwargs):
    """
    KMeans clustering logic. Useful for classifying neurons into S+, S-, O+, O-.
    data: (n_samples, n_features)
    """
    log.action(f"[action] _compute_kmeans invoked with {n_clusters} clusters")
    model = KMeans(n_clusters=n_clusters, random_state=kwargs.get('random_state', 42), n_init="auto")
    labels = model.fit_predict(data)
    return labels, model

def _compute_gmm(data, n_components=4, **kwargs):
    """
    Gaussian Mixture Model logic for soft clustering.
    data: (n_samples, n_features)
    """
    log.action(f"[action] _compute_gmm invoked with {n_components} components")
    model = GaussianMixture(n_components=n_components, random_state=kwargs.get('random_state', 42))
    labels = model.fit_predict(data)
    probs = model.predict_proba(data)
    return labels, probs, model

def _compute_pca(data, n_components=0.95, **kwargs):
    """
    PCA logic for dimensionality reduction before clustering.
    By default keeps 95% of variance.
    data: (n_samples, n_features)
    """
    log.action(f"[action] _compute_pca invoked with {n_components} components target")
    model = PCA(n_components=n_components, random_state=kwargs.get('random_state', 42))
    reduced_data = model.fit_transform(data)
    return reduced_data, model