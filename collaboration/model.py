import numpy as np
from sklearn.ensemble               import RandomForestClassifier, RandomForestRegressor
from collaboration.beta_calibrator import BetaCalibrator

clf       = RandomForestClassifier(n_estimators=200, random_state=42)
sigma_reg = RandomForestRegressor(n_estimators=100, random_state=42)
beta_cal  = BetaCalibrator(n_bins=15, alpha0=2.0, beta0=2.0)

MARKET_KEYS = [
    "1X2_H","1X2_D","1X2_A",
    "OU1.5_O","OU1.5_U",
    "OU2.5_O","OU2.5_U",
    "OU3.5_O","OU3.5_U",
    "BTTS_Y","BTTS_N"
]

def train_models(X, y, X_sigma, residuals):
    clf.fit(X, y)
    sigma_reg.fit(X_sigma, residuals)
    raw_p = clf.predict_proba(X)[:,1]
    beta_cal.fit(raw_p, y.values)

def predict_proba_sigma(X):
    raw_p = clf.predict_proba(X)[:,1]
    p_cal = beta_cal.transform(raw_p)
    sigma = sigma_reg.predict(X)
    return p_cal, sigma

def compute_all(fx_feats, feats):
    rows = []
    for _, r in fx_feats.iterrows():
        p, sigma = predict_proba_sigma(r[feats].values.reshape(1,-1))
        p, sigma = float(p), float(sigma)
        for mk in MARKET_KEYS:
            odds_col = f"{mk}_odds"
            if odds_col not in r: continue
            odds = r[odds_col]
            b    = odds - 1
            ev   = p*b - (1-p)
            rows.append({
                **r.to_dict(),
                "market":       mk,
                "p":            p,
                "sigma":        sigma,
                "ev":           ev,
                "decimal_odds": odds
            })
    return pd.DataFrame(rows)
