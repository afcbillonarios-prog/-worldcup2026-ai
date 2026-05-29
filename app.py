import streamlit as st

st.set_page_config(
    page_title="World Cup 2026 - AI Analytics",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "telegram_chat_id" not in st.session_state:
    st.session_state.telegram_chat_id = None
if "telegram_connected" not in st.session_state:
    st.session_state.telegram_connected = False
if "telegram_auto_send" not in st.session_state:
    st.session_state.telegram_auto_send = False
if "telegram_signal_log" not in st.session_state:
    st.session_state.telegram_signal_log = []
if "team_a" not in st.session_state:
    st.session_state.team_a = "Argentina"
if "team_b" not in st.session_state:
    st.session_state.team_b = "Francia"

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0a1628 0%, #1a1a2e 50%, #16213e 100%);
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00d4ff, #7b2ff7, #ff6b6b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        color: #8892b0;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .module-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    .module-card:hover {
        border-color: #00d4ff;
        box-shadow: 0 0 20px rgba(0,212,255,0.1);
        transform: translateY(-2px);
    }
    .stSidebar {
        background: rgba(10,14,23,0.95);
    }
    .css-1d391kg {
        background: rgba(10,14,23,0.95);
    }
    .st-emotion-cache-1v7f65g {
        background: rgba(10,14,23,0.95);
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🏆 World Cup 2026 — AI Analytics Platform</div>',
            unsafe_allow_html=True)
st.markdown('<div class="sub-header">Sistema profesional de análisis deportivo con Big Data, ML e IA</div>',
            unsafe_allow_html=True)

st.sidebar.image("https://img.icons8.com/fluency/96/000000/world-cup.png", width=80)
st.sidebar.title("🏆 Mundial 2026")
st.sidebar.markdown("---")
st.sidebar.markdown("### 📡 Señales en vivo")
st.sidebar.markdown("Sistema de analítica avanzada con:")
st.sidebar.markdown("- 🤖 Machine Learning")
st.sidebar.markdown("- 📊 Big Data")
st.sidebar.markdown("- 🎯 Modelos Predictivos")
st.sidebar.markdown("- 👁️ Visión Computacional")
st.sidebar.markdown("- 📡 Tracking Tiempo Real")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🤖 Telegram Bot")
st.sidebar.markdown(f"**Bot:** @BotArTrading2026_bot")

if st.session_state.telegram_connected:
    st.sidebar.success(f"✅ Conectado (ID: {st.session_state.telegram_chat_id})")
    st.sidebar.checkbox("Auto-enviar señales", key="telegram_auto_send",
                        value=st.session_state.telegram_auto_send)
    if st.sidebar.button("📤 Probar señal", key="test_telegram_btn"):
        from utils.telegram_bot import send_signal_alert
        test_signals = {
            "xG_dynamics": 0.35, "possession": 58, "pressing_intensity": 72,
            "momentum": 65, "defensive_line": 32, "fatigue": 28,
            "attack_danger": 55, "control_index": 62, "expected_goals": 1.8,
            "shot_accuracy": 48,
        }
        resp = send_signal_alert(
            st.session_state.telegram_chat_id, test_signals,
            match_time=35, team_a=st.session_state.team_a,
            team_b=st.session_state.team_b
        )
        if resp.get("ok"):
            st.sidebar.success("✅ Señal de prueba enviada!")
        else:
            st.sidebar.error(f"❌ Error: {resp.get('description', 'desconocido')}")
