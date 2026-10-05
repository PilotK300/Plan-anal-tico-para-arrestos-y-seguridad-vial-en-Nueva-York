"""Descarga y documenta las dos fuentes complementarias del bono."""

# Las dependencias externas se limitan a HTTP y a las dos gráficas reproducibles.
import csv
import hashlib
import html
import io
import json
import os
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import requests


# Resolvemos rutas desde este archivo para poder ejecutar el programa desde cualquier carpeta.
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "datos"
FIGURES = ROOT / "figuras"
POPULATION_PAGE = "https://healthweb-back.health.ny.gov/statistics/cancer/registry/population.htm"
OPEN_METEO_API = "https://archive-api.open-meteo.com/v1/archive"
OPEN_WEATHER_API = "https://api.openweathermap.org/data/2.5/weather"
BOROUGHS = {"Bronx": "Bronx", "Kings": "Brooklyn", "New York": "Manhattan",
            "Queens": "Queens", "Richmond": "Staten Island"}


def write_csv(path, fieldnames, rows):
    """Guarda una tabla pequeña con nombres de columna explícitos."""
    # Un salto de línea uniforme y UTF-8 facilitan la lectura desde Spark y hojas de cálculo.
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def scrape_population():
    """Lee el HTML oficial y la tabla CSV del tablero enlazado allí."""
    # La ruta antigua del PDF (appendix/neighborhoodpop.htm) ya responde 404.
    # La página actual del mismo organismo incrusta el tablero de población de Tableau.
    response = requests.get(POPULATION_PAGE, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    response.raise_for_status()
    match = re.search(r"<param\s+name=['\"]name['\"]\s+value=['\"]([^'\"]+)", response.text)
    if not match:
        raise ValueError("La página oficial no contiene el identificador del tablero.")

    # Extraemos el identificador desde el HTML, sin depender de una ruta CSV fija.
    view = html.unescape(match.group(1))
    if not re.fullmatch(r"[A-Za-z0-9_/-]+", view):
        raise ValueError("El identificador del tablero tiene caracteres inesperados.")
    csv_url = f"https://public.tableau.com/views/{view}.csv?:showVizHome=no"
    table_response = requests.get(csv_url, timeout=30)
    table_response.raise_for_status()
    raw = table_response.content
    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    if not rows or set(rows[0]) != {"County", "Sex", "Pop"}:
        raise ValueError("Cambió la estructura de la tabla pública de población.")

    # Validamos cada valor numérico antes de persistir o graficar la tabla.
    cleaned = []
    for row in rows:
        population = int(row["Pop"].replace(",", ""))
        if population < 0:
            raise ValueError("La tabla contiene una población negativa.")
        cleaned.append({"county": row["County"], "sex": row["Sex"], "population": population})
    DATA.joinpath("bono_poblacion_tabla.csv").write_bytes(raw)
    selected = [
        {"borough": BOROUGHS[row["county"]], "county": row["county"],
         "population": row["population"]}
        for row in cleaned
        if row["county"] in BOROUGHS and row["sex"] == "Male and Female"
    ]
    if len(selected) != 5:
        raise ValueError("No se recuperaron los cinco condados de NYC.")
    selected.sort(key=lambda row: row["population"], reverse=True)
    write_csv(DATA / "bono_poblacion_nyc.csv", ["borough", "county", "population"], selected)

    # El tablero identifica estas cifras como promedios anuales de 2019 a 2023.
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    ax.barh([row["borough"] for row in reversed(selected)],
            [row["population"] / 1_000_000 for row in reversed(selected)], color="#1565A3")
    ax.set(xlabel="Millones de personas", title="Población media anual por borough, 2019–2023")
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(FIGURES / "bono_poblacion_nyc.png", dpi=180)
    plt.close(fig)
    return {"source_page": POPULATION_PAGE, "table_url": csv_url,
            "sha256_csv": hashlib.sha256(raw).hexdigest(), "rows": len(rows),
            "nyc_boroughs": selected, "period": "2019-2023 (promedio anual)"}


def fetch_open_meteo():
    """Consulta el reanálisis ERA5 para un contexto climático ejecutable sin clave."""
    # Usamos cinco años completos y una ubicación explícita del centro de NYC.
    params = {"latitude": 40.7128, "longitude": -74.0060,
              "start_date": "2021-01-01", "end_date": "2025-12-31",
              "daily": "temperature_2m_mean,precipitation_sum",
              "timezone": "America/New_York", "models": "era5"}
    response = requests.get(OPEN_METEO_API, params=params, timeout=90)
    response.raise_for_status()
    payload = response.json()
    daily = payload["daily"]
    dates = daily["time"]
    temperatures = daily["temperature_2m_mean"]
    precipitation = daily["precipitation_sum"]
    if not (len(dates) == len(temperatures) == len(precipitation) == 1826):
        raise ValueError("La serie climática no cubre todos los días de 2021 a 2025.")

    # Conservamos la respuesta original y una tabla plana apta para PySpark.
    raw = response.content
    (DATA / "bono_clima_openmeteo_era5.json").write_bytes(raw)
    daily_rows = [
        {"date": date, "temperature_mean_c": temp, "precipitation_mm": rain}
        for date, temp, rain in zip(dates, temperatures, precipitation)
    ]
    write_csv(DATA / "bono_clima_diario.csv",
              ["date", "temperature_mean_c", "precipitation_mm"], daily_rows)

    # Para cada mes calendario promediamos temperatura diaria y lluvia mensual anual.
    by_year_month = defaultdict(lambda: {"temps": [], "rain": []})
    for row in daily_rows:
        if row["temperature_mean_c"] is None or row["precipitation_mm"] is None:
            raise ValueError("Hay días sin temperatura o precipitación en el reanálisis.")
        key = row["date"][:7]
        by_year_month[key]["temps"].append(row["temperature_mean_c"])
        by_year_month[key]["rain"].append(row["precipitation_mm"])
    monthly_rows = []
    for month in range(1, 13):
        months = [value for key, value in by_year_month.items() if int(key[-2:]) == month]
        monthly_rows.append({"month": month,
                             "temperature_mean_c": round(mean(mean(x["temps"]) for x in months), 2),
                             "precipitation_monthly_mm": round(mean(sum(x["rain"]) for x in months), 2)})
    write_csv(DATA / "bono_clima_mensual.csv",
              ["month", "temperature_mean_c", "precipitation_monthly_mm"], monthly_rows)

    # Las dos variables comparten el eje temporal y conservan sus unidades distintas.
    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    months = [row["month"] for row in monthly_rows]
    ax.plot(months, [row["temperature_mean_c"] for row in monthly_rows],
            marker="o", color="#C1512D", label="Temperatura media (°C)")
    ax.set(xlabel="Mes", ylabel="Temperatura media (°C)", xticks=months,
           title="Nueva York: patrón mensual del reanálisis ERA5, 2021–2025")
    ax.grid(alpha=0.2)
    second = ax.twinx()
    second.bar(months, [row["precipitation_monthly_mm"] for row in monthly_rows],
               color="#2980B9", alpha=0.35, label="Precipitación mensual (mm)")
    second.set_ylabel("Precipitación mensual media (mm)")
    fig.tight_layout()
    fig.savefig(FIGURES / "bono_clima_mensual.png", dpi=180)
    plt.close(fig)
    return {"api_url_without_query": OPEN_METEO_API, "sha256_json": hashlib.sha256(raw).hexdigest(),
            "days": len(daily_rows), "model": "ERA5", "period": "2021-2025",
            "requested_location": {"latitude": 40.7128, "longitude": -74.0060},
            "returned_location": {"latitude": payload["latitude"], "longitude": payload["longitude"]},
            "monthly": monthly_rows}


def fetch_open_weather():
    """Consulta la API exigida por el PDF solo si existe una clave configurada."""
    # La clave se lee del entorno y jamás se escribe en el repositorio ni en las salidas.
    key = os.environ.get("OPENWEATHER_API_KEY") or os.environ.get("OWM_API_KEY")
    if not key:
        return {"status": "pendiente_clave", "reason": "OpenWeatherMap exige una clave de API."}
    params = {"lat": 40.7128, "lon": -74.0060, "appid": key, "units": "metric"}
    response = requests.get(OPEN_WEATHER_API, params=params, timeout=30)
    if response.status_code != 200:
        return {"status": "error_api", "http_status": response.status_code}
    payload = response.json()
    observation = {"timestamp_utc": datetime.fromtimestamp(payload["dt"], timezone.utc).isoformat(),
                   "temperature_c": payload["main"]["temp"],
                   "humidity_percent": payload["main"]["humidity"],
                   "weather": payload["weather"][0]["main"],
                   "location": payload["name"]}
    write_csv(DATA / "bono_openweather_actual.csv", list(observation), [observation])
    return {"status": "ejecutado", "observation": observation,
            "caution": "Es una observación actual, no una serie climática ni histórica."}


def main():
    """Ejecuta ambas vías y deja un manifiesto que separa resultados y pendientes."""
    # Creamos carpetas si el repositorio se acaba de clonar.
    DATA.mkdir(exist_ok=True)
    FIGURES.mkdir(exist_ok=True)
    result = {"retrieved_utc": datetime.now(timezone.utc).isoformat(),
              "population": scrape_population(),
              "climate_open_meteo": fetch_open_meteo(),
              "climate_open_weather": fetch_open_weather()}
    (DATA / "bono_manifest.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Bono: población y clima alternativo descargados; OpenWeatherMap:",
          result["climate_open_weather"]["status"])


if __name__ == "__main__":
    main()
