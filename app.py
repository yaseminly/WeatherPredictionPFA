import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.api_client import WeatherAPIClient
from models.weather_model import WeatherPredictor
import os

# Configuration de la page
st.set_page_config(
    page_title="🌤️ Prédiction Météo",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialisation
if 'predictor' not in st.session_state:
    st.session_state.predictor = WeatherPredictor()
    st.session_state.predictor.load_model()

if 'api_client' not in st.session_state:
    st.session_state.api_client = WeatherAPIClient()

# Titre principal
st.title("🌤️ Prédiction Météo - 7 Jours")
st.markdown("---")

# Sidebar pour la sélection de ville (US2)
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Liste de villes prédéfinies
    cities = [
        "Casablanca", "Rabat", "Marrakech", "Fès", "Tanger",
        "Paris", "London", "New York", "Tokyo", "Dubai"
    ]
    
    selected_city = st.selectbox(
        "🏙️ Choisissez une ville",
        cities,
        index=0
    )
    
    # Option pour ville personnalisée
    custom_city = st.text_input("Ou entrez une ville personnalisée")
    
    if custom_city:
        selected_city = custom_city
    
    st.markdown("---")
    st.info("💡 **Astuce**: Les prédictions sont basées sur un modèle ML entraîné sur des données historiques.")

# Bouton de prédiction
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    predict_button = st.button("🔮 Obtenir les Prédictions", use_container_width=True, type="primary")

if predict_button and selected_city:
    with st.spinner(f"📡 Récupération des données pour {selected_city}..."):
        # Récupérer les données météo actuelles
        current_weather = st.session_state.api_client.get_current_weather(selected_city)
        
        if current_weather:
            # Afficher la météo actuelle
            st.success(f"✅ Données récupérées pour {selected_city}")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("🌡️ Température", f"{current_weather['main']['temp']:.1f}°C")
            
            with col2:
                st.metric("💧 Humidité", f"{current_weather['main']['humidity']}%")
            
            with col3:
                st.metric("🌪️ Pression", f"{current_weather['main']['pressure']} hPa")
            
            with col4:
                st.metric("💨 Vent", f"{current_weather['wind']['speed']} m/s")
            
            st.markdown("---")
            
            # Récupérer les données historiques (simulées)
            with st.spinner("🤖 Entraînement du modèle..."):
                historical_data = st.session_state.api_client.get_historical_data(selected_city, days=60)
                
                if historical_data is not None:
                    # Entraîner le modèle
                    results = st.session_state.predictor.train(historical_data)
                    
                    # Faire les prédictions (US1)
                    predictions = st.session_state.predictor.predict_next_days(historical_data, n_days=7)
                    
                    # Afficher les métriques du modèle
                    with st.expander("📊 Performance du Modèle"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Score Entraînement", f"{results['train_score']:.2%}")
                        with col2:
                            st.metric("Score Test", f"{results['test_score']:.2%}")
                        with col3:
                            st.metric("Échantillons", results['n_samples'])
                    
                    # Afficher les prédictions
                    st.subheader("📅 Prédictions pour les 7 prochains jours")
                    
                    # Créer un DataFrame pour les prédictions
                    pred_df = pd.DataFrame(predictions)
                    pred_df['date'] = pd.to_datetime(pred_df['date'])
                    pred_df['day_name'] = pred_df['date'].dt.strftime('%A %d/%m')
                    
                    # Affichage en cartes
                    cols = st.columns(7)
                    for i, (col, row) in enumerate(zip(cols, pred_df.itertuples())):
                        with col:
                            st.markdown(f"""
                            <div style='text-align: center; padding: 10px; background-color: #f0f2f6; border-radius: 10px;'>
                                <h4 style='margin: 0;'>{row.day_name.split()[0][:3]}</h4>
                                <p style='margin: 5px 0; font-size: 0.8em;'>{row.day_name.split()[1]}</p>
                                <h2 style='margin: 10px 0; color: #ff6b6b;'>{row.temperature}°C</h2>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Graphique simple (sera amélioré dans US3)
                    st.subheader("📈 Évolution de la Température")
                    
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=pred_df['date'],
                        y=pred_df['temperature'],
                        mode='lines+markers',
                        name='Température prédite',
                        line=dict(color='#ff6b6b', width=3),
                        marker=dict(size=10)
                    ))
                    
                    fig.update_layout(
                        xaxis_title="Date",
                        yaxis_title="Température (°C)",
                        hovermode='x unified',
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Sauvegarde du modèle
                    st.session_state.predictor.save_model()
                    
                    # Sauvegarde de l'historique (pour US5)
                    os.makedirs('data', exist_ok=True)
                    pred_df['city'] = selected_city
                    pred_df['prediction_date'] = pd.Timestamp.now()
                    
                    history_file = 'data/predictions_history.csv'
                    if os.path.exists(history_file):
                        history = pd.read_csv(history_file)
                        history = pd.concat([history, pred_df], ignore_index=True)
                    else:
                        history = pred_df
                    
                    history.to_csv(history_file, index=False)
                    
                else:
                    st.error("❌ Impossible de récupérer les données historiques")
        else:
            st.error(f"❌ Ville '{selected_city}' non trouvée. Vérifiez l'orthographe.")

elif predict_button:
    st.warning("⚠️ Veuillez sélectionner une ville")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🌍 Prédiction Météo ML | Sprint 1 - US1 & US2 ✅</p>
</div>
""", unsafe_allow_html=True)