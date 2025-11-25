# City Day Planner — Solo Starter (Python/Tkinter)

A minimal open‑source intelligent desktop app with a GUI that pulls data from **5 sources** (Open‑Meteo Weather, Open‑Meteo Air Quality, OpenAQ, OSRM Routing, Nominatim Geocoding) and computes a simple **Comfort Score** + recommendation. Includes ready‑to‑use templates for **Project Plan**, **Risk Plan**, **Earned Value**, **PM Plan**, and a **Test Document**.

## Quick Start
```bash
# 1) Create & activate venv (Windows)
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

# 2) Install
pip install -r app/requirements.txt

# 3) Run
python app/main.py
```

## Data Sources (no API keys)
- Open‑Meteo Forecast API
- Open‑Meteo Air Quality API
- OpenAQ Measurements API
- OSRM Public Routing API
- Nominatim (OpenStreetMap) Geocoding

## Deliverables
See the `docs/` folder for: project_plan.csv, risk_register.csv, earned_value.csv, pm_plan.md, test_document.md. Update as you work and push to GitHub.
# city-day-planner-solo