else:
    st.sidebar.warning("⚠️ No conectado")
    st.sidebar.caption("1. Abrí Telegram y buscá @BotArTrading2026_bot")
    st.sidebar.caption("2. Enviá /start al bot")
    if st.sidebar.button("🔌 Detectar chat", key="detect_chat"):
        from utils.telegram_bot import get_updates
        updates = get_updates(5)
        if updates:
            chat = updates[0]
            st.session_state.telegram_chat_id = chat["chat_id"]
            st.session_state.telegram_connected = True
            st.sidebar.success(f"✅ Conectado: {chat['title']} (ID: {chat['chat_id']})")
        else:
            st.sidebar.error("❌ No se encontraron chats. Envía /start al bot primero")
    manual_id = st.sidebar.text_input("O ingresa Chat ID manual:", key="manual_chat_id", placeholder="-1001234567890")
    if manual_id and st.sidebar.button("Conectar", key="connect_telegram"):
        from utils.telegram_bot import send_message
        resp = send_message(manual_id, "🤖 <b>World Cup 2026</b>\n✅ Conexión establecida")
        if resp.get("ok"):
            st.session_state.telegram_chat_id = int(manual_id)
            st.session_state.telegram_connected = True
            st.sidebar.success("✅ Conectado!")
        else:
            st.sidebar.error(f"❌ Error: {resp.get('description', 'desconocido')}")

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Partido actual")
st.session_state.team_a = st.sidebar.selectbox(
    "Equipo A", ["Argentina", "Francia", "Brasil", "Inglaterra", "España",
                 "Alemania", "Portugal", "Países Bajos", "Uruguay", "Croacia"],
    index=["Argentina", "Francia", "Brasil", "Inglaterra", "España",
           "Alemania", "Portugal", "Países Bajos", "Uruguay", "Croacia"].index(
        st.session_state.team_a) if st.session_state.team_a in [
        "Argentina", "Francia", "Brasil", "Inglaterra", "España",
        "Alemania", "Portugal", "Países Bajos", "Uruguay", "Croacia"] else 0,
    key="sidebar_team_a"
)
st.session_state.team_b = st.sidebar.selectbox(
    "Equipo B", ["Argentina", "Francia", "Brasil", "Inglaterra", "España",
                 "Alemania", "Portugal", "Países Bajos", "Uruguay", "Croacia"],
    index=["Argentina", "Francia", "Brasil", "Inglaterra", "España",
           "Alemania", "Portugal", "Países Bajos", "Uruguay", "Croacia"].index(
        st.session_state.team_b) if st.session_state.team_b in [
        "Argentina", "Francia", "Brasil", "Inglaterra", "España",
        "Alemania", "Portugal", "Países Bajos", "Uruguay", "Croacia"] else 1,
    key="sidebar_team_b"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Stack Tecnológico")
st.sidebar.markdown("`Python · XGBoost · Streamlit · Plotly · OpenCV · Scikit-learn`")
st.sidebar.markdown("---")
st.sidebar.markdown("### 🇺🇸🇲🇽🇨🇦")
st.sidebar.markdown("*USA · México · Canadá 2026*")
st.sidebar.markdown("---")
if st.session_state.telegram_signal_log:
    with st.sidebar.expander("📋 Últimas señales enviadas", expanded=False):
        for entry in st.session_state.telegram_signal_log[-5:]:
            st.caption(entry)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div class="module-card">
        <h3>📊 Dashboard Live</h3>
        <p style="color:#8892b0;">Señales en tiempo real: xG, posesión, presión, fatiga, momentum, peligro ofensivo</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="module-card">
        <h3>🤖 Predictor IA</h3>
        <p style="color:#8892b0;">XGBoost predictivo: ganador, probabilidad, goles esperados y análisis táctico</p>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div class="module-card">
        <h3>🎯 Sistema xG</h3>
        <p style="color:#8892b0;">Expected Goals con regresión logística: distancia, ángulo, presión, velocidad</p>
    </div>
    """, unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div class="module-card">
        <h3>🔍 Scouting IA</h3>
        <p style="color:#8892b0;">Clustering K-Means, detección de talentos, jugadores similares, infravalorados</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="module-card">
        <h3>🗺️ Heatmaps Tácticos</h3>
        <p style="color:#8892b0;">Mapas de calor, presión, ocupación espacial, movimientos tácticos</p>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div class="module-card">
        <h3>🏆 Simulación Monte Carlo</h3>
        <p style="color:#8892b0;">10,000 simulaciones del torneo: probabilidades, fases finales, campeón</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #8892b0; padding: 1rem;">
    <p style="font-size: 0.9rem;">
    ⚡ <strong>Señales disponibles:</strong> xG Tiempo Real · Posesión Dinámica · Presión Alta · Momentum · 
    Línea Defensiva · Fatiga · Peligro Ofensivo · Control de Juego · Precisión de Tiro
    </p>
    <p style="font-size: 0.8rem; color: #555;">
    World Cup 2026 AI Analytics · Construido con Python + Machine Learning + Streamlit
    </p>
</div>
""", unsafe_allow_html=True)
