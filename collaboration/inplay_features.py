from collaboration.data_ingest import fetch_live_odds

def fetch_inplay_momentum(match_id, baseline_odds):
    live = fetch_live_odds(match_id)
    live['delta_odds'] = live.apply(
        lambda r: r.decimal_odds - baseline_odds.get(r.market, r.decimal_odds), axis=1
    )
    live['delta_skew'] = live.back_lay_skew
    return {
        'odds_mom_mean': live.delta_odds.mean(),
        'skew_mom_mean': live.delta_skew.mean(),
        'odds_mom_max':  live.delta_odds.max(),
        'odds_mom_min':  live.delta_odds.min()
    }
