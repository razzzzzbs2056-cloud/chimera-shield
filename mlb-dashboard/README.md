# ⚾ MLB Prop Dashboard

A live, interactive Streamlit web app for MLB player prop projections, powered
by sabermetrics + matchup data from the public MLB Stats API.

> ⚠️ **Disclaimer:** Projections are model estimates, not guarantees. Always
> verify lineups, weather, and injury reports before game time. Not financial
> advice.

---

## 📁 Project Structure

```
mlb-dashboard/
├── app.py              ← Main Streamlit UI
├── engine.py           ← Projection math
├── api_client.py       ← MLB API wrapper
├── parks.py            ← Park factor data
├── requirements.txt
└── README.md
```

## 🚀 Run Locally

```bash
# From the mlb-dashboard/ directory:

# 1. Virtual env
python -m venv venv
source venv/bin/activate    # Mac/Linux
# venv\Scripts\activate     # Windows

# 2. Install
pip install -r requirements.txt

# 3. Launch
streamlit run app.py
```

Opens at http://localhost:8501

## ✨ Features

- 📈 **Hit / Run / RBI / HR projections** per game
- 🎯 **Factor radar chart** with 8 key drivers
- ⚾ **Pitcher matchup** breakdown (ERA, WHIP, K%, HR/9, GB%)
- 🏟️ **Park factor** analysis across all 30 stadiums
- 🌤️ **Weather-adjusted** HR projections (temp, wind, humidity)
- 🔀 **Platoon split** (vs LHP / vs RHP) visualization
- 📅 **Today's schedule** with probable pitchers

## 🧠 How It Works

1. Type a player name in the sidebar.
2. Adjust weather + lineup position.
3. The engine blends season stats, platoon splits, the opposing probable
   pitcher's profile, park factors, and weather into per-stat projections.
4. Review projections and the factor radar to identify edges.

Data is sourced from the public **MLB Stats API**
(`https://statsapi.mlb.com`). Park factors are static approximations.

## ☁️ Deploy Free

1. Push to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io).
3. Connect the repo, set the app file to `mlb-dashboard/app.py`, and deploy.
