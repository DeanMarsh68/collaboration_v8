import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from collaboration.data_ingest        import fetch_weather, fetch_injuries, fetch_exchange_volumes
from collaboration.inplay_features   import fetch_inplay_momentum
from collaboration.config             import TOP_N_MARKETS_PER_MATCH

def build_features(fx_df, stats_df):
    df = fx_df.merge(
        stats_df.rename(columns={'team':'home','team_id':'home_id'}),
        on='home'
    ).merge(
        stats_df.rename(columns={'team':'away','team_id':'away_id'}),
        on='away', suffixes=('','_opp')
    )

    # basic signals
    df['btts_trend']   = 0.5*(df.btts_pct_last5 + df.btts_pct_last5_opp)
    df['def_solidity'] = 0.5*(df.shots_on_target + df.shots_on_target_opp)
    df['xG_diff']      = df.xG - df.xG_opp
    df['elo_diff']     = df.elo - df.elo_opp

    # weather & injuries
    wx = df.apply(lambda r: fetch_weather(r.home, r.date), axis=1)
    df = pd.concat([df, pd.DataFrame(wx.tolist())], axis=1)

    inj_h = df.home_id.apply(fetch_injuries)
    inj_a = df.away_id.apply(fetch_injuries)
    df['home_injured']  = [i['starters_out'] for i in inj_h]
    df['away_injured']  = [i['starters_out'] for i in inj_a]
    df['home_key_loss'] = [i['key_loss']    for i in inj_h]
    df['away_key_loss'] = [i['key_loss']    for i in inj_a]

    # volumes
    vol_map = fetch_exchange_volumes(df.match_id.iloc[0], df.match_id.tolist())
    df['vol_total'] = df.match_id.map(lambda m: vol_map[m]['total_volume'])
    df['vol_skew']  = df.match_id.map(lambda m: vol_map[m]['back_lay_skew'])

    # In-play momentum
    feats = ['xG_diff','elo_diff','btts_trend','def_solidity',
             'temp','humidity','wind_speed',
             'home_injured','away_injured','home_key_loss','away_key_loss',
             'vol_total','vol_skew']
    for i, row in df.iterrows():
        baseline = {mk: row[f"{mk}_odds"] for mk in [
            '1X2_H','1X2_D','1X2_A',
            'OU1.5_O','OU1.5_U',
            'OU2.5_O','OU2.5_U',
            'OU3.5_O','OU3.5_U',
            'BTTS_Y','BTTS_N'
        ] if f"{mk}_odds" in row}
        inplay = fetch_inplay_momentum(row.match_id, baseline)
        for k,v in inplay.items():
            df.at[i, k] = v
    feats += ['odds_mom_mean','skew_mom_mean','odds_mom_max','odds_mom_min']

    # scale
    df[feats] = StandardScaler().fit_transform(df[feats])
    return df, feats

def extract_context(row, feats):
    x = row[feats].values.astype(float)
    x = np.concatenate([x, [row.p, row.sigma]])
    return x
