# models/weather_model.py
import pandas as pd
import numpy as np
from pathlib import Path

from config import (
    DATASET_PATH, 
    HUMIDITY_PATH, 
    PRESSURE_PATH, 
    WIND_SPEED_PATH,
    WIND_DIRECTION_PATH,
    WEATHER_DESC_PATH,
    CITY_ATTRIBUTES_PATH
)

def load_and_clean_data():
    """Charge et nettoie tous les datasets météorologiques."""
    # Charger tous les fichiers
    df_temp = pd.read_csv(DATASET_PATH)
    df_humidity = pd.read_csv(HUMIDITY_PATH)
    df_pressure = pd.read_csv(PRESSURE_PATH)
    df_wind_speed = pd.read_csv(WIND_SPEED_PATH)
    df_wind_dir = pd.read_csv(WIND_DIRECTION_PATH)
    df_weather_desc = pd.read_csv(WEATHER_DESC_PATH)
    
    # Convertir datetime pour tous
    for df in [df_temp, df_humidity, df_pressure, df_wind_speed, df_wind_dir, df_weather_desc]:
        df["datetime"] = pd.to_datetime(df["datetime"])
    
    # Liste des villes
    city_columns = [col for col in df_temp.columns if col != "datetime"]
    
    # Convertir Kelvin → Celsius pour température
    for col in city_columns:
        df_temp[col] = df_temp[col] - 273.15
    
    # Agréger par jour (moyenne quotidienne pour numériques, mode pour descriptions)
    for df in [df_temp, df_humidity, df_pressure, df_wind_speed, df_wind_dir, df_weather_desc]:
        df["date"] = df["datetime"].dt.date
    
    # Moyennes quotidiennes
    daily_temp = df_temp.groupby("date")[city_columns].mean().reset_index()
    daily_humidity = df_humidity.groupby("date")[city_columns].mean().reset_index()
    daily_pressure = df_pressure.groupby("date")[city_columns].mean().reset_index()
    daily_wind_speed = df_wind_speed.groupby("date")[city_columns].mean().reset_index()
    daily_wind_dir = df_wind_dir.groupby("date")[city_columns].mean().reset_index()
    
    # Mode pour les descriptions météo
    daily_weather_desc = df_weather_desc.groupby("date")[city_columns].agg(lambda x: x.mode()[0] if len(x.mode()) > 0 else None).reset_index()
    
    # Convertir toutes les dates en datetime
    daily_temp["date"] = pd.to_datetime(daily_temp["date"])
    daily_humidity["date"] = pd.to_datetime(daily_humidity["date"])
    daily_pressure["date"] = pd.to_datetime(daily_pressure["date"])
    daily_wind_speed["date"] = pd.to_datetime(daily_wind_speed["date"])
    daily_wind_dir["date"] = pd.to_datetime(daily_wind_dir["date"])
    daily_weather_desc["date"] = pd.to_datetime(daily_weather_desc["date"])
    
    # Transformer en format long
    df_long = daily_temp.melt(id_vars=["date"], var_name="City", value_name="AvgTemperature")
    df_long = df_long.dropna(subset=["AvgTemperature"])
    
    # Ajouter tous les autres paramètres
    humidity_long = daily_humidity.melt(id_vars=["date"], var_name="City", value_name="Humidity")
    pressure_long = daily_pressure.melt(id_vars=["date"], var_name="City", value_name="Pressure")
    wind_speed_long = daily_wind_speed.melt(id_vars=["date"], var_name="City", value_name="WindSpeed")
    wind_dir_long = daily_wind_dir.melt(id_vars=["date"], var_name="City", value_name="WindDirection")
    weather_desc_long = daily_weather_desc.melt(id_vars=["date"], var_name="City", value_name="WeatherDesc")
    
    df_long = df_long.merge(humidity_long, on=["date", "City"], how="left")
    df_long = df_long.merge(pressure_long, on=["date", "City"], how="left")
    df_long = df_long.merge(wind_speed_long, on=["date", "City"], how="left")
    df_long = df_long.merge(wind_dir_long, on=["date", "City"], how="left")
    df_long = df_long.merge(weather_desc_long, on=["date", "City"], how="left")
    
    # Ajouter les attributs des villes (latitude, longitude, pays)
    try:
        city_attrs = pd.read_csv(CITY_ATTRIBUTES_PATH)
        df_long = df_long.merge(city_attrs, on="City", how="left")
    except:
        pass
    
    return df_long

