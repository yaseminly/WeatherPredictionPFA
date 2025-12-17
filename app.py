
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

# CSS personnalisé pour un thème bleu nuit moderne amélioré
st.markdown("""
<style>
    /* Fond principal avec dégradé bleu nuit */
    .main {
        background: linear-gradient(180deg, #0f1729 0%, #1a237e 40%, #283593 70%, #3949ab 100%);
        animation: gradientShift 15s ease infinite;
        background-size: 100% 200%;
    }
    
    @keyframes gradientShift {
        0%, 100% { background-position: 0% 0%; }
        50% { background-position: 0% 100%; }
    }
    
    .stApp {
        background: linear-gradient(180deg, #0f1729 0%, #1a237e 40%, #283593 70%, #3949ab 100%);
    }
    
    /* Styles pour le bloc de contenu */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Carte météo avec effet glassmorphism amélioré */
    .weather-card {
        background: rgba(255, 255, 255, 0.12);
        border-radius: 28px;
        padding: 45px;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4), 
                    inset 0 1px 0 rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(25px);
        border: 1.5px solid rgba(255, 255, 255, 0.25);
        margin: 25px 0;
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .weather-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: shimmer 8s infinite;
        pointer-events: none;
    }
    
    @keyframes shimmer {
        0%, 100% { transform: translate(-25%, -25%); }
        50% { transform: translate(25%, 25%); }
    }
    
    .weather-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 16px 50px rgba(0, 0, 0, 0.5),
                    inset 0 1px 0 rgba(255, 255, 255, 0.3);
    }
    
    /* Cartes métriques avec dégradé subtil et animations */
    .metric-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.18) 0%, rgba(255, 255, 255, 0.08) 100%);
        border-radius: 22px;
        padding: 28px;
        color: white;
        text-align: center;
        box-shadow: 0 6px 25px rgba(0, 0, 0, 0.25),
                    inset 0 1px 0 rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(15px);
        border: 1.5px solid rgba(255, 255, 255, 0.15);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.1);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .metric-card:hover::after {
        width: 300px;
        height: 300px;
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.35),
                    inset 0 1px 0 rgba(255, 255, 255, 0.25);
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.22) 0%, rgba(255, 255, 255, 0.12) 100%);
    }
    
    /* Affichage de la température principale avec animation */
    .temp-display {
        font-size: 102px;
        font-weight: 200;
        color: #ffffff;
        text-align: center;
        margin: 25px 0;
        text-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
        animation: fadeInScale 0.8s ease-out;
        letter-spacing: -2px;
    }
    
    @keyframes fadeInScale {
        0% {
            opacity: 0;
            transform: scale(0.9);
        }
        100% {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    /* Nom de la ville avec animation */
    .city-name {
        font-size: 52px;
        font-weight: 300;
        color: #ffffff;
        text-align: center;
        margin-bottom: 12px;
        text-shadow: 0 3px 6px rgba(0, 0, 0, 0.4);
        animation: slideDown 0.6s ease-out;
        letter-spacing: 1px;
    }
    
    @keyframes slideDown {
        0% {
            opacity: 0;
            transform: translateY(-20px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Affichage de la date */
    .date-display {
        font-size: 17px;
        color: rgba(255, 255, 255, 0.85);
        text-align: center;
        margin-bottom: 35px;
        font-weight: 300;
        letter-spacing: 0.5px;
    }
    
    /* Cartes de prévision améliorées */
    .forecast-card {
        background: rgba(255, 255, 255, 0.12);
        border-radius: 22px;
        padding: 24px 18px;
        text-align: center;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25),
                    inset 0 1px 0 rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(15px);
        border: 1.5px solid rgba(255, 255, 255, 0.15);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .forecast-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #64b5f6, #ff9800, #64b5f6);
        transform: scaleX(0);
        transition: transform 0.4s ease;
    }
    
    .forecast-card:hover::before {
        transform: scaleX(1);
    }
    
    .forecast-card:hover {
        transform: translateY(-10px) scale(1.03);
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.35),
                    inset 0 1px 0 rgba(255, 255, 255, 0.25);
        background: rgba(255, 255, 255, 0.16);
    }
    
    /* Titres avec animations */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 300 !important;
    }
    
    h2 {
        position: relative;
        display: inline-block;
        padding-bottom: 12px;
    }
    
    h2::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 80px;
        height: 3px;
        background: linear-gradient(90deg, transparent, #64b5f6, transparent);
        border-radius: 2px;
    }
    
    /* Selectbox personnalisé amélioré */
    .stSelectbox label {
        color: #ffffff !important;
        font-weight: 400;
        font-size: 17px;
        letter-spacing: 0.3px;
    }
    
    .stSelectbox > div > div {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.15) 0%, rgba(255, 255, 255, 0.08) 100%);
        border-radius: 14px;
        border: 1.5px solid rgba(255, 255, 255, 0.25);
        color: white;
        backdrop-filter: blur(15px);
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    .stSelectbox > div > div:hover {
        border-color: rgba(255, 255, 255, 0.4);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
    }
    
    .stSelectbox svg {
        fill: white;
    }
    
    /* Header avec dégradé et glassmorphism amélioré */
    .header {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.15) 0%, rgba(255, 255, 255, 0.08) 100%);
        backdrop-filter: blur(25px);
        padding: 40px;
        border-radius: 28px;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.35),
                    inset 0 1px 0 rgba(255, 255, 255, 0.2);
        margin-bottom: 45px;
        border: 1.5px solid rgba(255, 255, 255, 0.25);
        position: relative;
        overflow: hidden;
    }
    
    .header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(100, 181, 246, 0.15) 0%, transparent 70%);
        animation: headerGlow 10s infinite alternate;
    }
    
    @keyframes headerGlow {
        0% { opacity: 0.3; transform: translate(0, 0); }
        100% { opacity: 0.6; transform: translate(-10%, -10%); }
    }
    
    .header-title {
        font-size: 60px;
        font-weight: 200;
        color: white;
        text-align: center;
        margin: 0;
        text-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
        letter-spacing: 3px;
        position: relative;
        z-index: 1;
    }
    
    .header-subtitle {
        font-size: 17px;
        color: rgba(255, 255, 255, 0.88);
        text-align: center;
        margin-top: 18px;
        font-weight: 300;
        letter-spacing: 1px;
        position: relative;
        z-index: 1;
    }
    
    /* Footer moderne centré */
    .footer-container {
        max-width: 950px;
        margin: 70px auto 35px auto;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.12) 0%, rgba(255, 255, 255, 0.06) 100%);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 35px 45px;
        text-align: center;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4),
                    inset 0 1px 0 rgba(255, 255, 255, 0.15);
        border: 1.5px solid rgba(255, 255, 255, 0.2);
        font-size: 15px;
        color: rgba(255, 255, 255, 0.88);
        line-height: 1.9;
        font-weight: 300;
        letter-spacing: 0.3px;
    }
    
    .footer-container span {
        font-weight: 500;
        color: #ffffff;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    /* Spinner personnalisé */
    .stSpinner > div {
        border-top-color: #64b5f6 !important;
        border-right-color: rgba(255, 255, 255, 0.3) !important;
    }
    
    /* Amélioration des graphiques */
    .js-plotly-plot {
        border-radius: 18px;
        overflow: hidden;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
    }
    
    /* Animation de pulsation pour les icônes météo */
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    .weather-icon {
        animation: pulse 3s ease-in-out infinite;
        display: inline-block;
    }
    
    /* Effet de lueur sur les valeurs importantes */
    .glow-text {
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.5),
                     0 0 20px rgba(100, 181, 246, 0.3);
    }
    
    /* Styles pour les badges de température */
    .temp-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 13px;
        font-weight: 400;
        margin: 0 4px;
        backdrop-filter: blur(10px);
    }
    
    .temp-high {
        background: rgba(255, 152, 0, 0.2);
        color: #ffb74d;
        border: 1px solid rgba(255, 152, 0, 0.3);
    }
    
    .temp-low {
        background: rgba(100, 181, 246, 0.2);
        color: #90caf9;
        border: 1px solid rgba(100, 181, 246, 0.3);
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
    <p class="header-subtitle">🌍 Prévisions météorologiques intelligentes • 📊 Analyse de données en temps réel</p>
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
    
    # Ajout : Températures min/max (fallback si absentes)
    current_temp_min = latest_data.get("MinTemperature", current_temp - 3)
    current_temp_max = latest_data.get("MaxTemperature", current_temp + 3)
    
    city_info = get_city_info(df, selected_city)
    
    # Date actuelle
    now = datetime.now()
    st.markdown(f'<div class="city-name">{selected_city}</div>', unsafe_allow_html=True)
    
    if city_info:
        st.markdown(f'<div class="date-display">📍 {city_info["country"]} | {now.strftime("%A, %d %B %Y")}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="date-display">{now.strftime("%A, %d %B %Y")}</div>', unsafe_allow_html=True)
    
    # ✅ CARTE MÉTÉO PRINCIPALE ENCADRÉE DANS UN weather-card (comme demandé)
    st.markdown('<div class="weather-card">', unsafe_allow_html=True)
    
    feels_like = current_temp - (current_wind * 0.5)
    weather_icon = get_weather_emoji(current_temp, current_desc)
    
    # Layout horizontal moderne, intégré dans le weather-card
    st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: space-between; gap: 40px;">
        <div style="flex: 1; text-align: left;">
            <div style="font-size: 96px; font-weight: 200; color: white; letter-spacing: -3px; margin-bottom: 15px;">{current_temp:.1f}°C</div>
            <div style="font-size: 22px; color: rgba(255, 255, 255, 0.85); margin-bottom: 15px; font-weight: 300; letter-spacing: 0.5px;">
                {current_desc if current_desc else 'Conditions météo inconnues'}
            </div>
            <div style="font-size: 17px; color: rgba(255, 255, 255, 0.75); font-weight: 300; letter-spacing: 0.5px; margin-bottom: 25px;">
                Max {current_temp_max:.0f}° • Min {current_temp_min:.0f}° • Ressenti {feels_like:.0f}°
            </div>
        </div>
        <div style="flex-shrink: 0; display: flex; align-items: center; justify-content: center;">
            <div style="font-size: 130px;" class="weather-icon">{weather_icon}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Bouton de partage avec JavaScript
    share_text = f"🌤️ Météo à {selected_city}: {current_temp:.1f}°C - {current_desc if current_desc else 'Conditions météo'} | Max {current_temp_max:.0f}° • Min {current_temp_min:.0f}° #SamYasWeather"
    
    st.markdown(f"""
    <div style="display: flex; justify-content: flex-end; margin-top: 15px;">
        <button onclick="shareWeather()" style="
            background: linear-gradient(135deg, rgba(100, 181, 246, 0.3) 0%, rgba(100, 181, 246, 0.15) 100%);
            border: 1.5px solid rgba(100, 181, 246, 0.5);
            color: white;
            padding: 12px 28px;
            border-radius: 16px;
            font-size: 15px;
            font-weight: 400;
            cursor: pointer;
            backdrop-filter: blur(15px);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            letter-spacing: 0.5px;
            display: flex;
            align-items: center;
            gap: 10px;
        " onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 6px 25px rgba(100, 181, 246, 0.4)'; this.style.background='linear-gradient(135deg, rgba(100, 181, 246, 0.4) 0%, rgba(100, 181, 246, 0.2) 100%)';" 
           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px rgba(0, 0, 0, 0.2)'; this.style.background='linear-gradient(135deg, rgba(100, 181, 246, 0.3) 0%, rgba(100, 181, 246, 0.15) 100%)';">
            <span style="font-size: 18px;">📤</span>
            <span>Partager les prévisions</span>
        </button>
    </div>
    
    <script>
    function shareWeather() {{
        const shareData = {{
            title: 'Prévisions SamYasWeather',
            text: `{share_text}`,
            url: window.location.href
        }};
        
        if (navigator.share) {{
            navigator.share(shareData)
                .then(() => console.log('Partage réussi'))
                .catch((err) => {{
                    fallbackShare();
                }});
        }} else {{
            fallbackShare();
        }}
    }}
    
    function fallbackShare() {{
        const text = `{share_text}`;
        if (navigator.clipboard) {{
            navigator.clipboard.writeText(text).then(() => {{
                alert('✅ Prévisions copiées dans le presse-papiers!');
            }}).catch(() => {{
                promptCopy(text);
            }});
        }} else {{
            promptCopy(text);
        }}
    }}
    
    function promptCopy(text) {{
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        try {{
            document.execCommand('copy');
            alert('✅ Prévisions copiées dans le presse-papiers!');
        }} catch (err) {{
            alert('❌ Impossible de copier automatiquement. Voici le texte:\\n\\n' + text);
        }}
        document.body.removeChild(textarea);
    }}
    </script>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Métriques météo
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 44px; margin-bottom: 8px;">💧</div>
            <div style="font-size: 36px; font-weight: 300; margin: 12px 0; letter-spacing: -1px;" class="glow-text">{current_humidity:.0f}%</div>
            <div style="font-size: 14px; opacity: 0.85; font-weight: 300; letter-spacing: 0.5px;">Humidité</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 44px; margin-bottom: 8px;">🌡️</div>
            <div style="font-size: 36px; font-weight: 300; margin: 12px 0; letter-spacing: -1px;" class="glow-text">{current_pressure:.0f} hPa</div>
            <div style="font-size: 14px; opacity: 0.85; font-weight: 300; letter-spacing: 0.5px;">Pression</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 44px; margin-bottom: 8px;">💨</div>
            <div style="font-size: 36px; font-weight: 300; margin: 12px 0; letter-spacing: -1px;" class="glow-text">{current_wind:.1f} m/s</div>
            <div style="font-size: 14px; opacity: 0.85; font-weight: 300; letter-spacing: 0.5px;">Vent</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 44px; margin-bottom: 8px;">🌡️</div>
            <div style="font-size: 36px; font-weight: 300; margin: 12px 0; letter-spacing: -1px;" class="glow-text">{feels_like:.1f}°C</div>
            <div style="font-size: 14px; opacity: 0.85; font-weight: 300; letter-spacing: 0.5px;">Ressenti</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Prévisions 7 jours
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div style="text-align: center;"><h2 style="margin-bottom: 35px; font-weight: 300; display: inline-block;">📅 Prévisions sur 7 jours</h2></div>', unsafe_allow_html=True)
    
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
                        <div style="font-weight: 500; color: #ffffff; margin-bottom: 8px; font-size: 17px; letter-spacing: 0.5px;">{day_name}</div>
                        <div style="font-size: 14px; color: rgba(255,255,255,0.75); margin-bottom: 18px;">{day_num}</div>
                        <div style="font-size: 52px; margin: 18px 0;" class="weather-icon">{emoji}</div>
                        <div style="font-size: 32px; font-weight: 300; color: #ffffff; margin: 12px 0; letter-spacing: -1px;" class="glow-text">{temp:.0f}°</div>
                        <div style="font-size: 13px; margin-top: 12px;">
                            <span class="temp-badge temp-high">↑ {temp_max:.0f}°</span>
                            <span class="temp-badge temp-low">↓ {temp_min:.0f}°</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Graphique de tendance
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown('<div style="text-align: center;"><h2 style="margin-bottom: 35px; font-weight: 300; display: inline-block;">📈 Tendance des températures</h2></div>', unsafe_allow_html=True)
            
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
                line=dict(color='rgba(100, 181, 246, 0.9)', width=3.5, shape='spline'),
                fill=None
            ))
            
            # Prédictions
            fig.add_trace(go.Scatter(
                x=predictions["ds"],
                y=predictions["yhat"],
                mode='lines+markers',
                name='Prévisions',
                line=dict(color='#ff9800', width=4.5, shape='spline'),
                marker=dict(size=12, symbol='circle', color='#ff9800', line=dict(color='white', width=2))
            ))
            
            # Intervalle de confiance
            fig.add_trace(go.Scatter(
                x=predictions["ds"].tolist() + predictions["ds"].tolist()[::-1],
                y=predictions["yhat_upper"].tolist() + predictions["yhat_lower"].tolist()[::-1],
                fill='toself',
                fillcolor='rgba(255, 152, 0, 0.25)',
                line=dict(color='rgba(255,255,255,0)'),
                showlegend=True,
                name='Intervalle de confiance'
            ))
            
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Température (°C)",
                hovermode='x unified',
                height=450,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(255,255,255,0.06)',
                font=dict(color='#ffffff', size=13, family='system-ui'),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    bgcolor='rgba(0,0,0,0.4)',
                    bordercolor='rgba(255,255,255,0.25)',
                    borderwidth=1.5,
                    font=dict(size=12)
                ),
                xaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(255,255,255,0.12)',
                    gridwidth=1
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(255,255,255,0.12)',
                    gridwidth=1
                ),
                margin=dict(t=50, b=50, l=50, r=50)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown(f"""
<div class="footer-container">
    © {datetime.now().year} • Développé par <span>Yasmine & Samia - SamYasWeather</span> 
</div>
""", unsafe_allow_html=True)

