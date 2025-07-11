import pandas as pd
import requests
from collaboration.config import API_KEYS, WEATHER_API_URL, INJURY_API_URL, EXCHANGE_API_URL, STADIUM_GEOCODE

def stadium_geocode(team):
    return STADIUM_GEOCODE.get(team, "0,0")

def fetch_fixture_data(date):
    key     = API_KEYS["api_football"]
    headers = {"x-apisports-key": key}
    fx_url  = "https://v3.football.api-sports.io/fixtures"
    od_url  = "https://v3.football.api-sports.io/odds"

    resp = requests.get(fx_url, headers=headers,
                        params={"date": date, "league": 1075, "season": 2025}).json()["response"]
    rows = []
    for f in resp:
        mid   = f["fixture"]["id"]
        home  = f["teams"]["home"]["name"]
        away  = f["teams"]["away"]["name"]
        odds  = requests.get(od_url, headers=headers,
                              params={"fixture": mid, "league": 1075, "season": 2025}
                             ).json()["response"]
        if not odds: continue
        bets = odds[0]["bookmakers"][0]["bets"]
        o_map = {}
        for b in bets:
            lbl = b["label"]
            for v in b["values"]:
                if lbl == "1X2":
                    mk = f"1X2_{v['value'].replace(' ','')}"
                elif lbl.startswith("Over/Under"):
                    t  = lbl.split()[-1]
                    mk = f"OU{t}_{'O' if 'Over' in v['value'] else 'U'}"
                elif lbl == "Both Teams to Score":
                    mk = f"BTTS_{'Y' if v['value']=='Yes' else 'N'}"
                else:
                    continue
                o_map[f"{mk}_odds"] = float(v["odd"])
        rows.append({
            "match_id": mid, "home": home, "away": away,
            **o_map
        })
    return pd.DataFrame(rows)

def fetch_team_stats(date):
    key     = API_KEYS["api_football"]
    headers = {"x-apisports-key": key}
    tm_url  = "https://v3.football.api-sports.io/teams"
    st_url  = "https://v3.football.api-sports.io/teams/statistics"
    fx_url  = "https://v3.football.api-sports.io/fixtures"

    teams = requests.get(tm_url, headers=headers,
                         params={"league": 1075, "season": 2025}).json()["response"]
    stats = []
    for t in teams:
        tid  = t["team"]["id"]
        name = t["team"]["name"]
        r    = requests.get(st_url, headers=headers,
                            params={"team": tid, "league": 1075, "season": 2025}
                           ).json()["response"]
        gf = r["goals"]["for"]["total"]["total"]
        ga = r["goals"]["against"]["total"]["total"]
        mp = r["fixtures"]["played"]["total"] or 1
        xG, xGA = gf/mp, ga/mp
        sot     = r["shots"]["on"]["total"]["total"]/mp
        last5   = requests.get(fx_url, headers=headers,
                               params={"team": tid, "season": 2025, "last": 5}
                              ).json()["response"]
        hits    = sum(1 for fx in last5 if fx["goals"]["home"]["total"]>0 and fx["goals"]["away"]["total"]>0)
        stats.append({
            "team": name,
            "team_id": tid,
            "xG": xG,
            "xGA": xGA,
            "elo": tid * 10,
            "shots_on_target": sot,
            "btts_pct_last5": hits / 5
        })
    return pd.DataFrame(stats)

def fetch_weather(home, date):
    latlng = stadium_geocode(home)
    resp   = requests.get(WEATHER_API_URL,
                          params={"apiKey": API_KEYS["weather"],
                                  "format": "json", "geocode": latlng}).json()
    return {
        "temp":      resp.get("temperature"),
        "humidity":  resp.get("relativeHumidity"),
        "wind_speed":resp.get("windSpeed")
    }

def fetch_injuries(team_id):
    resp = requests.get(INJURY_API_URL.format(team_id=team_id),
                        headers={"X-Auth-Token": API_KEYS["football_data"]}).json()
    inj  = resp.get("injuries", [])
    return {
        "starters_out": sum(i["role"]=="STARTER" for i in inj),
        "key_loss":     any(i["position"] in ("Forward","Midfielder") for i in inj)
    }

def fetch_exchange_volumes(match_id, market_ids):
    resp = requests.get(EXCHANGE_API_URL,
                        headers={"X-API-Key": API_KEYS["exchange"]},
                        params={"matchId": match_id, "marketIds": ",".join(map(str, market_ids))}
                       ).json()
    out = {}
    for m in resp.get("markets", []):
        tv = m.get("totalMatched", 0)
        bv = m.get("matchedBack", 0)
        lv = m.get("matchedLay", 0)
        out[int(m["marketId"])] = {
            "total_volume":   tv,
            "back_lay_skew": (bv - lv) / tv if tv else 0.0
        }
    return out

def fetch_live_odds(match_id):
    """
    In-play odds & volume skew fetch.
    """
    url  = EXCHANGE_API_URL.replace("/volume", "/inplay")
    resp = requests.get(url,
                        headers={"X-API-Key": API_KEYS["exchange"]},
                        params={"matchId": match_id}).json()
    rows=[]
    ts = pd.Timestamp.now()
    for m in resp.get("markets", []):
        rows.append({
            "market":       m["marketName"],
            "decimal_odds": m.get("bestBackPrice") or m.get("bestLayPrice"),
            "total_volume": m.get("totalMatched", 0),
            "back_lay_skew": (m.get("matchedBack",0)-m.get("matchedLay",0))/max(m.get("totalMatched",1),1),
            "timestamp":    ts
        })
    return pd.DataFrame(rows)
