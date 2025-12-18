import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from streamlit.components.v1 import html as components_html
from models.weather_model import load_and_clean_data, get_city_data, train_and_predict, get_city_info
from config import DEFAULT_CITY, FORECAST_DAYS
import base64
# Configuration de la page
st.set_page_config(
    page_title="SYWeather - Prévisions Météo Intelligentes",
     page_icon="assets/syweather.jpeg",   # favicon
    layout="wide",
    initial_sidebar_state="collapsed"
)

def load_logo(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_base64 = load_logo("assets/syweather.jpeg")
# CSS professionnel et moderne
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Fond avec dégradé dynamique et particules */
    .main {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 25%, #2d1b69 50%, #1e3a8a 75%, #1e40af 100%);
        animation: gradientFlow 20s ease infinite;
        background-size: 400% 400%;
        position: relative;
    }
    
    @keyframes gradientFlow {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .stApp {
        background: transparent;
    }
    
    .block-container {
        padding: 3rem 2rem;
        max-width: 1600px;
    }
    
    /* Hero Section - Header Premium avec Meilleure Visibilité */
    .hero-header {
        background: linear-gradient(135deg, rgba(15,23,42,0.95) 0%, rgba(30,58,138,0.9) 100%);
        backdrop-filter: blur(40px) saturate(180%);
        padding: 70px 50px;
        border-radius: 32px;
        box-shadow: 0 25px 70px rgba(0,0,0,0.6),
                    inset 0 2px 0 rgba(255,255,255,0.3),
                    0 0 120px rgba(96,165,250,0.2);
        margin-bottom: 50px;
        border: 2px solid rgba(96,165,250,0.4);
        position: relative;
        overflow: hidden;
    }
    
    .hero-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(circle at 20% 50%, rgba(96,165,250,0.15) 0%, transparent 50%),
            radial-gradient(circle at 80% 50%, rgba(129,140,248,0.15) 0%, transparent 50%);
        animation: heroGlow 12s ease infinite;
        pointer-events: none;
    }
    
    .hero-header::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, 
            transparent 0%, 
            #60a5fa 25%, 
            #818cf8 50%, 
            #a78bfa 75%, 
            transparent 100%);
        animation: borderShine 3s ease-in-out infinite;
    }
    
    @keyframes heroGlow {
        0%, 100% { opacity: 0.5; transform: scale(1); }
        50% { opacity: 1; transform: scale(1.1); }
    }
    
    @keyframes borderShine {
        0%, 100% { opacity: 0.5; }
        50% { opacity: 1; }
    }
    
    .hero-title {
        font-size: 80px;
        font-weight: 800;
        color: #ffffff;
        text-align: center;
        margin: 0;
        letter-spacing: -2px;
        position: relative;
        z-index: 1;
        text-shadow: 
            0 0 40px rgba(96,165,250,0.8),
            0 0 80px rgba(96,165,250,0.4),
            0 4px 20px rgba(0,0,0,0.8),
            0 8px 40px rgba(0,0,0,0.5);
        filter: drop-shadow(0 4px 8px rgba(96,165,250,0.5));
        animation: titlePulse 4s ease-in-out infinite;
    }
    
    @keyframes titlePulse {
        0%, 100% { 
            text-shadow: 
                0 0 40px rgba(96,165,250,0.8),
                0 0 80px rgba(96,165,250,0.4),
                0 4px 20px rgba(0,0,0,0.8);
        }
        50% { 
            text-shadow: 
                0 0 60px rgba(96,165,250,1),
                0 0 120px rgba(96,165,250,0.6),
                0 4px 20px rgba(0,0,0,0.8);
        }
    }
    
    .hero-subtitle {
        font-size: 22px;
        color: rgba(255,255,255,0.95);
        text-align: center;
        margin-top: 25px;
        font-weight: 400;
        letter-spacing: 1px;
        position: relative;
        z-index: 1;
        text-shadow: 0 2px 10px rgba(0,0,0,0.5);
    }
    
    .hero-badges {
        display: flex;
        justify-content: center;
        gap: 15px;
        margin-top: 35px;
        flex-wrap: wrap;
        position: relative;
        z-index: 1;
    }
    
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 12px 24px;
        background: linear-gradient(135deg, rgba(96,165,250,0.25) 0%, rgba(129,140,248,0.2) 100%);
        border: 2px solid rgba(96,165,250,0.4);
        border-radius: 50px;
        backdrop-filter: blur(10px);
        font-size: 14px;
        color: #ffffff;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    .hero-badge:hover {
        background: linear-gradient(135deg, rgba(96,165,250,0.35) 0%, rgba(129,140,248,0.3) 100%);
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(59,130,246,0.5);
        border-color: rgba(96,165,250,0.6);
    }
    
    /* Carte météo principale - Design premium */
    .main-weather-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.12) 0%, rgba(255,255,255,0.06) 100%);
        border-radius: 40px;
        padding: 60px;
        box-shadow: 0 25px 80px rgba(0,0,0,0.6),
                    inset 0 2px 0 rgba(255,255,255,0.2);
        backdrop-filter: blur(40px) saturate(180%);
        border: 2px solid rgba(255,255,255,0.2);
        margin: 40px 0;
        position: relative;
        overflow: hidden;
    }
    
    .main-weather-card::before {
        content: '';
        position: absolute;
        top: -100%;
        right: -100%;
        width: 300%;
        height: 300%;
        background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
        animation: cardShimmer 20s infinite;
        pointer-events: none;
    }
    
    @keyframes cardShimmer {
        0%, 100% { transform: translate(0, 0) scale(1); }
        50% { transform: translate(-30%, -30%) scale(1.1); }
    }
    
    /* Ville et date */
    .city-header {
        text-align: center;
        margin-bottom: 50px;
        position: relative;
        z-index: 1;
    }
    
    .city-name {
        font-size: 64px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 10px;
        letter-spacing: -1px;
        text-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }
    
    .city-meta {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 20px;
        font-size: 18px;
        color: rgba(255,255,255,0.85);
        font-weight: 400;
    }
    
    .city-meta-divider {
        width: 6px;
        height: 6px;
        background: rgba(255,255,255,0.5);
        border-radius: 50%;
    }
    
    /* Section température principale - Améliorée */
    .temp-display {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 60px;
        position: relative;
        z-index: 1;
        padding: 50px 40px;
        background: linear-gradient(135deg, rgba(96,165,250,0.08) 0%, rgba(129,140,248,0.05) 100%);
        border-radius: 30px;
        border: 1px solid rgba(96,165,250,0.2);
    }
    
    .temp-left {
        flex: 1;
    }
    
    .current-temp {
        font-size: 160px;
        font-weight: 800;
        color: #ffffff;
        line-height: 0.9;
        letter-spacing: -8px;
        text-shadow: 
            0 0 60px rgba(96,165,250,0.6),
            0 10px 40px rgba(0,0,0,0.6);
        margin-bottom: 30px;
        display: flex;
        align-items: flex-start;
        gap: 10px;
    }
    
    .temp-unit {
        font-size: 70px;
        font-weight: 600;
        opacity: 0.9;
        margin-top: 20px;
        color: rgba(96,165,250,0.9);
        text-shadow: 0 0 30px rgba(96,165,250,0.5);
    }
    
    .weather-desc {
        font-size: 32px;
        color: rgba(255,255,255,0.95);
        margin-bottom: 30px;
        font-weight: 500;
        letter-spacing: 0.5px;
        text-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    
    .temp-range {
        display: flex;
        gap: 15px;
        font-size: 17px;
        color: rgba(255,255,255,0.9);
        font-weight: 500;
        flex-wrap: wrap;
    }
    
    .temp-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 12px 20px;
        background: linear-gradient(135deg, rgba(255,255,255,0.12) 0%, rgba(255,255,255,0.08) 100%);
        border-radius: 14px;
        backdrop-filter: blur(15px);
        border: 1.5px solid rgba(255,255,255,0.15);
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .temp-item:hover {
        transform: translateY(-3px);
        background: linear-gradient(135deg, rgba(96,165,250,0.2) 0%, rgba(129,140,248,0.15) 100%);
        border-color: rgba(96,165,250,0.4);
        box-shadow: 0 6px 20px rgba(59,130,246,0.3);
    }
    
    .temp-item strong {
        font-weight: 700;
        font-size: 19px;
        color: #ffffff;
    }
    
    .temp-right {
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
    }
    
    .weather-icon-large {
        font-size: 220px;
        animation: floatIcon 6s ease-in-out infinite;
        filter: drop-shadow(0 15px 40px rgba(0,0,0,0.4));
    }
    
    @keyframes floatIcon {
        0%, 100% { transform: translateY(0px) rotate(-2deg); }
        50% { transform: translateY(-25px) rotate(2deg); }
    }
    
    /* Bouton de partage premium */
    .share-section {
        display: flex;
        justify-content: flex-end;
        margin-top: 30px;
        position: relative;
        z-index: 1;
    }
    
    /* Cartes métriques premium */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 25px;
        margin: 50px 0;
    }
    
    .metric-card-pro {
        background: linear-gradient(135deg, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0.08) 100%);
        border-radius: 28px;
        padding: 40px 30px;
        text-align: center;
        box-shadow: 0 15px 40px rgba(0,0,0,0.4),
                    inset 0 1px 0 rgba(255,255,255,0.2);
        backdrop-filter: blur(25px);
        border: 2px solid rgba(255,255,255,0.15);
        transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card-pro::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #60a5fa, #818cf8, #a78bfa);
        transform: scaleX(0);
        transform-origin: left;
        transition: transform 0.6s ease;
    }
    
    .metric-card-pro:hover::before {
        transform: scaleX(1);
    }
    
    .metric-card-pro:hover {
        transform: translateY(-15px) scale(1.03);
        box-shadow: 0 25px 60px rgba(59,130,246,0.4),
                    inset 0 1px 0 rgba(255,255,255,0.3);
        border-color: rgba(96,165,250,0.4);
    }
    
    .metric-icon {
        font-size: 60px;
        margin-bottom: 15px;
        display: inline-block;
        filter: drop-shadow(0 5px 15px rgba(0,0,0,0.3));
    }
    
    .metric-value {
        font-size: 48px;
        font-weight: 700;
        color: #ffffff;
        margin: 15px 0;
        letter-spacing: -2px;
        text-shadow: 0 3px 15px rgba(0,0,0,0.3);
    }
    
    .metric-label {
        font-size: 16px;
        color: rgba(255,255,255,0.85);
        font-weight: 500;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    
    /* Section titre avec séparateur élégant */
    .section-header {
        text-align: center;
        margin: 80px 0 50px 0;
        position: relative;
    }
    
    .section-title {
        font-size: 42px;
        font-weight: 700;
        color: #ffffff;
        display: inline-block;
        position: relative;
        padding: 0 30px;
        letter-spacing: -1px;
    }
    
    .section-title::before,
    .section-title::after {
        content: '';
        position: absolute;
        top: 50%;
        width: 100px;
        height: 2px;
        background: linear-gradient(90deg, transparent, #60a5fa, transparent);
    }
    
    .section-title::before {
        right: 100%;
        margin-right: 30px;
    }
    
    .section-title::after {
        left: 100%;
        margin-left: 30px;
    }
    
    /* Cartes de prévision premium */
    .forecast-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 20px;
        margin: 40px 0;
    }
    
    .forecast-card-pro {
        background: linear-gradient(135deg, rgba(255,255,255,0.12) 0%, rgba(255,255,255,0.06) 100%);
        border-radius: 24px;
        padding: 30px 20px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3),
                    inset 0 1px 0 rgba(255,255,255,0.15);
        backdrop-filter: blur(20px);
        border: 1.5px solid rgba(255,255,255,0.15);
        transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        position: relative;
        overflow: hidden;
    }
    
    .forecast-card-pro::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #60a5fa, #818cf8);
        transform: scaleX(0);
        transition: transform 0.4s ease;
    }
    
    .forecast-card-pro:hover::before {
        transform: scaleX(1);
    }
    
    .forecast-card-pro:hover {
        transform: translateY(-12px) scale(1.05);
        box-shadow: 0 20px 50px rgba(59,130,246,0.4),
                    inset 0 1px 0 rgba(255,255,255,0.25);
        border-color: rgba(96,165,250,0.4);
    }
    
    .forecast-day {
        font-size: 18px;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 5px;
        letter-spacing: 0.5px;
    }
    
    .forecast-date {
        font-size: 14px;
        color: rgba(255,255,255,0.7);
        margin-bottom: 20px;
    }
    
    .forecast-icon {
        font-size: 64px;
        margin: 20px 0;
        display: inline-block;
        animation: pulse 3s ease-in-out infinite;
    }
    
    .forecast-temp {
        font-size: 36px;
        font-weight: 700;
        color: #ffffff;
        margin: 15px 0;
        letter-spacing: -1px;
    }
    
    .forecast-range {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-top: 15px;
    }
    
    .temp-badge-pro {
        padding: 6px 14px;
        border-radius: 12px;
        font-size: 13px;
        font-weight: 600;
        backdrop-filter: blur(10px);
    }
    
    .temp-high {
        background: rgba(251,146,60,0.25);
        color: #fbbf24;
        border: 1px solid rgba(251,146,60,0.4);
    }
    
    .temp-low {
        background: rgba(96,165,250,0.25);
        color: #93c5fd;
        border: 1px solid rgba(96,165,250,0.4);
    }
    
    /* Graphique dans une carte élégante */
    .chart-container {
    background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
    border-radius: 24px;
    padding: 25px 30px;        /* ⬅ padding réduit */
    box-shadow: 0 12px 40px rgba(0,0,0,0.45),
                inset 0 1px 0 rgba(255,255,255,0.12);
    backdrop-filter: blur(25px);
    border: 1.5px solid rgba(255,255,255,0.15);
    margin: 25px 0;            /* ⬅ marge verticale réduite */
}

    
    /* Footer premium */
    .footer-pro {
        max-width: 1200px;
        margin: 100px auto 40px auto;
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        backdrop-filter: blur(30px);
        border-radius: 28px;
        padding: 50px;
        text-align: center;
        box-shadow: 0 15px 50px rgba(0,0,0,0.5),
                    inset 0 1px 0 rgba(255,255,255,0.15);
        border: 2px solid rgba(255,255,255,0.15);
    }
    
    .footer-content {
        font-size: 16px;
        color: rgba(255,255,255,0.85);
        line-height: 1.8;
        font-weight: 400;
    }
    
    .footer-brand {
        font-weight: 700;
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 18px;
    }
    
    /* Sélecteur de ville premium */
    .stSelectbox label, .stMultiSelect label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 18px !important;
        letter-spacing: 0.5px;
    }
    
    .stSelectbox > div > div, .stMultiSelect > div > div {
        background: linear-gradient(135deg, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0.08) 100%);
        border-radius: 16px;
        border: 2px solid rgba(255,255,255,0.2);
        color: white;
        backdrop-filter: blur(20px);
        transition: all 0.3s ease;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        font-weight: 500;
    }
    
    .stSelectbox > div > div:hover, .stMultiSelect > div > div:hover {
        border-color: rgba(96,165,250,0.5);
        box-shadow: 0 12px 35px rgba(59,130,246,0.4);
        transform: translateY(-2px);
    }
    
    /* Style pour les tags du multiselect */
    .stMultiSelect [data-baseweb="tag"] {
        background: linear-gradient(135deg, rgba(96,165,250,0.3) 0%, rgba(129,140,248,0.2) 100%);
        border: 1px solid rgba(96,165,250,0.5);
        border-radius: 8px;
        color: #ffffff;
        font-weight: 500;
    }
    
    /* Info box style */
    .stAlert {
        background: linear-gradient(135deg, rgba(96,165,250,0.15) 0%, rgba(129,140,248,0.1) 100%);
        border: 2px solid rgba(96,165,250,0.3);
        border-radius: 16px;
        backdrop-filter: blur(15px);
        color: rgba(255,255,255,0.95) !important;
    }
    
    /* Spinner premium */
    .stSpinner > div {
        border-top-color: #60a5fa !important;
    }
    
    /* Animations globales */
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.05); opacity: 0.9; }
    }
    
    /* Responsive - Amélioré */
    @media (max-width: 768px) {
        .hero-title { font-size: 48px; }
        .current-temp { 
            font-size: 100px !important; 
            letter-spacing: -4px;
            flex-direction: column;
            align-items: flex-start;
            gap: 0;
        }
        .temp-unit { 
            font-size: 50px !important;
            margin-top: 5px;
        }
        .weather-icon-large { font-size: 140px; }
        .temp-display { 
            flex-direction: column; 
            gap: 30px; 
            padding: 30px 20px;
        }
        .temp-range {
            flex-direction: column;
            gap: 10px;
        }
        .temp-item {
            width: 100%;
            justify-content: space-between;
        }
        .section-title { font-size: 32px; }
        .weather-desc { font-size: 24px; }
    }
            /* ==================== AMÉLIORATION VISIBILITÉ (SANS CHANGER LE DESIGN) ==================== */

