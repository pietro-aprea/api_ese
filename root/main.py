import requests
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

def get_coordinates(city: str):
    """Geocodifica: Nominatim OpenStreetMap"""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": city, "format": "json", "limit": 1}
    headers = {"User-Agent": "world-info-app"}
    resp = requests.get(url, params=params, headers=headers)
    if resp.status_code != 200 or not resp.json():
        return None
    d = resp.json()[0]
    return float(d["lat"]), float(d["lon"]), d["display_name"]

def get_weather_and_time(lat: float, lon: float):
    """Open-Meteo: meteo + orario locale"""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "timezone": "auto"  # molto importante!
    }
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        return None
    return resp.json()

@app.get("/info")
def info(city: str = Query(...)):
    coords = get_coordinates(city)
    if not coords:
        return JSONResponse(status_code=404, content={"errore": "Città non trovata"})

    lat, lon, name = coords
    data = get_weather_and_time(lat, lon)
    if not data or "current_weather" not in data:
        return JSONResponse(status_code=500, content={"errore": "Errore nel recupero dati meteo/orario"})

    current = data["current_weather"]

    return {
        "città": name,
        "latitudine": lat,
        "longitudine": lon,
        "fuso_orario": data.get("timezone", "sconosciuto"),
        "orario_locale": current.get("time", "n.d."),
        "meteo": {
            "temperatura_°C": current["temperature"],
            "vento_km/h": current["windspeed"],
            "codice_meteo": current["weathercode"]
        }
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
