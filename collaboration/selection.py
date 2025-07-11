from itertools import combinations
from collaboration.config import MAX_PAIR_CORR, CORR_MATRIX, EV_THRESHOLDS

def market_type(m):
    if m.startswith("OU1.5"): return "Totals_1.5"
    if m.startswith("OU2.5"): return "Totals_2.5"
    if m.startswith("OU3.5"): return "Totals_3.5"
    if m.startswith("BTTS"):  return "BTTS_No"
    if m.startswith("1X2"):   return "1X2"
    return "Other"

def select_markets(ev_df):
    out=[]
    for mid, grp in ev_df.groupby("match_id"):
        grp["type"] = grp.market.map(market_type)
        grp = grp[grp.ev >= grp.type.map(lambda t: EV_THRESHOLDS.get(t,0.05))]
        out.append(grp.nlargest(2, "ev"))
    return pd.concat(out) if out else ev_df.iloc[0:0]

def generate_doubles(ev_df, top_n=2):
    rows=[]
    for mid, grp in ev_df.groupby("match_id"):
        top = grp.nlargest(top_n, "ev")
        for a,b in combinations(top.itertuples(), 2):
            corr = CORR_MATRIX.get((a.market,b.market), 0.0)
            if corr > MAX_PAIR_CORR: continue
            joint_p  = a.p * b.p
            joint_od = a.decimal_odds * b.decimal_odds
            joint_ev = joint_p*(joint_od-1) - (1-joint_p)
            rows.append({
                "match_id":     mid,
                "market":       f"DOUBLE_{a.market}+{b.market}",
                "p":            joint_p,
                "sigma":        max(a.sigma,b.sigma),
                "ev":           joint_ev,
                "decimal_odds": joint_od,
                "vol_total":    (a.vol_total + b.vol_total)/2
            })
    return pd.DataFrame(rows)

def kelly_fraction(p, odds):
    b = odds - 1
    return (p*b - (1-p))/b if b>0 else 0.0
