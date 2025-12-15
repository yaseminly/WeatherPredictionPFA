# config.py
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
DATA_DIR = BASE_DIR / "data"

# Chemins de tous les datasets
DATASET_PATH = DATA_DIR / "temperature.csv"

HUMIDITY_PATH = DATA_DIR / "humidity.csv"
PRESSURE_PATH = DATA_DIR / "pressure.csv"
WIND_SPEED_PATH = DATA_DIR / "wind_speed.csv"
WIND_DIRECTION_PATH = DATA_DIR / "wind_direction.csv"
WEATHER_DESC_PATH = DATA_DIR / "weather_description.csv"
CITY_ATTRIBUTES_PATH = DATA_DIR / "city_attributes.csv"

# Configuration
DEFAULT_CITY = "New York"
FORECAST_DAYS = 7