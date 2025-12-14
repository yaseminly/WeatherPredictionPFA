# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from models.weather_model import load_and_clean_data, get_city_data, train_and_predict, get_city_info
from config import DEFAULT_CITY, FORECAST_DAYS

# Configuration de la page
st.set_page_config(
    page_title="SamYasWeather - Prévisions Météo",
    page_icon="⛅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personnalisé pour un look moderne
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #e3f2fd 0%, #fff3e0 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #e3f2fd 0%, #fff3e0 100%);
    }
    .weather-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
        backdrop-filter: blur(10px);
        margin: 20px 0;
        border: 1px solid rgba(255, 255, 255, 0.5);
    }
    .metric-card {
        background: linear-gradient(135deg, #90caf9 0%, #ffb74d 100%);
        border-radius: 15px;
        padding: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    .temp-display {
        font-size: 72px;
        font-weight: bold;
        color: #42a5f5;
        text-align: center;
        margin: 20px 0;
    }
    .city-name {
        font-size: 42px;
        font-weight: 600;
        color: #1976d2;
        text-align: center;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(255,255,255,0.5);
    }
    .date-display {
        font-size: 18px;
        color: #5e35b1;
        text-align: center;
        margin-bottom: 30px;
    }
    .forecast-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s;
    }
    .forecast-card:hover {
        transform: translateY(-5px);
    }
    h1, h2, h3 {
        color: #1976d2 !important;
    }
    .stSelectbox label {
        color: #1976d2 !important;
        font-weight: 600;
    }
    .stSelectbox > div > div {
        background-color: white;
        border-radius: 10px;
        border: 2px solid #90caf9;
    }
    .header {
        background: linear-gradient(135deg, #42a5f5 0%, #ff7043 100%);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        margin-bottom: 30px;
    }
    .header-title {
        font-size: 48px;
        font-weight: bold;
        color: white;
        text-align: center;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    .header-subtitle {
        font-size: 16px;
        color: rgba(255, 255, 255, 0.95);
        text-align: center;
        margin-top: 10px;
    }
    .footer {
        background: linear-gradient(135deg, #42a5f5 0%, #ff7043 100%);
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        margin-top: 50px;
        color: white;
    }
    .footer-content {
        text-align: center;
    }
    .footer-title {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 15px;
        color: white;
    }
    .footer-divider {
        width: 100px;
        height: 3px;
        background: white;
        margin: 20px auto;
        border-radius: 2px;
    }
    .footer-credits {
        font-size: 18px;
        margin: 15px 0;
        font-weight: 500;
    }
    .footer-info {
        font-size: 14px;
        opacity: 0.9;
        line-height: 1.8;
    }
</style>
""", unsafe_allow_html=True)

# Fonction pour obtenir l'emoji météo
def get_weather_emoji(temp, desc=None):
    if desc:
        desc_lower = str(desc).lower()
        if "rain" in desc_lower or "drizzle" in desc_lower:
            return "🌧️"
        elif "snow" in desc_lower:
            return "❄️"
        elif "cloud" in desc_lower:
            return "☁️"
        elif "clear" in desc_lower or "sun" in desc_lower:
            return "☀️"
        elif "storm" in desc_lower or "thunder" in desc_lower:
            return "⛈️"
    
    if temp > 30:
        return "🌡️"
    elif temp > 20:
        return "☀️"
    elif temp > 10:
        return "⛅"
    elif temp > 0:
        return "☁️"
    else:
        return "❄️"

@st.cache_data
def load_data():
    return load_and_clean_data()

# Charger les données
df = load_data()
cities = sorted(df["City"].unique())

# Header
st.markdown("""
<div class="header">
    <h1 class="header-title">⛅ SamYasWeather</h1>
    <p class="header-subtitle">🌍 Prévisions météorologiques intelligentes • 📊 Analyse de données en temps réel • 🤖 Powered by AI</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Sélection de ville centrée
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    selected_city = st.selectbox(
        "🌍 Sélectionnez votre ville",
        cities,
        index=cities.index(DEFAULT_CITY) if DEFAULT_CITY in cities else 0
    )

# Obtenir les données de la ville
city_data_full = df[df["City"] == selected_city]
if not city_data_full.empty:
    latest_data = city_data_full.iloc[-1]
    current_temp = latest_data["AvgTemperature"]
    current_humidity = latest_data.get("Humidity", 0)
    current_pressure = latest_data.get("Pressure", 0)
    current_wind = latest_data.get("WindSpeed", 0)
    current_desc = latest_data.get("WeatherDesc", "")
    
    city_info = get_city_info(df, selected_city)
    
    # Date actuelle
    now = datetime.now()
    st.markdown(f'<div class="city-name">{selected_city}</div>', unsafe_allow_html=True)
    
    if city_info:
        st.markdown(f'<div class="date-display">📍 {city_info["country"]} | {now.strftime("%A, %d %B %Y")}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="date-display">{now.strftime("%A, %d %B %Y")}</div>', unsafe_allow_html=True)
    
    # Carte météo principale
    st.markdown('<div class="weather-card">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        weather_icon = get_weather_emoji(current_temp, current_desc)
        st.markdown(f'<div style="text-align: center; font-size: 120px;">{weather_icon}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="temp-display">{current_temp:.1f}°C</div>', unsafe_allow_html=True)
        if current_desc:
            st.markdown(f'<p style="text-align: center; font-size: 24px; color: #666; margin-top: -10px;">{current_desc}</p>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Métriques météo
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 40px;">💧</div>
            <div style="font-size: 28px; font-weight: bold; margin: 10px 0;">{current_humidity:.0f}%</div>
            <div style="font-size: 14px; opacity: 0.9;">Humidité</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 40px;">🌡️</div>
            <div style="font-size: 28px; font-weight: bold; margin: 10px 0;">{current_pressure:.0f} hPa</div>
            <div style="font-size: 14px; opacity: 0.9;">Pression</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 40px;">💨</div>
            <div style="font-size: 28px; font-weight: bold; margin: 10px 0;">{current_wind:.1f} m/s</div>
            <div style="font-size: 14px; opacity: 0.9;">Vent</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        feels_like = current_temp - (current_wind * 0.5)
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 40px;">🌡️</div>
            <div style="font-size: 28px; font-weight: bold; margin: 10px 0;">{feels_like:.1f}°C</div>
            <div style="font-size: 14px; opacity: 0.9;">Ressenti</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Prévisions 7 jours
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; margin-bottom: 30px;">📅 Prévisions sur 7 jours</h2>', unsafe_allow_html=True)
    
    with st.spinner("🔮 Calcul des prévisions..."):
        city_data = get_city_data(df, selected_city)
        
        if city_data is not None and not city_data.empty:
            forecast = train_and_predict(city_data, periods=FORECAST_DAYS)
            next_7_days = forecast.tail(FORECAST_DAYS).copy()
            
            # Afficher les cartes de prévision
            cols = st.columns(7)
            
            for idx, (i, row) in enumerate(next_7_days.iterrows()):
                date = pd.to_datetime(row["ds"])
                temp = row["yhat"]
                temp_min = row["yhat_lower"]
                temp_max = row["yhat_upper"]
                
                day_name = date.strftime("%a")
                day_num = date.strftime("%d")
                
                with cols[idx]:
                    emoji = get_weather_emoji(temp)
                    st.markdown(f"""
                    <div class="forecast-card">
                        <div style="font-weight: 600; color: #42a5f5; margin-bottom: 10px;">{day_name}</div>
                        <div style="font-size: 14px; color: #999; margin-bottom: 15px;">{day_num}</div>
                        <div style="font-size: 48px; margin: 15px 0;">{emoji}</div>
                        <div style="font-size: 24px; font-weight: bold; color: #333; margin: 10px 0;">{temp:.0f}°</div>
                        <div style="font-size: 12px; color: #999;">
                            <span style="color: #ff7043;">↑{temp_max:.0f}°</span> 
                            <span style="color: #42a5f5;">↓{temp_min:.0f}°</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Graphique de tendance
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown('<h2 style="text-align: center; margin-bottom: 30px;">📈 Tendance des températures</h2>', unsafe_allow_html=True)
            
            st.markdown('<div class="weather-card">', unsafe_allow_html=True)
            
            # Préparer les données pour le graphique
            historical = forecast.head(len(forecast) - FORECAST_DAYS).tail(30)
            predictions = forecast.tail(FORECAST_DAYS)
            
            fig = go.Figure()
            
            # Historique
            fig.add_trace(go.Scatter(
                x=historical["ds"],
                y=historical["yhat"],
                mode='lines',
                name='Historique (30 derniers jours)',
                line=dict(color='rgba(66, 165, 245, 0.8)', width=3),
                fill=None
            ))
            
            # Prédictions
            fig.add_trace(go.Scatter(
                x=predictions["ds"],
                y=predictions["yhat"],
                mode='lines+markers',
                name='Prévisions',
                line=dict(color='#ff7043', width=4),
                marker=dict(size=10, symbol='circle', color='#ff7043')
            ))
            
            # Intervalle de confiance
            fig.add_trace(go.Scatter(
                x=predictions["ds"].tolist() + predictions["ds"].tolist()[::-1],
                y=predictions["yhat_upper"].tolist() + predictions["yhat_lower"].tolist()[::-1],
                fill='toself',
                fillcolor='rgba(255, 112, 67, 0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                showlegend=True,
                name='Intervalle de confiance'
            ))
            
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Température (°C)",
                hovermode='x unified',
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333', size=12),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                xaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(200,200,200,0.2)'
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(200,200,200,0.2)'
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div class="footer">
    <div class="footer-content">
        <div class="footer-title">⛅ SamYasWeather</div>
        <div class="footer-divider"></div>
        
        <p class="footer-credits">
            💻 Développé avec passion par <strong>Yasmine</strong> & <strong>Samia</strong>
        </p>
        
        <div class="footer-info">
            <p>🔬 <strong>Sources de données:</strong> Historical Hourly Weather Data (2012-2017) • Kaggle Dataset</p>
            <p>🤖 <strong>Technologie:</strong> Python • Streamlit • Pandas • Plotly • Machine Learning</p>
            <p>📊 <strong>Paramètres analysés:</strong> Température • Humidité • Pression • Vitesse du vent • Direction du vent • Conditions météo</p>
            <p>🎯 <strong>Précision:</strong> Prédictions basées sur l'analyse de +45,000 enregistrements horaires</p>
        </div>
        
        <div class="footer-divider"></div>
        <p style="font-size: 13px; margin-top: 20px; opacity: 0.85;">
            © 2025 WeatherPro - Projet universitaire de prédiction climatique<br>
            Tous droits réservés 
        </p>
    </div>
</div>
""", unsafe_allow_html=True)