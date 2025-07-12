# ⚙️ General Settings
TOP_N_MARKETS_PER_MATCH = 3           # Number of high-EV bets to return per match
MIN_EV_THRESHOLD        = 0.05        # Minimum expected value for a market to be selected
MAX_ODDS_CAP            = 20.0        # Upper limit on decimal odds for filtering

# 📅 League and Match Filters
SUPPORTED_LEAGUES = [
    "Premier League", "Serie A", "La Liga", "Bundesliga", "Ligue 1",
    "Eredivisie", "Primeira Liga", "Scottish Premiership",
    "Super Lig", "Belgian Pro League"
]

WOMENS_COMPETITIONS = [
    "UEFA Championship - Women",
    "FA Women's Super League",
    "Division 1 Féminine",
    "Frauen-Bundesliga"
]

# 🤖 Model Configuration
RANDOM_FOREST_PARAMS = {
    "n_estimators": 100,
    "max_depth": 8,
    "min_samples_split": 5,
    "random_state": 42
}

# 📊 Feature Flags
INCLUDE_HOME_ADVANTAGE      = True
INCLUDE_RECENT_FORM         = True
INCLUDE_INJURY_DATA         = False  # toggle when injury feed is active
INCLUDE_WEATHER_FEATURES    = False  # toggle when weather API is wired

# 📍 External API Settings
DEFAULT_EXCHANGE_CURRENCY = "EUR"
DEFAULT_MARKET_REGION     = "EU"
