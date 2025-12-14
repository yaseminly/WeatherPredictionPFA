# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from models.weather_model import load_and_clean_data, get_city_data, train_and_predict, get_city_info
from config import DEFAULT_CITY, FORECAST_DAYS

st.set_page_config(
    page_title="Météo Prévue – Prédiction Climatique",
    page_icon="🌤️",
    layout="wide"
)

st.title("🌤️ Prédiction Météo Avancée")
st.markdown("Application de prédiction basée sur 6 paramètres météorologiques")

@st.cache_data
def load_data():
    return load_and_clean_data()

df = load_data()

# Sidebar pour sélection
with st.sidebar:
    st.header("⚙️ Configuration")
    cities = sorted(df["City"].unique())
    selected_city = st.selectbox(
        "📍 Choisir une ville", 
        cities, 
        index=cities.index(DEFAULT_CITY) if DEFAULT_CITY in cities else 0
    )
    
    # Afficher les infos de la ville
    city_info = get_city_info(df, selected_city)
    if city_info:
        st.info(f"""
        **Pays:** {city_info['country']}  
        **Latitude:** {city_info['latitude']:.2f}  
        **Longitude:** {city_info['longitude']:.2f}
        """)

# Colonnes pour les métriques
col1, col2, col3 = st.columns(3)

with col1:
    recent_temp = df[df["City"] == selected_city]["AvgTemperature"].tail(1).values[0]
    st.metric("🌡️ Température actuelle", f"{recent_temp:.1f}°C")

with col2:
    recent_humidity = df[df["City"] == selected_city]["Humidity"].tail(1).values[0]
    st.metric("💧 Humidité", f"{recent_humidity:.0f}%")

with col3:
    recent_wind = df[df["City"] == selected_city]["WindSpeed"].tail(1).values[0]
    st.metric("💨 Vitesse du vent", f"{recent_wind:.1f} m/s")

st.markdown("---")

if st.button("🔮 Prédire la météo", type="primary"):
    with st.spinner(f"Analyse des données pour {selected_city}..."):
        city_data = get_city_data(df, selected_city)
        
        if city_data is None or city_data.empty:
            st.error(f"Aucune donnée historique pour {selected_city}.")
        else:
            forecast = train_and_predict(city_data, periods=FORECAST_DAYS)
            
            # Extraire les prédictions
            next_7_days = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(FORECAST_DAYS).copy()
            next_7_days["Date"] = pd.to_datetime(next_7_days["ds"]).dt.date
            next_7_days["Température (°C)"] = next_7_days["yhat"].round(1)
            next_7_days["Min (°C)"] = next_7_days["yhat_lower"].round(1)
            next_7_days["Max (°C)"] = next_7_days["yhat_upper"].round(1)
            
            # Afficher le tableau
            st.subheader(f"📊 Prévisions pour {selected_city}")
            st.dataframe(
                next_7_days[["Date", "Température (°C)", "Min (°C)", "Max (°C)"]], 
                use_container_width=True,
                hide_index=True
            )
            
            # Graphique avec intervalle de confiance
            st.subheader("📈 Visualisation des prévisions")
            
            fig = go.Figure()
            
            # Données historiques
            historical = forecast.head(len(forecast) - FORECAST_DAYS)
            fig.add_trace(go.Scatter(
                x=historical["ds"],
                y=historical["yhat"],
                mode='lines',
                name='Historique',
                line=dict(color='blue', width=2)
            ))
            
            # Prédictions
            predictions = forecast.tail(FORECAST_DAYS)
            fig.add_trace(go.Scatter(
                x=predictions["ds"],
                y=predictions["yhat"],
                mode='lines+markers',
                name='Prédictions',
                line=dict(color='red', width=3),
                marker=dict(size=8)
            ))
            
            # Intervalle de confiance
            fig.add_trace(go.Scatter(
                x=predictions["ds"],
                y=predictions["yhat_upper"],
                mode='lines',
                name='Max',
                line=dict(width=0),
                showlegend=False
            ))
            
            fig.add_trace(go.Scatter(
                x=predictions["ds"],
                y=predictions["yhat_lower"],
                mode='lines',
                name='Intervalle de confiance',
                line=dict(width=0),
                fillcolor='rgba(255, 0, 0, 0.2)',
                fill='tonexty'
            ))
            
            fig.update_layout(
                title=f"Prévision de température à {selected_city}",
                xaxis_title="Date",
                yaxis_title="Température (°C)",
                hovermode='x unified',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("🔬 Données: Kaggle Historical Hourly Weather Data (2012-2017) | 6 paramètres: Température, Humidité, Pression, Vent, Direction, Description")