import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class WeatherAPIClient:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    def get_current_weather(self, city):
        """Récupère la météo actuelle pour une ville"""
        url = f"{self.base_url}/weather"
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric',
            'lang': 'fr'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erreur API: {e}")
            return None
    
    def get_forecast(self, city):
        """Récupère les prévisions sur 5 jours (gratuit)"""
        url = f"{self.base_url}/forecast"
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric',
            'lang': 'fr'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erreur API: {e}")
            return None
    
    def get_historical_data(self, city, days=30):
        """Simule des données historiques (version simplifiée)"""
        # Note: L'API gratuite ne fournit pas d'historique
        # On utilise les prévisions actuelles comme base
        import pandas as pd
        import numpy as np
        from datetime import timedelta
        
        current = self.get_current_weather(city)
        if not current:
            return None
        
        # Génération de données simulées basées sur la température actuelle
        base_temp = current['main']['temp']
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        data = {
            'date': dates,
            'temp': base_temp + np.random.normal(0, 3, days),
            'humidity': current['main']['humidity'] + np.random.normal(0, 10, days),
            'pressure': current['main']['pressure'] + np.random.normal(0, 5, days),
            'wind_speed': current['wind']['speed'] + np.random.normal(0, 2, days)
        }
        
        return pd.DataFrame(data)