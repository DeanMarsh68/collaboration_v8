import numpy as np
import pandas as pd
from collaboration.config            import START_BANKROLL
from collaboration.data_ingest       import fetch_fixture_data, fetch_team_stats
from collaboration.features           import build_features
from collaboration.model              import compute_all
from collaboration.selection          import generate_doubles, kelly_fraction
from collaboration.continuous_bandit  import BetaPolicy
from collaboration.alerts             import check_alerts

policy = BetaPolicy()
bank    = START_BANKROLL

def paper_trade_for_date(date, peak):
    global policy, bank

    fx_df      = fetch_fixture_data(date)
    stats_df   = fetch_team_stats(date)
    fx_feats, feats = build_features(fx_df, stats_df)

    ev_singles = compute_all(fx_feats, feats)
    ev_doubles = generate_doubles(ev_singles, top_n=2)
    ev_all     = pd.concat([ev_singles, ev_doubles], ignore_index=True)

    trades=[]
    alpha = policy.sample()
    for r in ev_all.itertuples():
        if r.ev < 0.05: continue
        f0    = kelly_fraction(r.p, r.decimal_odds)
        conf  = max(0.5, 1 - r.sigma/r.p)
        mv    = getattr(r, "vol_total", 0) / fx_feats.vol_total.median()
        stake = bank * f0 * conf * (1 + alpha*(mv-1))
        trades.append({**r._asdict(), "stake": stake, "alpha": alpha, "date": date, "win": np.nan})

    df = pd.DataFrame(trades)
    df["return"] = df.apply(
        lambda x: (x.decimal_odds * x.stake - x.stake) if x.win else -x.stake,
        axis=1
    )

    total_pl = df["return"].sum()
    reward   = total_pl / bank if bank>0 else 0
    policy.update(alpha, reward)
    bank   += total_pl

    df["bankroll"] = bank
    check_alerts(df)
    peak = max(peak, bank)
    return df, peak
