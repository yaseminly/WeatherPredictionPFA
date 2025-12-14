import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
from datetime import datetime, timedelta

class WeatherPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def prepare_features(self, df):
        """Prépare les features pour l'entraînement"""
        df = df.copy()
        
        # Extraction de features temporelles
        df['day_of_year'] = pd.to_datetime(df['date']).dt.dayofyear
        df['month'] = pd.to_datetime(df['date']).dt.month
        df['day_of_week'] = pd.to_datetime(df['date']).dt.dayofweek
        
        # Features de lag (températures précédentes)
        df['temp_lag_1'] = df['temp'].shift(1)
        df['temp_lag_2'] = df['temp'].shift(2)
        df['temp_lag_3'] = df['temp'].shift(3)
        
        # Moyenne mobile
        df['temp_rolling_mean_7'] = df['temp'].rolling(window=7, min_periods=1).mean()
        
        df = df.dropna()
        
        feature_columns = ['day_of_year', 'month', 'day_of_week', 
                          'humidity', 'pressure', 'wind_speed',
                          'temp_lag_1', 'temp_lag_2', 'temp_lag_3',
                          'temp_rolling_mean_7']
        
        X = df[feature_columns]
        y = df['temp']
        
        return X, y, feature_columns
    
    def train(self, df):
        """Entraîne le modèle"""
        X, y, self.feature_columns = self.prepare_features(df)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Normalisation
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Entraînement
        self.model.fit(X_train_scaled, y_train)
        
        # Évaluation
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        self.is_trained = True
        
        return {
            'train_score': train_score,
            'test_score': test_score,
            'n_samples': len(df)
        }
    
    def predict_next_days(self, historical_df, n_days=7):
        """Prédit la température pour les n prochains jours"""
        if not self.is_trained:
            raise ValueError("Le modèle doit être entraîné avant de faire des prédictions")
        
        predictions = []
        current_data = historical_df.copy()
        
        for i in range(n_days):
            # Préparer les features pour la prédiction
            last_row = current_data.iloc[-1:].copy()
            next_date = pd.to_datetime(last_row['date'].values[0]) + timedelta(days=1)
            
            # Créer une nouvelle ligne avec la date suivante
            new_row = pd.DataFrame({
                'date': [next_date],
                'temp': [last_row['temp'].values[0]],  # Temporaire
                'humidity': [last_row['humidity'].values[0]],
                'pressure': [last_row['pressure'].values[0]],
                'wind_speed': [last_row['wind_speed'].values[0]]
            })
            
            # Concaténer et préparer les features
            temp_df = pd.concat([current_data, new_row], ignore_index=True)
            X, _, _ = self.prepare_features(temp_df)
            
            if len(X) > 0:
                X_last = X.iloc[-1:][self.feature_columns]
                X_scaled = self.scaler.transform(X_last)
                predicted_temp = self.model.predict(X_scaled)[0]
                
                # Mettre à jour avec la température prédite
                new_row['temp'] = predicted_temp
                current_data = pd.concat([current_data, new_row], ignore_index=True)
                
                predictions.append({
                    'date': next_date,
                    'temperature': round(predicted_temp, 1)
                })
        
        return predictions
    
    def save_model(self, path='models/trained_model.pkl'):
        """Sauvegarde le modèle"""
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'is_trained': self.is_trained
        }, path)
    
    def load_model(self, path='models/trained_model.pkl'):
        """Charge le modèle"""
        try:
            data = joblib.load(path)
            self.model = data['model']
            self.scaler = data['scaler']
            self.feature_columns = data['feature_columns']
            self.is_trained = data['is_trained']
            return True
        except FileNotFoundError:
            return False