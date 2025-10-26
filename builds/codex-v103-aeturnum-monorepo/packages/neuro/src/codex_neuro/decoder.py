import numpy as np
class TinyLogit:
    def __init__(self, n): self.w=np.zeros(n); self.b=0.0
    @staticmethod
    def _sig(z): return 1.0/(1.0+np.exp(-z))
    def predict_proba(self, X): X=np.asarray(X); return self._sig(X@self.w + self.b)
    def fit(self, X, y, lr=0.1, epochs=200):
        X=np.asarray(X); y=np.asarray(y)
        for _ in range(epochs):
            p=self.predict_proba(X); g=(p-y)
            self.w -= lr * (X.T @ g)/len(X); self.b -= lr * g.mean()
        return self
