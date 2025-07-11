import pandas as pd
from collaboration.execution import paper_trade_for_date

def run_backtest():
    hist_fx    = pd.read_csv("historical_fixtures.csv")
    hist_stats = pd.read_csv("historical_team_stats.csv")
    ledger     = []
    peak       = START_BANKROLL
    for d in sorted(hist_fx.date.unique()):
        trades, peak = paper_trade_for_date(d, peak)
        # merge in results to set trades.win here
        ledger.append(trades)
    pd.concat(ledger).to_csv("ledger.csv", index=False)

if __name__=="__main__":
    run_backtest()