def get_city_data(df, city_name):
    """Extrait les données complètes d'une ville."""
    city_name = city_name.strip()
    
    columns_to_keep = ["date", "AvgTemperature", "Humidity", "Pressure", 
                       "WindSpeed", "WindDirection", "WeatherDesc"]
    
    # Filtrer les colonnes qui existent
    available_cols = [col for col in columns_to_keep if col in df.columns]
    
    city_df = df[df["City"] == city_name][available_cols].copy()
    if city_df.empty:
        return None
    
    city_df.rename(columns={"date": "ds", "AvgTemperature": "y"}, inplace=True)
    city_df.sort_values("ds", inplace=True)
    city_df.reset_index(drop=True, inplace=True)
    
    return city_df

def train_and_predict(model_data, periods=7):
    """
    Prédit les N prochains jours en utilisant tous les paramètres météo disponibles.
    """
    # Calcul de la moyenne mobile sur les 30 derniers jours
    window = min(30, len(model_data))
    recent_avg = model_data["y"].tail(window).mean()
    
    # Calcul de la tendance (variation sur les 60 derniers jours)
    if len(model_data) >= 60:
        old_avg = model_data["y"].tail(60).head(30).mean()
        trend = (recent_avg - old_avg) / 30
    else:
        trend = 0
    
    # Extraction des informations temporelles
    model_data_copy = model_data.copy()
    model_data_copy["day_of_year"] = pd.to_datetime(model_data_copy["ds"]).dt.dayofyear
    model_data_copy["month"] = pd.to_datetime(model_data_copy["ds"]).dt.month
    model_data_copy["week_of_year"] = pd.to_datetime(model_data_copy["ds"]).dt.isocalendar().week
    
    # Calcul de l'effet saisonnier (moyenne par jour de l'année)
    seasonal_effect = model_data_copy.groupby("day_of_year")["y"].mean()
    overall_mean = model_data_copy["y"].mean()
    
    # Calcul des facteurs basés sur les autres paramètres météo
    humidity_factor = 0
    pressure_factor = 0
    wind_factor = 0
    
    # Ajustement basé sur l'humidité
    if "Humidity" in model_data.columns and model_data["Humidity"].notna().sum() > 30:
        recent_humidity = model_data["Humidity"].tail(window).mean()
        avg_humidity = model_data["Humidity"].mean()
        humidity_factor = (recent_humidity - avg_humidity) * 0.015
    
    # Ajustement basé sur la pression
    if "Pressure" in model_data.columns and model_data["Pressure"].notna().sum() > 30:
        recent_pressure = model_data["Pressure"].tail(window).mean()
        avg_pressure = model_data["Pressure"].mean()
        pressure_factor = (recent_pressure - avg_pressure) * 0.008
    
    # Ajustement basé sur la vitesse du vent
    if "WindSpeed" in model_data.columns and model_data["WindSpeed"].notna().sum() > 30:
        recent_wind = model_data["WindSpeed"].tail(window).mean()
        avg_wind = model_data["WindSpeed"].mean()
        wind_factor = (recent_wind - avg_wind) * 0.1
    
    # Génération des prédictions
    last_date = model_data["ds"].max()
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=periods)
    
    predictions = []
    uncertainties = []
    
    for i, date in enumerate(future_dates):
        day_of_year = date.dayofyear
        
        # Prédiction de base avec tendance
        base_pred = recent_avg + trend * (i + 1)
        
        # Ajout de l'effet saisonnier
        if day_of_year in seasonal_effect.index:
            seasonal_adj = seasonal_effect[day_of_year] - overall_mean
            pred = base_pred + seasonal_adj * 0.6
        else:
            pred = base_pred
        
        # Ajustements basés sur les paramètres météo
        pred += humidity_factor + pressure_factor + wind_factor
        
        # Calcul de l'incertitude (augmente avec le temps)
        uncertainty = 2 + (i * 0.5)
        
        predictions.append(pred)
        uncertainties.append(uncertainty)
    
    # Construction du dataframe de résultats
    forecast = pd.DataFrame({
        "ds": list(model_data["ds"]) + list(future_dates),
        "yhat": list(model_data["y"]) + predictions,
        "yhat_lower": list(model_data["y"]) + [p - u for p, u in zip(predictions, uncertainties)],
        "yhat_upper": list(model_data["y"]) + [p + u for p, u in zip(predictions, uncertainties)]
    })
    
    return forecast

def get_city_info(df, city_name):
    """Retourne les informations d'une ville (pays, coordonnées)."""
    city_name = city_name.strip()
    city_info = df[df["City"] == city_name].iloc[0] if not df[df["City"] == city_name].empty else None
    
    if city_info is not None and "Country" in df.columns:
        return {
            "country": city_info.get("Country", "N/A"),
            "latitude": city_info.get("Latitude", "N/A"),
            "longitude": city_info.get("Longitude", "N/A")
        }
    return None