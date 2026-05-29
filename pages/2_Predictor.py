import streamlit as st
import pandas as pd
import numpy as np
from models.predictor import MatchPredictor
from data.teams import TEAMS, get_team_stats, simulate_match

st.set_page_config(page_title="Predictor IA - Mundial 2026", page_icon="🤖", layout="wide")

st.markdown("# 🤖 Predictor Inteligente de Partidos")
st.markdown("### Modelo XGBoost entrenado con 5,000 partidos simulados")

if "predictor" not in st.session_state:
    with st.spinner("Entrenando modelo XGBoost..."):
        st.session_state.predictor = MatchPredictor()
predictor = st.session_state.predictor

st.sidebar.markdown("### Ajustes del Modelo")
st.sidebar.metric("Precisión modelo", f"{predictor.test_score:.1%}")

st.sidebar.markdown("### Importancia de Variables")
imp = predictor.feature_importance()
for var, val in imp.items():
    label = var.replace("_", " ").title()
    st.sidebar.progress(float(val), text=f"{label}: {val:.1%}")

st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🇦🇹 Selección Local")
    team_a = st.selectbox("Equipo A", sorted(TEAMS.keys()), index=0, key="team_a")
    form_a = st.slider("Forma reciente (0-1)", 0.0, 1.0, 0.7, 0.05, key="form_a")
    fatigue_a = st.slider("Fatiga (0-1)", 0.0, 1.0, 0.2, 0.05, key="fatigue_a")
    home = st.checkbox("Juega en casa", value=True)

    stats_a = get_team_stats(team_a)
    st.info(f"**{team_a}** — Estilo: {stats_a['style'].title()} | Elo: {stats_a['elo']} | Fuerza: {stats_a['strength']}")

with col2:
    st.markdown("### 🇦🇷 Selección Visitante")
    team_b = st.selectbox("Equipo B", sorted(TEAMS.keys()), index=1, key="team_b")
    form_b = st.slider("Forma reciente (0-1)", 0.0, 1.0, 0.6, 0.05, key="form_b")
    fatigue_b = st.slider("Fatiga (0-1)", 0.0, 1.0, 0.3, 0.05, key="fatigue_b")

    stats_b = get_team_stats(team_b)
    st.info(f"**{team_b}** — Estilo: {stats_b['style'].title()} | Elo: {stats_b['elo']} | Fuerza: {stats_b['strength']}")

st.markdown("---")

