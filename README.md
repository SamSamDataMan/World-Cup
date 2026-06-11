# World Cup Pool Tracker

A small Streamlit app for viewing the 2026 World Cup group-stage schedule through the lens of the pool draw.

## Run

```powershell
pip install -r requirements.txt
streamlit run app.py
```

The app lists fixtures in Eastern time, shows the owner for each team, and includes filters for owner, team, group, search, and upcoming-only views.

## Data Notes

The group-stage fixture list was curated from FourFourTwo's full fixture page and converted to Eastern time:
https://www.fourfourtwo.com/competition/world-cup-2026-fixtures-and-results

TV labels were cross-checked from SB Nation's schedule page:
https://www.sbnation.com/soccer/1117513/world-cup-schedule-2026-how-to-watch-every-match-scores-and-more

Knockout-round games are not included yet because the teams are not known until the group stage is complete.
