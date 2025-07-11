import smtplib, requests
import numpy as np
from collaboration.config import (
    SHARPE_ALERT_THRESH, DRIFT_ALERT_WINDOW,
    DRIFT_ALERT_BRIER, BRIER_BASELINE, ALERT_RECIPIENTS, SMS_GATEWAY_API
)

def rolling_sharpe(returns):
    return returns.rolling(DRIFT_ALERT_WINDOW).mean() / returns.rolling(DRIFT_ALERT_WINDOW).std()

def brier_score(p, wins):
    return np.mean((p - wins)**2)

def send_alert(msg):
    with smtplib.SMTP("smtp.example.com") as s:
        for to in ALERT_RECIPIENTS:
            s.sendmail("model@example.com", to, f"Subject: ALERT\n\n{msg}")
    if SMS_GATEWAY_API:
        requests.post(SMS_GATEWAY_API, json={"to": ALERT_RECIPIENTS, "msg": msg})

def check_alerts(df):
    rs = rolling_sharpe(df["return"])
    if rs.iloc[-1] < SHARPE_ALERT_THRESH:
        send_alert(f"Sharpe below {SHARPE_ALERT_THRESH}: {rs.iloc[-1]:.2f}")
    recent = df.tail(DRIFT_ALERT_WINDOW)
    bs     = brier_score(recent["p"], recent["win"])
    if bs - BRIER_BASELINE > DRIFT_ALERT_BRIER:
        send_alert(f"Calibration drift: Brier={bs:.3f}")