if st.button("🔮 Predecir Partido", type="primary", use_container_width=True):
    with st.spinner("Ejecutando modelo predictivo..."):
        prob_a = predictor.predict(
            {**stats_a, "form": form_a, "fatigue": fatigue_a},
            {**stats_b, "form": form_b, "fatigue": fatigue_b},
            home
        )
        prob_b = 1 - prob_a

        match = simulate_match(team_a, team_b)
        match["win_prob_a"] = prob_a
        match["win_prob_b"] = prob_b

    st.markdown("## 📊 Resultados de la Predicción")

    prob_cols = st.columns(3)

    with prob_cols[0]:
        st.markdown(f"### {team_a}")
        st.markdown(f"## {prob_a:.1%}")
        st.markdown(f"Goles: **{match['goals_a']}**")
        st.markdown(f"Posesión: **{match['possession_a']:.0f}%**")
        st.markdown(f"Tiros: **{match['shots_a']}**")
        st.markdown(f"xG: **{match['xg_a']}**")

    with prob_cols[1]:
        st.markdown("### ⚖️")
        st.markdown("## VS")
        st.markdown("### Empate")
        st.markdown(f"{1 - prob_a - prob_b:.1%}" if prob_a + prob_b < 1 else "0.0%")
        st.markdown(f"Marcador: **{match['goals_a']} - {match['goals_b']}**")
        st.markdown(f"Estilo: {match['style_a'].title()} vs {match['style_b'].title()}")

    with prob_cols[2]:
        st.markdown(f"### {team_b}")
        st.markdown(f"## {prob_b:.1%}")
        st.markdown(f"Goles: **{match['goals_b']}**")
        st.markdown(f"Posesión: **{match['possession_b']:.0f}%**")
        st.markdown(f"Tiros: **{match['shots_b']}**")
        st.markdown(f"xG: **{match['xg_b']}**")

    st.markdown("---")
    st.markdown("### 📈 Distribución de Probabilidades")

    probs_df = pd.DataFrame({
        "Equipo": [team_a, "Empate", team_b],
        "Probabilidad": [prob_a, max(0, 1 - prob_a - prob_b), prob_b]
    })

    import plotly.express as px
    fig = px.bar(probs_df, x="Equipo", y="Probabilidad",
                 color="Equipo", text_auto=".0%",
                 color_discrete_sequence=["#00d4ff", "#ffd93d", "#ff6b6b"])
    fig.update_layout(
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font_color="white", height=300,
        showlegend=False,
    )
    fig.update_traces(textfont_size=16, textposition="outside")
    fig.update_yaxes(range=[0, 1], dtick=0.1)
    st.plotly_chart(fig, use_container_width=True, key="prob_chart")

    st.markdown("---")
    st.markdown("### 🧠 Análisis del Modelo")

    col_a, col_b = st.columns(2)
    with col_a:
        if prob_a > 0.6:
            st.success(f"🔮 **{team_a} es el claro favorito** ({prob_a:.0%} probabilidad)")
        elif prob_a > 0.4:
            st.warning(f"⚠️ **{team_a} parte con ligera ventaja** ({prob_a:.0%})")
        else:
            st.error(f"📉 **{team_a} es el underdog** ({prob_a:.0%})")

    with col_b:
        xg_diff = match["xg_a"] - match["xg_b"]
        style_advantage = "posesión" if xg_diff > 0 else "transición"
        st.info(f"💡 **Ventaja táctica:** {team_a if xg_diff > 0 else team_b} "
                f"domina en xG por {abs(xg_diff):.2f}")

    st.markdown("---")
    st.subheader("📤 Compartir predicción")
    if st.session_state.get("telegram_connected") and st.session_state.get("telegram_chat_id"):
        if st.button("📤 Enviar predicción a Telegram", use_container_width=True, type="primary"):
            from utils.telegram_bot import send_message
            emoji_winner = "🏆" if prob_a > 0.5 else "⚔️"
            winner = team_a if prob_a > prob_b else ("Empate" if prob_a < 0.4 and prob_b < 0.4 else team_b)
            msg = (
                f"🤖 <b>PREDICCIÓN IA</b> 🤖\n"
                f"{'━'*30}\n"
                f"⚔️ <b>{team_a} vs {team_b}</b>\n\n"
                f"{emoji_winner} <b>Favorito:</b> {winner} ({max(prob_a, prob_b):.1%})\n"
                f"📊 <b>Probabilidades:</b>\n"
                f"   {team_a}: {prob_a:.1%}\n"
                f"   Empate: {1-prob_a-pro_b:.1%}\n"
                f"   {team_b}: {prob_b:.1%}\n\n"
                f"🥅 <b>Resultado probable:</b> {match['goals_a']}-{match['goals_b']}\n"
                f"⚽ <b>xG:</b> {match['xg_a']} - {match['xg_b']}\n"
                f"🎯 <b>Precisión modelo:</b> {predictor.test_score:.1%}\n"
                f"{'━'*30}\n"
                f"🏆 World Cup 2026 · AI Analytics"
            )
            resp = send_message(st.session_state.telegram_chat_id, msg)
            if resp.get("ok"):
                st.success("✅ Predicción enviada a Telegram!")
            else:
                st.error(f"❌ Error: {resp.get('description', 'desconocido')}")
    else:
        st.info("💡 Conectá Telegram en la barra lateral para compartir predicciones")

else:
    st.info("👆 Selecciona los equipos y ajusta los parámetros, luego presiona 'Predecir Partido'")
