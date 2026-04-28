## Methods: SVM Decoding and Statistical Thresholding

### SVM Decoding Pipeline
A Support Vector Machine (SVM) classifier with a linear kernel was employed to decode omission versus standard states. Features consisted of Z-scored FR from the Stable-Plus population. We utilized 10-fold stratified cross-validation. Decoding accuracy was assessed over time using a sliding window approach (50 ms width, 10 ms step).

### Statistical Thresholding
Functional unit classification and omission-related significance were determined using non-parametric Wilcoxon rank-sum tests (alpha = 0.01). Multiple comparison corrections (Bonferroni) were applied where specified in the analysis scripts.
