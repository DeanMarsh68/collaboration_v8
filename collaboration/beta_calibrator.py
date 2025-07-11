import numpy as np

class BetaCalibrator:
    def __init__(self, n_bins=10, alpha0=2.0, beta0=2.0):
        self.n_bins = n_bins
        self.alpha0 = alpha0
        self.beta0  = beta0

    def fit(self, probs, outcomes):
        bins = np.minimum((probs * self.n_bins).astype(int), self.n_bins-1)
        self.bin_means = np.zeros(self.n_bins)
        for i in range(self.n_bins):
            idx = bins == i
            if np.any(idx):
                self.bin_means[i] = np.mean(outcomes[idx])
            else:
                self.bin_means[i] = (i+0.5)/self.n_bins

    def transform(self, probs):
        bins = np.minimum((probs * self.n_bins).astype(int), self.n_bins-1)
        return np.array([self.bin_means[b] for b in bins])
