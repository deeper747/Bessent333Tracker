# Bessent 3-3-3 Tracker

A single-page dashboard that measures Treasury Secretary Scott Bessent's three 2028 targets against public data:

| Indicator | Target | Source |
|---|---|---|
| Real GDP growth | 3 percent | Bureau of Economic Analysis, via FRED (`A191RL1Q225SBEA`) |
| Federal deficit as a share of GDP | 3 percent | Monthly Treasury Statement (`MTSDS133FMS`) over nominal GDP (`GDP`), via FRED |
| Oil and gas production | 3 million more barrels of oil equivalent per day | Energy Information Administration monthly production |

## How it works

- `index.html` is the whole page. It reads `data.json` and draws the charts. There is no build step.
- `scripts/fetch_data.py` downloads the source series and writes `data.json`.
- `.github/workflows/update-data.yml` runs the script every Monday and commits `data.json` when it changes. You can also run it by hand from the Actions tab.

## Method notes

- The deficit ratio is the sum of the latest 12 monthly balances divided by the most recent quarterly nominal GDP (annual rate). Its baseline is January 2025.
- The energy total adds crude oil, natural gas plant liquids, and dry natural gas. Gas converts at 6 thousand cubic feet per barrel of oil equivalent. Its baseline is the 2024 average. Bessent has not published an official definition, so this composition is a judgment call.

## Run locally

```
pip install xlrd
python scripts/fetch_data.py
python -m http.server
```

Then open http://localhost:8000.
