import pandas as pd
from tqdm import tqdm
from collaboration.data_ingest import fetch_fixture_data, fetch_team_stats

def main():
    # adjust to your desired period
    dates = pd.date_range("2025-01-01", "2025-07-14", freq="D")
    fx_hist   = []
    stats_hist = []

    for d in tqdm(dates):
        ds = d.strftime("%Y-%m-%d")
        try:
            fx = fetch_fixture_data(ds)
            if not fx.empty:
                fx["date"] = ds
                fx_hist.append(fx)
        except Exception as e:
            print(f"skip fixtures {ds}: {e}")

        try:
            st = fetch_team_stats(ds)
            if not st.empty:
                st["date"] = ds
                stats_hist.append(st)
        except Exception as e:
            print(f"skip stats    {ds}: {e}")

    pd.concat(fx_hist, ignore_index=True).to_csv("historical_fixtures.csv", index=False)
    pd.concat(stats_hist, ignore_index=True).to_csv("historical_team_stats.csv", index=False)
    print("Wrote historical_fixtures.csv and historical_team_stats.csv")

if __name__=="__main__":
    main()
