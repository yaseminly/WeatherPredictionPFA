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
    """
    Charge et nettoie tous les datasets météorologiques.
    Fusionne automatiquement le dataset original et le dataset européen.
    """
    # ========== CHARGEMENT DATASET ORIGINAL ==========
    print("📂 Chargement du dataset original...")
    df_temp = pd.read_csv(DATASET_PATH)
    df_humidity = pd.read_csv(HUMIDITY_PATH)
    df_pressure = pd.read_csv(PRESSURE_PATH)
    df_wind_speed = pd.read_csv(WIND_SPEED_PATH)
    df_wind_dir = pd.read_csv(WIND_DIRECTION_PATH)
    df_weather_desc = pd.read_csv(WEATHER_DESC_PATH)
    
    # Convertir datetime pour tous
    for df in [df_temp, df_humidity, df_pressure, df_wind_speed, df_wind_dir, df_weather_desc]:
        df["datetime"] = pd.to_datetime(df["datetime"])
    
    # Liste des villes du dataset original
    city_columns = [col for col in df_temp.columns if col != "datetime"]
    
    # Convertir Kelvin → Celsius pour température
    for col in city_columns:
        df_temp[col] = df_temp[col] - 273.15
    
    # Agréger par jour (moyenne quotidienne)
    for df in [df_temp, df_humidity, df_pressure, df_wind_speed, df_wind_dir, df_weather_desc]:
        df["date"] = df["datetime"].dt.date
    
    daily_temp = df_temp.groupby("date")[city_columns].mean().reset_index()
    daily_humidity = df_humidity.groupby("date")[city_columns].mean().reset_index()
    daily_pressure = df_pressure.groupby("date")[city_columns].mean().reset_index()
    daily_wind_speed = df_wind_speed.groupby("date")[city_columns].mean().reset_index()
    daily_wind_dir = df_wind_dir.groupby("date")[city_columns].mean().reset_index()
    daily_weather_desc = df_weather_desc.groupby("date")[city_columns].agg(
        lambda x: x.mode()[0] if len(x.mode()) > 0 else None
    ).reset_index()
    
    # Convertir dates en datetime
    daily_temp["date"] = pd.to_datetime(daily_temp["date"])
    daily_humidity["date"] = pd.to_datetime(daily_humidity["date"])
    daily_pressure["date"] = pd.to_datetime(daily_pressure["date"])
    daily_wind_speed["date"] = pd.to_datetime(daily_wind_speed["date"])
    daily_wind_dir["date"] = pd.to_datetime(daily_wind_dir["date"])
    daily_weather_desc["date"] = pd.to_datetime(daily_weather_desc["date"])
    
    # ========== CHARGEMENT DATASET EUROPÉEN ==========
    european_data_loaded = False
    try:
        print("🇪🇺 Chargement du dataset européen...")
        european_dir = "data/european_converted/"
        
        df_temp_eu = pd.read_csv(f"{european_dir}temperature_european.csv")
        df_humidity_eu = pd.read_csv(f"{european_dir}humidity_european.csv")
        df_pressure_eu = pd.read_csv(f"{european_dir}pressure_european.csv")
        df_wind_speed_eu = pd.read_csv(f"{european_dir}wind_speed_european.csv")
        df_wind_dir_eu = pd.read_csv(f"{european_dir}wind_direction_european.csv")
        df_weather_desc_eu = pd.read_csv(f"{european_dir}weather_description_european.csv")
        
        # Convertir datetime
        for df in [df_temp_eu, df_humidity_eu, df_pressure_eu, 
                   df_wind_speed_eu, df_wind_dir_eu, df_weather_desc_eu]:
            df["datetime"] = pd.to_datetime(df["datetime"])
            df["date"] = df["datetime"].dt.date
        
        # Villes européennes
        eu_city_columns = [col for col in df_temp_eu.columns if col not in ["datetime", "date"]]
        
        # Convertir Kelvin → Celsius (déjà fait lors de la conversion)
        for col in eu_city_columns:
            df_temp_eu[col] = df_temp_eu[col] - 273.15
        
        # Agréger par jour
        daily_temp_eu = df_temp_eu.groupby("date")[eu_city_columns].mean().reset_index()
        daily_humidity_eu = df_humidity_eu.groupby("date")[eu_city_columns].mean().reset_index()
        daily_pressure_eu = df_pressure_eu.groupby("date")[eu_city_columns].mean().reset_index()
        daily_wind_speed_eu = df_wind_speed_eu.groupby("date")[eu_city_columns].mean().reset_index()
        daily_wind_dir_eu = df_wind_dir_eu.groupby("date")[eu_city_columns].mean().reset_index()
        daily_weather_desc_eu = df_weather_desc_eu.groupby("date")[eu_city_columns].agg(
            lambda x: x.mode()[0] if len(x.mode()) > 0 else None
        ).reset_index()
        
        # Convertir dates
        daily_temp_eu["date"] = pd.to_datetime(daily_temp_eu["date"])
        daily_humidity_eu["date"] = pd.to_datetime(daily_humidity_eu["date"])
        daily_pressure_eu["date"] = pd.to_datetime(daily_pressure_eu["date"])
        daily_wind_speed_eu["date"] = pd.to_datetime(daily_wind_speed_eu["date"])
        daily_wind_dir_eu["date"] = pd.to_datetime(daily_wind_dir_eu["date"])
        daily_weather_desc_eu["date"] = pd.to_datetime(daily_weather_desc_eu["date"])
        
        # ========== FUSION DES DATASETS ==========
        print("🔗 Fusion des datasets...")
        
        # Fusionner les dataframes de température
        daily_temp = daily_temp.merge(daily_temp_eu, on="date", how="outer")
        daily_humidity = daily_humidity.merge(daily_humidity_eu, on="date", how="outer")
        daily_pressure = daily_pressure.merge(daily_pressure_eu, on="date", how="outer")
        daily_wind_speed = daily_wind_speed.merge(daily_wind_speed_eu, on="date", how="outer")
        daily_wind_dir = daily_wind_dir.merge(daily_wind_dir_eu, on="date", how="outer")
        daily_weather_desc = daily_weather_desc.merge(daily_weather_desc_eu, on="date", how="outer")
        
        # Mettre à jour la liste des villes
        city_columns = [col for col in daily_temp.columns if col != "date"]
        
        european_data_loaded = True
        print(f"✅ Dataset européen fusionné ! {len(eu_city_columns)} villes ajoutées")
        
    except FileNotFoundError:
        print("⚠️ Dataset européen non trouvé. Exécutez convert_european_dataset.py d'abord.")
        print("   Utilisation du dataset original uniquement.")
    except Exception as e:
        print(f"⚠️ Erreur lors du chargement du dataset européen : {e}")
        print("   Utilisation du dataset original uniquement.")
    
    # ========== TRANSFORMATION EN FORMAT LONG ==========
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
    
    # ========== AJOUTER ATTRIBUTS DES VILLES ==========
    try:
        # Essayer d'abord le fichier combiné (créé par convert_european_dataset.py)
        if Path("data/city_attributes_combined.csv").exists():
            city_attrs = pd.read_csv("data/city_attributes_combined.csv")
            print("✅ Utilisation du fichier d'attributs combiné (toutes les villes)")
        else:
            # Sinon, charger et fusionner manuellement
            city_attrs = pd.read_csv(CITY_ATTRIBUTES_PATH)
            
            if european_data_loaded:
                try:
                    city_attrs_eu = pd.read_csv("data/european_converted/city_attributes_european.csv")
                    city_attrs = pd.concat([city_attrs, city_attrs_eu], ignore_index=True)
                except:
                    pass
        
        df_long = df_long.merge(city_attrs, on="City", how="left")
    except Exception as e:
        print(f"⚠️ Erreur chargement attributs : {e}")
        pass
    
    print(f"\n📊 Dataset final : {len(df_long)} lignes, {df_long['City'].nunique()} villes")
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
    Algorithme amélioré avec plus de données.
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
    
    # Calcul de l'effet saisonnier
    seasonal_effect = model_data_copy.groupby("day_of_year")["y"].mean()
    overall_mean = model_data_copy["y"].mean()
    
    # Facteurs météo
    humidity_factor = 0
    pressure_factor = 0
    wind_factor = 0
    
    if "Humidity" in model_data.columns and model_data["Humidity"].notna().sum() > 30:
        recent_humidity = model_data["Humidity"].tail(window).mean()
        avg_humidity = model_data["Humidity"].mean()
        humidity_factor = (recent_humidity - avg_humidity) * 0.015
    
    if "Pressure" in model_data.columns and model_data["Pressure"].notna().sum() > 30:
        recent_pressure = model_data["Pressure"].tail(window).mean()
        avg_pressure = model_data["Pressure"].mean()
        pressure_factor = (recent_pressure - avg_pressure) * 0.008
    
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
        
        base_pred = recent_avg + trend * (i + 1)
        
        if day_of_year in seasonal_effect.index:
            seasonal_adj = seasonal_effect[day_of_year] - overall_mean
            pred = base_pred + seasonal_adj * 0.6
        else:
            pred = base_pred
        
        pred += humidity_factor + pressure_factor + wind_factor
        
        uncertainty = 2 + (i * 0.5)
        
        predictions.append(pred)
        uncertainties.append(uncertainty)
    
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