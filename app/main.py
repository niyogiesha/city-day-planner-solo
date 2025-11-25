import tkinter as tk
from tkinter import ttk, messagebox
import requests

APP_TITLE = "City Day Planner (Solo Starter)"
# put your real email in the User-Agent (helps geocoding providers allow requests)
USER_AGENT = "CityDayPlanner-Solo/1.0 (contact@example.com)"

# ---------- Data sources (4 APIs) ----------


def geocode(city: str):
    """Robust geocoder: Open-Meteo -> Nominatim -> fuzzy fallbacks for common cities."""
    city = (city or "").strip()
    # 1) Open-Meteo Geocoding
    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {"name": city, "count": 1, "language": "en", "format": "json"}
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        results = (r.json() or {}).get("results") or []
        if results:
            lat = float(results[0]["latitude"]); lon = float(results[0]["longitude"])
            display = results[0].get("name") or city
            if results[0].get("admin1"): display += ", " + results[0]["admin1"]
            if results[0].get("country"): display += ", " + results[0]["country"]
            return lat, lon, display
    except Exception:
        pass

    # 2) Nominatim
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": city, "format": "json", "limit": 1}
        headers = {"User-Agent": USER_AGENT}
        r = requests.get(url, params=params, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json() or []
        if data:
            lat = float(data[0]["lat"]); lon = float(data[0]["lon"])
            display = data[0].get("display_name", city)
            return lat, lon, display
    except Exception:
        pass

    # 3) Fuzzy fallback for common cities/landmarks
    key = ''.join(ch.lower() if ch.isalnum() or ch.isspace() else ' ' for ch in city)
    key = ' '.join(key.split())

    if 'chicago' in key:
        return 41.8781, -87.6298, "Chicago, IL, USA"
    if 'new york' in key or 'nyc' in key:
        return 40.7128, -74.0060, "New York, NY, USA"
    if 'san francisco' in key or 'sanfrancisco' in key or 'sf' in key:
        return 37.7749, -122.4194, "San Francisco, CA, USA"
    if 'millennium park' in key and 'chicago' in key:
        return 41.8826, -87.6226, "Millennium Park, Chicago, USA"
    if 'museum of science and industry' in key and 'chicago' in key:
        return 41.7906, -87.5830, "Museum of Science and Industry, Chicago, USA"

    raise ValueError("Location not found")

def openmeteo_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,precipitation,wind_speed_10m",
        "forecast_days": 1,
    }
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    return r.json()

def openmeteo_air(lat, lon):
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {"latitude": lat, "longitude": lon, "hourly": "pm2_5"}
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    return r.json()

def osrm_route(src, dst):
    """src, dst are (lon, lat). Returns (km, minutes) or (None, None)."""
    url = f"https://router.project-osrm.org/route/v1/driving/{src[0]},{src[1]};{dst[0]},{dst[1]}"
    params = {"overview": "false", "alternatives": "false", "steps": "false"}
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    j = r.json()
    if j.get("routes"):
        sec = j["routes"][0]["duration"]
        km = j["routes"][0]["distance"] / 1000.0
        return km, sec / 60.0
    return None, None

# ---------- Simple “intelligence” ----------

def comfort_score(temp_c, pm25, precip_mm, wind_mps):
    """Very simple rule-based score out of 100."""
    score = 100
    # temp
    if temp_c is not None:
        if temp_c < 5 or temp_c > 32:
            score -= 25
        elif temp_c < 10 or temp_c > 28:
            score -= 10
    # pm2.5
    if pm25 is not None:
        if pm25 > 100:
            score -= 40
        elif pm25 > 55:
            score -= 25
        elif pm25 > 35:
            score -= 10
    # precip
    if (precip_mm or 0) > 1:
        score -= 20
    # wind (m/s)
    if (wind_mps or 0) > 10:  # ~36 kph
        score -= 10
    return max(0, score)

def analyze_and_recommend(w_hourly, a_hourly):
    try:
        temp = w_hourly["hourly"]["temperature_2m"][0]
        precip = w_hourly["hourly"]["precipitation"][0]
        wind = w_hourly["hourly"]["wind_speed_10m"][0]
    except Exception:
        temp = precip = wind = None

    try:
        pm25 = a_hourly["hourly"]["pm2_5"][0]
    except Exception:
        pm25 = None

    score = comfort_score(temp, pm25, precip, wind)
    if score >= 75:
        rec = "Great time to go out. Consider outdoor activities."
    elif score >= 50:
        rec = "Okay to go out. Bring a light jacket/mask if sensitive."
    else:
        rec = "Consider indoor plans or reschedule."
    return score, rec, {"temp_c": temp, "pm25": pm25, "precip_mm": precip, "wind": wind}

# ---------- GUI ----------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("780x560")
        self._make_widgets()

    def _make_widgets(self):
        frm = ttk.Frame(self, padding=12)
        frm.pack(fill="both", expand=True)

        row1 = ttk.Frame(frm); row1.pack(fill="x", pady=6)
        ttk.Label(row1, text="City or Address:").pack(side="left")
        self.city_var = tk.StringVar(value="Chicago, IL")
        tk.Entry(row1, textvariable=self.city_var, width=40).pack(side="left", padx=6)
        ttk.Button(row1, text="Plan", command=self.run_plan).pack(side="left")

        row2 = ttk.Frame(frm); row2.pack(fill="x", pady=6)
        ttk.Label(row2, text="Route: From").pack(side="left")
        self.src_var = tk.StringVar(value="Millennium Park, Chicago")
        tk.Entry(row2, textvariable=self.src_var, width=30).pack(side="left", padx=4)
        ttk.Label(row2, text="To").pack(side="left")
        self.dst_var = tk.StringVar(value="Museum of Science and Industry, Chicago")
        tk.Entry(row2, textvariable=self.dst_var, width=30).pack(side="left", padx=4)
        ttk.Button(row2, text="Route", command=self.run_route).pack(side="left")

        self.out = tk.Text(frm, height=24)
        self.out.pack(fill="both", expand=True, pady=8)

    def log(self, s: str):
        self.out.insert("end", s + "\n")
        self.out.see("end")

    def run_plan(self):
        self.out.delete("1.0", "end")
        city = self.city_var.get().strip()
        try:
            lat, lon, disp = geocode(city)
            self.log(f"[Location] {disp} -> lat={lat:.4f}, lon={lon:.4f}")

            w = openmeteo_weather(lat, lon)
            a = openmeteo_air(lat, lon)
            score, rec, metrics = analyze_and_recommend(w, a)

            self.log(
                "[Weather] temp=%s°C precip=%s mm wind(m/s)=%s"
                % (metrics.get("temp_c"), metrics.get("precip_mm"), metrics.get("wind"))
            )
            self.log("[Air] pm2.5(hourly)=%s  OpenAQ nearest=N/A" % (metrics.get("pm25"),))
            self.log("[Comfort Score] %d/100 — %s" % (score, rec))
            self.log("Done.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def run_route(self):
        self.out.delete("1.0", "end")
        try:
            s_lat, s_lon, _ = geocode(self.src_var.get().strip())
            d_lat, d_lon, _ = geocode(self.dst_var.get().strip())
            km, minutes = osrm_route((s_lon, s_lat), (d_lon, d_lat))
            if km is None:
                self.log("Route not found.")
            else:
                self.log(f"[Route] distance={km:.1f} km, duration={minutes:.0f} minutes (OSRM)")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    App().mainloop()
