import os

MODEL_NAME              = "collaboration_v8"
START_BANKROLL          = float(os.getenv("START_BANKROLL", "100.0"))

EV_THRESHOLDS = {
    "BTTS_No":    0.08,
    "Totals_1.5": 0.05,
    "Totals_2.5": 0.05,
    "Totals_3.5": 0.05,
    "1X2":        0.05
}

MAX_PAIR_CORR = 0.70
CORR_MATRIX   = {}

API_KEYS = {
    "api_football":  os.getenv("API_FOOTBALL_KEY", ""),
    "weather":       os.getenv("WEATHER_API_KEY", ""),
    "football_data": os.getenv("FOOTBALL_DATA_KEY", ""),
    "exchange":      os.getenv("EXCHANGE_API_KEY", "")
}

WEATHER_API_URL  = "https://api.weather.com/v3/wx/conditions/current"
INJURY_API_URL   = "https://api.football-data.org/v2/teams/{team_id}/injuries"
EXCHANGE_API_URL = "https://api.betfair.com/exchange/volume"

SHARPE_ALERT_THRESH = 1.0
DRIFT_ALERT_WINDOW  = 50
DRIFT_ALERT_BRIER   = 0.05
BRIER_BASELINE      = 0.16

ALERT_RECIPIENTS = os.getenv("ALERT_RECIPIENTS", "you@example.com").split(",")
SMS_GATEWAY_API  = os.getenv("SMS_GATEWAY_API", "")

STADIUM_GEOCODE = {
    "England":     "51.555,0.108",
    "Netherlands": "52.314,4.941",
    "France":      "48.853,2.369",
    "Wales":       "51.481,-3.179"
}
