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

# CSS personnalisé pour un thème bleu nuit moderne
st.markdown("""
<style>
    /* Fond principal avec dégradé bleu nuit */
    .main {
        background: linear-gradient(180deg, #1a237e 0%, #283593 50%, #3949ab 100%);
    }
    .stApp {
        background: linear-gradient(180deg, #1a237e 0%, #283593 50%, #3949ab 100%);
    }
    
    /* Styles pour le bloc de contenu */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Carte météo avec effet glassmorphism */
    .weather-card {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 40px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin: 20px 0;
    }
    
    /* Cartes métriques avec dégradé subtil */
    .metric-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.15) 0%, rgba(255, 255, 255, 0.05) 100%);
        border-radius: 20px;
        padding: 25px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
    }
    
    /* Affichage de la température principale */
    .temp-display {
        font-size: 96px;
        font-weight: 300;
        color: #ffffff;
        text-align: center;
        margin: 20px 0;
        text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    
    /* Nom de la ville */
    .city-name {
        font-size: 48px;
        font-weight: 300;
        color: #ffffff;
        text-align: center;
        margin-bottom: 10px;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    /* Affichage de la date */
    .date-display {
        font-size: 18px;
        color: rgba(255, 255, 255, 0.8);
        text-align: center;
        margin-bottom: 30px;
        font-weight: 300;
    }
    
    /* Cartes de prévision */
    .forecast-card {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
    }
    
    .forecast-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        background: rgba(255, 255, 255, 0.15);
    }
    
    /* Titres */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 300 !important;
    }
    
    /* Selectbox personnalisé */
    .stSelectbox label {
        color: #ffffff !important;
        font-weight: 400;
        font-size: 16px;
    }
    
    .stSelectbox > div > div {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
        backdrop-filter: blur(10px);
    }
    
    .stSelectbox svg {
        fill: white;
    }
    
    /* Header avec dégradé et glassmorphism */
    .header {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        padding: 30px;
        border-radius: 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        margin-bottom: 40px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .header-title {
        font-size: 56px;
        font-weight: 300;
        color: white;
        text-align: center;
        margin: 0;
        text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        letter-spacing: 2px;
    }
    
    .header-subtitle {
        font-size: 16px;
        color: rgba(255, 255, 255, 0.85);
        text-align: center;
        margin-top: 15px;
        font-weight: 300;
    }
    
    /* Footer moderne avec colonnes */
    .footer {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px);
        padding: 40px;
        border-radius: 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        margin-top: 60px;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    
    .footer-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 30px;
        margin-top: 20px;
    }
    
    .footer-section {
        color: rgba(255, 255, 255, 0.9);
    }
    
    .footer-section h3 {
        font-size: 18px;
        font-weight: 500;
        margin-bottom: 15px;
        color: #ffffff !important;
        border-bottom: 2px solid rgba(255, 255, 255, 0.2);
        padding-bottom: 10px;
    }
    
    .footer-section p, .footer-section ul {
        font-size: 14px;
        line-height: 1.8;
        color: rgba(255, 255, 255, 0.75);
        margin: 8px 0;
    }
    
    .footer-section ul {
        list-style: none;
        padding: 0;
    }
    
    .footer-section ul li::before {
        content: "→ ";
        color: rgba(255, 255, 255, 0.5);
        margin-right: 8px;
    }
    
    .footer-bottom {
        text-align: center;
        margin-top: 30px;
        padding-top: 25px;
        border-top: 1px solid rgba(255, 255, 255, 0.15);
        color: rgba(255, 255, 255, 0.7);
        font-size: 13px;
    }
    
    .footer-developers {
        font-size: 20px;
        font-weight: 500;
        color: #ffffff;
        text-align: center;
        margin-bottom: 20px;
    }
    
    /* Spinner personnalisé */
    .stSpinner > div {
        border-top-color: #ffffff !important;
    }
    
    /* Amélioration des graphiques */
    .js-plotly-plot {
        border-radius: 15px;
        overflow: hidden;
    }
            /* Footer centré, élégant et lisible */
.footer-card {
    max-width: 900px;
    margin: 60px auto 30px auto;
    background: rgba(255, 255, 255, 0.10);
    backdrop-filter: blur(18px);
    border-radius: 22px;
    padding: 30px 40px;
    text-align: center;
    box-shadow: 0 10px 35px rgba(0, 0, 0, 0.35);
    border: 1px solid rgba(255, 255, 255, 0.18);
}

.footer-title {
    font-size: 22px;
    font-weight: 400;
    color: #ffffff;
    letter-spacing: 1px;
    margin-bottom: 10px;
}

.footer-text {
    font-size: 15px;
    color: rgba(255, 255, 255, 0.85);
    line-height: 1.8;
    font-weight: 300;
}

.footer-subtext {
    margin-top: 15px;
    font-size: 13px;
    color: rgba(255, 255, 255, 0.65);
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
    <p class="header-subtitle">🌍 Prévisions météorologiques intelligentes • 📊 Analyse de données en temps réel </p>
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
            st.markdown(f'<p style="text-align: center; font-size: 24px; color: rgba(255,255,255,0.8); margin-top: -10px; font-weight: 300;">{current_desc}</p>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Métriques météo
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 40px;">💧</div>
            <div style="font-size: 32px; font-weight: 300; margin: 10px 0;">{current_humidity:.0f}%</div>
            <div style="font-size: 14px; opacity: 0.8; font-weight: 300;">Humidité</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 40px;">🌡️</div>
            <div style="font-size: 32px; font-weight: 300; margin: 10px 0;">{current_pressure:.0f} hPa</div>
            <div style="font-size: 14px; opacity: 0.8; font-weight: 300;">Pression</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 40px;">💨</div>
            <div style="font-size: 32px; font-weight: 300; margin: 10px 0;">{current_wind:.1f} m/s</div>
            <div style="font-size: 14px; opacity: 0.8; font-weight: 300;">Vent</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        feels_like = current_temp - (current_wind * 0.5)
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 40px;">🌡️</div>
            <div style="font-size: 32px; font-weight: 300; margin: 10px 0;">{feels_like:.1f}°C</div>
            <div style="font-size: 14px; opacity: 0.8; font-weight: 300;">Ressenti</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Prévisions 7 jours
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; margin-bottom: 30px; font-weight: 300;">📅 Prévisions sur 7 jours</h2>', unsafe_allow_html=True)
    
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
                        <div style="font-weight: 400; color: #ffffff; margin-bottom: 10px; font-size: 16px;">{day_name}</div>
                        <div style="font-size: 14px; color: rgba(255,255,255,0.7); margin-bottom: 15px;">{day_num}</div>
                        <div style="font-size: 48px; margin: 15px 0;">{emoji}</div>
                        <div style="font-size: 28px; font-weight: 300; color: #ffffff; margin: 10px 0;">{temp:.0f}°</div>
                        <div style="font-size: 12px; color: rgba(255,255,255,0.7);">
                            <span style="color: #ff9800;">↑{temp_max:.0f}°</span> 
                            <span style="color: #64b5f6;">↓{temp_min:.0f}°</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Graphique de tendance
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown('<h2 style="text-align: center; margin-bottom: 30px; font-weight: 300;">📈 Tendance des températures</h2>', unsafe_allow_html=True)
            
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
                line=dict(color='rgba(100, 181, 246, 0.8)', width=3),
                fill=None
            ))
            
            # Prédictions
            fig.add_trace(go.Scatter(
                x=predictions["ds"],
                y=predictions["yhat"],
                mode='lines+markers',
                name='Prévisions',
                line=dict(color='#ff9800', width=4),
                marker=dict(size=10, symbol='circle', color='#ff9800')
            ))
            
            # Intervalle de confiance
            fig.add_trace(go.Scatter(
                x=predictions["ds"].tolist() + predictions["ds"].tolist()[::-1],
                y=predictions["yhat_upper"].tolist() + predictions["yhat_lower"].tolist()[::-1],
                fill='toself',
                fillcolor='rgba(255, 152, 0, 0.2)',
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
                plot_bgcolor='rgba(255,255,255,0.05)',
                font=dict(color='#ffffff', size=12),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    bgcolor='rgba(0,0,0,0.3)',
                    bordercolor='rgba(255,255,255,0.2)',
                    borderwidth=1
                ),
                xaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(255,255,255,0.1)'
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(255,255,255,0.1)'
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
# =========================
# Footer SamYasWeather
# =========================
# =============================
# FOOTER
# =============================
st.markdown(f"""
<div class="footer-container">
    © {datetime.now().year} • Développé par <span>Yasmine & Samia  - SamYasWeather</span> 
</div>
""", unsafe_allow_html=True)
