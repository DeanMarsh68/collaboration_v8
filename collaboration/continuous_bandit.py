import numpy as np
from scipy.stats import beta

class BetaPolicy:
    def __init__(self, a0=2.0, b0=2.0, lr=0.05):
        self.a  = a0
        self.b  = b0
        self.lr = lr

    def sample(self):
        return float(beta.rvs(self.a, self.b))

    def update(self, alpha, reward):
        grad_a = reward*(np.log(alpha) - (np.log(self.a)-np.log(self.a+self.b)))
        grad_b = reward*(np.log(1-alpha) - (np.log(self.b)-np.log(self.a+self.b)))
        self.a  = max(1e-3, self.a + self.lr * grad_a)
        self.b  = max(1e-3, self.b + self.lr * grad_b)