/* Meilleure lisibilité globale du texte */
body {
    line-height: 1.65;
}

/* Réduction très légère des halos trop agressifs */
.hero-title,
.current-temp {
    filter: drop-shadow(0 3px 6px rgba(0,0,0,0.6));
}

/* Texte secondaire plus doux et lisible */
.hero-subtitle,
.weather-desc,
.city-meta,
.metric-label,
.forecast-date {
    color: rgba(255,255,255,0.88);
}

/* Amélioration contraste des cartes sans changer couleurs */
.metric-card-pro,
.forecast-card-pro,
.chart-container,
.main-weather-card {
    backdrop-filter: blur(28px);
}

/* Texte des graphiques plus net */
.plotly text,
.plotly .xtick text,
.plotly .ytick text {
    fill: rgba(255,255,255,0.9) !important;
}

/* Légère amélioration des paragraphes */
p {
    letter-spacing: 0.3px;
}

/* Éviter l'effet "éblouissant" sur mobile */
@media (max-width: 768px) {
    .hero-title,
    .current-temp {
        text-shadow:
            0 0 20px rgba(96,165,250,0.6),
            0 4px 15px rgba(0,0,0,0.7);
    }
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

# Hero Header Premium
st.markdown("""
<div class="hero-header">
    <h1 class="hero-title">⛅ SYWeather</h1>
    <p class="hero-subtitle">Intelligence artificielle au service de prévisions météorologiques ultra-précises</p>
    <div class="hero-badges">
        <span class="hero-badge"> IA & Machine Learning</span>
        <span class="hero-badge"> Données en temps réel</span>
        <span class="hero-badge"> Couverture mondiale</span>
        <span class="hero-badge"> Prévisions 7 jours</span>
    </div>
</div>
        
""", unsafe_allow_html=True)


# Fonction pour charger le logo
def load_logo(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Sélection de ville
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    selected_city = st.selectbox(
        " Sélectionnez votre ville",
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
    current_desc = latest_data.get("WeatherDesc", "Conditions météo")
    current_temp_min = latest_data.get("MinTemperature", current_temp - 3)
    current_temp_max = latest_data.get("MaxTemperature", current_temp + 3)
    
    city_info = get_city_info(df, selected_city)
    now = datetime.now()
    
    # Carte météo principale
    st.markdown('<div class="main-weather-card">', unsafe_allow_html=True)
    
    # En-tête ville et date
    country_text = f' {city_info["country"]}' if city_info else ''
    date_text = now.strftime("%A, %d %B %Y")
    
    st.markdown(f"""
    <div class="city-header">
        <div class="city-name">{selected_city}</div>
        <div class="city-meta">
            <span>{country_text}</span>
            <div class="city-meta-divider"></div>
            <span> {date_text}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Affichage température
    feels_like = current_temp - (current_wind * 0.5)
    weather_icon = get_weather_emoji(current_temp, current_desc)
    
    st.markdown(f"""
    <div class="temp-display">
        <div class="temp-left">
            <div class="current-temp">
                <span>{current_temp:.1f}</span>
                <span class="temp-unit">°C</span>
            </div>
            <div class="weather-desc">{current_desc}</div>
            <div class="temp-range">
                <div class="temp-item">
                    <span>↑ Maximum:</span>
                    <strong>{current_temp_max:.0f}°C</strong>
                </div>
                <div class="temp-item">
                    <span>↓ Minimum:</span>
                    <strong>{current_temp_min:.0f}°C</strong>
                </div>
                <div class="temp-item">
                    <span>🌡️ Ressenti:</span>
                    <strong>{feels_like:.0f}°C</strong>
                </div>
            </div>
        </div>
        <div class="temp-right">
            <div class="weather-icon-large">{weather_icon}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Bouton de partage
    share_text = f"🌤️ Météo à {selected_city}: {current_temp:.1f}°C - {current_desc} | Max {current_temp_max:.0f}° • Min {current_temp_min:.0f}° #SamYasWeather"
    
    share_html = f"""
    <div class="share-section">
        <button id="shareBtn" style="
            background: linear-gradient(135deg, rgba(96,165,250,0.3) 0%, rgba(129,140,248,0.2) 100%);
            border: 2px solid rgba(96,165,250,0.5);
            color: white;
            padding: 14px 32px;
            border-radius: 16px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            backdrop-filter: blur(15px);
            transition: all 0.3s ease;
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            gap: 10px;
        " onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 12px 35px rgba(59,130,246,0.5)';" 
           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 8px 25px rgba(0,0,0,0.3)';">
            <span style="font-size: 18px;">📤</span>
            <span>Partager les prévisions</span>
        </button>
    </div>

    <script>
    function copyToClipboard(text) {{
        if (navigator.clipboard && window.isSecureContext) {{
            navigator.clipboard.writeText(text).then(() => {{
                alert('✅ Prévisions copiées dans le presse-papiers !');
            }}).catch(() => fallbackCopy(text));
        }} else {{
            fallbackCopy(text);
        }}
    }}

    function fallbackCopy(text) {{
        const textArea = document.createElement("textarea");
        textArea.value = text;
        textArea.style.position = "fixed";
        textArea.style.opacity = "0";
        document.body.appendChild(textArea);
        textArea.select();
        try {{
            const success = document.execCommand('copy');
            if (success) {{
                alert('✅ Prévisions copiées !');
            }} else {{
                alert('❌ Copie manuelle requise.');
            }}
        }} catch (err) {{
            alert('❌ Échec. Copiez :\\n' + text);
        }}
        document.body.removeChild(textArea);
    }}

    setTimeout(() => {{
        const btn = document.getElementById('shareBtn');
        if (btn) {{
            btn.onclick = () => copyToClipboard({share_text!r});
        }}
    }}, 500);
    </script>
    """
    
    components_html(share_html, height=60)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Métriques météo dans une grille
    st.markdown('<div class="metrics-grid">', unsafe_allow_html=True)
    
    metrics = [
        ("💧", f"{current_humidity:.0f}%", "Humidité"),
        ("🌡️", f"{current_pressure:.0f} hPa", "Pression"),
        ("💨", f"{current_wind:.1f} m/s", "Vent"),
        ("🌡️", f"{feels_like:.1f}°C", "Ressenti")
    ]
    
    cols = st.columns(4)
    for idx, (icon, value, label) in enumerate(metrics):
        with cols[idx]:
            st.markdown(f"""
            <div class="metric-card-pro">
                <div class="metric-icon">{icon}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Analyse comparative multi-villes
    
    
    # Section prévisions 7 jours
    st.markdown("""
    <div class="section-header">
        <h2 class="section-title"> Prévisions sur 7 jours</h2>
    </div>
    """, unsafe_allow_html=True)
    
    with st.spinner(" Analyse des données et calcul des prévisions..."):
        city_data = get_city_data(df, selected_city)
        
        if city_data is not None and not city_data.empty:
            forecast = train_and_predict(city_data, periods=FORECAST_DAYS)
            next_7_days = forecast.tail(FORECAST_DAYS).copy()
            
            # Grille de prévisions
            st.markdown('<div class="forecast-grid">', unsafe_allow_html=True)
            
            cols = st.columns(7)
            for idx, (i, row) in enumerate(next_7_days.iterrows()):
                date = pd.to_datetime(row["ds"])
                temp = row["yhat"]
                temp_min = row["yhat_lower"]
                temp_max = row["yhat_upper"]
                
                day_name = date.strftime("%a")
                day_num = date.strftime("%d")
                month = date.strftime("%b")
                
                with cols[idx]:
                    emoji = get_weather_emoji(temp)
                    st.markdown(f"""
                    <div class="forecast-card-pro">
                        <div class="forecast-day">{day_name}</div>
                        <div class="forecast-date">{day_num} {month}</div>
                        <div class="forecast-icon">{emoji}</div>
                        <div class="forecast-temp">{temp:.0f}°</div>
                        <div class="forecast-range">
                            <span class="temp-badge-pro temp-high">↑{temp_max:.0f}°</span>
                            <span class="temp-badge-pro temp-low">↓{temp_min:.0f}°</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Section graphique
            st.markdown("""
            <div class="section-header">
                <h2 class="section-title"> Tendance des températures</h2>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            
            # Préparer les données pour le graphique
            historical = forecast.head(len(forecast) - FORECAST_DAYS).tail(30)
            predictions = forecast.tail(FORECAST_DAYS)
            
            fig = go.Figure()
            
            # Historique avec style premium
            fig.add_trace(go.Scatter(
                x=historical["ds"],
                y=historical["yhat"],
                mode='lines',
                name='Historique (30 derniers jours)',
                line=dict(color='rgba(96,165,250,0.9)', width=4, shape='spline'),
                fill=None,
                hovertemplate='<b>%{x|%d %b}</b><br>Température: %{y:.1f}°C<extra></extra>'
            ))
            
            # Prédictions avec marqueurs élégants
            fig.add_trace(go.Scatter(
                x=predictions["ds"],
                y=predictions["yhat"],
                mode='lines+markers',
                name='Prévisions IA',
                line=dict(color='#fb923c', width=5, shape='spline'),
                marker=dict(
                    size=14, 
                    symbol='circle', 
                    color='#fb923c',
                    line=dict(color='white', width=3),
                    opacity=1
                ),
                hovertemplate='<b>%{x|%d %b}</b><br>Prévision: %{y:.1f}°C<extra></extra>'
            ))
            
            # Intervalle de confiance avec gradient
            fig.add_trace(go.Scatter(
                x=predictions["ds"].tolist() + predictions["ds"].tolist()[::-1],
                y=predictions["yhat_upper"].tolist() + predictions["yhat_lower"].tolist()[::-1],
                fill='toself',
                fillcolor='rgba(251,146,60,0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                showlegend=True,
                name='Intervalle de confiance (±)',
                hoverinfo='skip'
            ))
            
            # Style premium du graphique
            fig.update_layout(
                xaxis_title="<b>Date</b>",
                yaxis_title="<b>Température (°C)</b>",
                hovermode='x unified',
                height=500,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(255,255,255,0.04)',
                font=dict(color='#ffffff', size=14, family='Inter, sans-serif'),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5,
                    bgcolor='rgba(15,23,42,0.8)',
                    bordercolor='rgba(96,165,250,0.3)',
                    borderwidth=2,
                    font=dict(size=13, family='Inter, sans-serif')
                ),
                xaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(255,255,255,0.08)',
                    gridwidth=1.5,
                    zeroline=False,
                    tickfont=dict(size=12)
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(255,255,255,0.08)',
                    gridwidth=1.5,
                    zeroline=False,
                    tickfont=dict(size=12)
                ),
                margin=dict(t=60, b=60, l=60, r=60),
                hoverlabel=dict(
                    bgcolor="rgba(15,23,42,0.95)",
                    font_size=13,
                    font_family="Inter, sans-serif",
                    bordercolor="rgba(96,165,250,0.5)"
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Analyse statistique de la ville
            st.markdown("""
            <div class="section-header">
                <h2 class="section-title"> Analyse statistique</h2>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            
            # Calculer les statistiques
            temps_historical = city_data_full.tail(90)["AvgTemperature"]
            humidity_historical = city_data_full.tail(90)["Humidity"]
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Graphique de distribution des températures
                fig_dist = go.Figure()
                
                fig_dist.add_trace(go.Histogram(
                    x=temps_historical,
                    nbinsx=20,
                    name='Distribution',
                    marker=dict(
                        color='rgba(96,165,250,0.7)',
                        line=dict(color='rgba(255,255,255,0.8)', width=1.5)
                    ),
                    hovertemplate='Température: %{x:.1f}°C<br>Fréquence: %{y}<extra></extra>'
                ))
                
                fig_dist.update_layout(
                    
                    xaxis_title="<b>Température (°C)</b>",
                    yaxis_title="<b>Nombre de jours</b>",
                    height=350,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(255,255,255,0.04)',
                    font=dict(color='#ffffff', size=12, family='Inter, sans-serif'),
                    showlegend=False,
                    xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.08)'),
                    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.08)'),
                    margin=dict(t=50, b=50, l=50, r=50)
                )
                
                st.plotly_chart(fig_dist, use_container_width=True)
            
            with col2:
                # Statistiques clés
                temp_mean = temps_historical.mean()
                temp_std = temps_historical.std()
                temp_min_stat = temps_historical.min()
                temp_max_stat = temps_historical.max()
                humidity_mean = humidity_historical.mean()
                
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.05); border-radius: 20px; padding: 30px; height: 350px; display: flex; flex-direction: column; justify-content: center;">
                    <h3 style="color: #60a5fa; margin-bottom: 25px; font-size: 20px;"></h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                        <div style="text-align: center; padding: 15px; background: rgba(96,165,250,0.1); border-radius: 12px; border: 1px solid rgba(96,165,250,0.3);">
                            <div style="font-size: 28px; font-weight: 700; color: #60a5fa;">{temp_mean:.1f}°C</div>
                            <div style="font-size: 13px; color: rgba(255,255,255,0.7); margin-top: 5px;">Moyenne</div>
                        </div>
                        <div style="text-align: center; padding: 15px; background: rgba(129,140,248,0.1); border-radius: 12px; border: 1px solid rgba(129,140,248,0.3);">
                            <div style="font-size: 28px; font-weight: 700; color: #818cf8;">{temp_std:.1f}°C</div>
                            <div style="font-size: 13px; color: rgba(255,255,255,0.7); margin-top: 5px;">Écart-type</div>
                        </div>
                        <div style="text-align: center; padding: 15px; background: rgba(251,146,60,0.1); border-radius: 12px; border: 1px solid rgba(251,146,60,0.3);">
                            <div style="font-size: 28px; font-weight: 700; color: #fb923c;">{temp_max_stat:.1f}°C</div>
                            <div style="font-size: 13px; color: rgba(255,255,255,0.7); margin-top: 5px;">Maximum</div>
                        </div>
                        <div style="text-align: center; padding: 15px; background: rgba(52,211,153,0.1); border-radius: 12px; border: 1px solid rgba(52,211,153,0.3);">
                            <div style="font-size: 28px; font-weight: 700; color: #34d399;">{temp_min_stat:.1f}°C</div>
                            <div style="font-size: 13px; color: rgba(255,255,255,0.7); margin-top: 5px;">Minimum</div>
                        </div>
                    </div>
                    <div style="text-align: center; margin-top: 20px; padding: 15px; background: rgba(167,139,250,0.1); border-radius: 12px; border: 1px solid rgba(167,139,250,0.3);">
                        <div style="font-size: 28px; font-weight: 700; color: #a78bfa;">{humidity_mean:.1f}%</div>
                        <div style="font-size: 13px; color: rgba(255,255,255,0.7); margin-top: 5px;">Humidité moyenne</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Graphique température vs humidité
            st.markdown("""
            <div class="section-header">
                <h2 class="section-title"> Corrélation Température & Humidité</h2>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            
            fig_corr = go.Figure()
            
            fig_corr.add_trace(go.Scatter(
                x=temps_historical,
                y=humidity_historical,
                mode='markers',
                marker=dict(
                    size=10,
                    color=temps_historical,
                    colorscale='Bluered',
                    showscale=True,
                    colorbar=dict(
                        title="Temp (°C)",
                        titlefont=dict(color='#ffffff'),
                        tickfont=dict(color='#ffffff')
                    ),
                    line=dict(color='rgba(255,255,255,0.3)', width=1)
                ),
                hovertemplate='Température: %{x:.1f}°C<br>Humidité: %{y:.1f}%<extra></extra>'
            ))
            
            fig_corr.update_layout(
                xaxis_title="<b>Température (°C)</b>",
                yaxis_title="<b>Humidité (%)</b>",
                height=450,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(255,255,255,0.04)',
                font=dict(color='#ffffff', size=14, family='Inter, sans-serif'),
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.08)', gridwidth=1.5),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.08)', gridwidth=1.5),
                margin=dict(t=50, b=60, l=60, r=60)
            )
            
            st.plotly_chart(fig_corr, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

# Footer premium
st.markdown(f"""
<div class="footer-pro">
    <div class="footer-content">
        <p style="margin-bottom: 15px; font-size: 18px;">
            Système de prévision basé sur l’intelligence artificielle et l’apprentissage automatique
        </p>
        <p style="margin-bottom: 10px;">
            © {datetime.now().year} • Créé par 
            <span class="footer-brand">Yasmine & Samia</span>
        </p>
        <p style="font-size: 14px; color: rgba(255,255,255,0.7);">
             Données météorologiques mondiales •  Algorithmes prédictifs avancés •  Visualisations interactives
        </p>
    </div>
</div>
""", unsafe_allow_html=True)