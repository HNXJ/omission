# beta
import numpy as np
from sklearn.decomposition import PCA
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log

def estimate_gaussian_mi(x, y):
    """
    Estimates MI between two vectors assuming Gaussianity.
    MI = -0.5 * log(1 - rho^2)
    """
    if x.ndim > 1: x = PCA(n_components=1).fit_transform(x).flatten()
    if y.ndim > 1: y = PCA(n_components=1).fit_transform(y).flatten()
    
    rho = np.corrcoef(x, y)[0, 1]
    # Bound rho to avoid infinity
    rho = np.clip(rho, -0.999, 0.999)
    return -0.5 * np.log(1 - rho**2)

def analyze_information_bottleneck(loader: DataLoader, sessions: list, areas: list):
    """
    Computes MI(Past; Present) and MI(Label; Present) for each area.
    'Past' = d1/d2 (pre-omission), 'Present' = p2/p3 (omission), 'Label' = AXAB vs BXBA.
    """
    results = {area: {'past_mi': [], 'label_mi': []} for area in areas}
    
    for ses in sessions:
        log.info(f"Computing Info Bottleneck for {ses}")
        for area in areas:
            # Load two conditions to have labels
            spk1 = loader.get_signal(mode="spk", condition="AXAB", area=area, session=ses)
            spk2 = loader.get_signal(mode="spk", condition="BXBA", area=area, session=ses)
            
            if not spk1 or not spk2: continue
            
            # (trials, units, time)
            # Past window: 500:1000 (local d1 proxy)
            # Present window: 1000:1531 (local p2)
            past1 = np.mean(spk1[0][:, :, 500:1000], axis=-1)
            pres1 = np.mean(spk1[0][:, :, 1000:1531], axis=-1)
            
            past2 = np.mean(spk2[0][:, :, 500:1000], axis=-1)
            pres2 = np.mean(spk2[0][:, :, 1000:1531], axis=-1)
            
            # MI(Past; Present) for AXAB
            mi_pp = estimate_gaussian_mi(past1, pres1)
            
            # MI(Label; Present)
            # Use trial-wise mean firing rate as proxy for 'Present' state
            pres_all = np.vstack([pres1, pres2]) # (trials_all, units)
            labels = np.concatenate([np.zeros(pres1.shape[0]), np.ones(pres2.shape[0])])
            mi_lp = estimate_gaussian_mi(pres_all, labels)
            
            results[area]['past_mi'].append(mi_pp)
            results[area]['label_mi'].append(mi_lp)
            
    # Aggregate
    final_results = {}
    for area in areas:
        if results[area]['past_mi']:
            final_results[area] = {
                'past_mi': np.mean(results[area]['past_mi']),
                'label_mi': np.mean(results[area]['label_mi'])
            }
            
    return final_results
