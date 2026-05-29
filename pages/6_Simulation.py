import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from models.simulation import TournamentSimulator
from data.teams import simulate_match

st.set_page_config(page_title="Simulación - Mundial 2026", page_icon="🏆", layout="wide")

st.markdown("# 🏆 Simulación del Mundial 2026")
st.markdown("### Monte Carlo con 10,000 simulaciones del torneo completo")

if "simulator" not in st.session_state:
    st.session_state.simulator = TournamentSimulator()

simulator = st.session_state.simulator

st.markdown("---")
tab1, tab2, tab3 = st.tabs(["📊 Fase de Grupos", "🔄 Monte Carlo", "⚔️ Partido Rápido"])

with tab1:
    st.markdown("### Resultados de fase de grupos")

    seed = st.number_input("Semilla aleatoria", 0, 9999, 42, key="group_seed")

    if st.button("🔄 Simular Fase de Grupos", type="primary", use_container_width=True):
        with st.spinner("Simulando fase de grupos..."):
            results = simulator.simulate_group_stage(seed=int(seed))

        for grp, teams in results.items():
            st.markdown(f"#### Grupo {grp}")

            df = pd.DataFrame(teams)
            df = df.rename(columns={"team": "Equipo", "pts": "Pts", "gf": "GF",
                                     "ga": "GA", "gd": "GD", "w": "G", "d": "E", "l": "P"})

            def highlight_top(s):
                is_top = s.index.isin(df.index[:2])
                return ["background-color: rgba(0,212,255,0.1)" if i else ""
                        for i in is_top]

            st.dataframe(
                df[["Equipo", "Pts", "G", "E", "P", "GF", "GA", "GD"]],
                use_container_width=True,
                column_config={
                    "GD": st.column_config.NumberColumn("GD"),
                },
            )

            fig = px.bar(df, x="Equipo", y="Pts",
                         color="Equipo",
                         text_auto=True,
                         color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_layout(
                height=250, margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
                font_color="white", showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True, key=f"group_{grp}")

with tab2:
    st.markdown("### Simulación Monte Carlo del Torneo")

    col1, col2 = st.columns([1, 2])

    with col1:
        n_sims = st.slider("Número de simulaciones", 100, 5000, 1000, 100, key="n_sims")
        st.caption("A mayor número, más precisa la probabilidad")

        if st.button("🚀 Ejecutar Monte Carlo", type="primary", use_container_width=True):
            with st.spinner(f"Ejecutando {n_sims:,} simulaciones..."):
                mc_results = simulator.monte_carlo(n_simulations=n_sims)
                st.session_state.mc_results = mc_results

    if "mc_results" in st.session_state:
        mc = st.session_state.mc_results

        st.markdown("### 🏆 Probabilidades del Torneo")

        top_n = st.slider("Mostrar top N", 5, 20, 10, key="top_n_mc")
        top_teams = mc.head(top_n)

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Probabilidad de ser Campeón", "Probabilidad de Llegar a Final",
                           "Probabilidad de Semifinales", "Probabilidad de Cuartos"),
            vertical_spacing=0.12, horizontal_spacing=0.08,
        )

        fig.add_trace(
            go.Bar(x=top_teams["team"], y=top_teams["wins_pct"],
                   marker_color="#ffd700",
                   text=[f"{v:.1f}%" for v in top_teams["wins_pct"]],
                   textposition="outside", name="Campeón"),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(x=top_teams["team"], y=top_teams["finals_pct"],
                   marker_color="#c0c0c0",
                   text=[f"{v:.1f}%" for v in top_teams["finals_pct"]],
                   textposition="outside", name="Final"),
            row=1, col=2
        )
        fig.add_trace(
            go.Bar(x=top_teams["team"], y=top_teams["semis_pct"],
                   marker_color="#cd7f32",
                   text=[f"{v:.1f}%" for v in top_teams["semis_pct"]],
                   textposition="outside", name="Semis"),
            row=2, col=1
        )
        fig.add_trace(
            go.Bar(x=top_teams["team"], y=top_teams["quarters_pct"],
                   marker_color="#00d4ff",
                   text=[f"{v:.1f}%" for v in top_teams["quarters_pct"]],
                   textposition="outside", name="Cuartos"),
            row=2, col=2
        )

        fig.update_layout(
            height=500, margin=dict(l=10, r=10, t=50, b=10),
            paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
            font_color="white", showlegend=False,
            hovermode="x unified",
        )
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True, key="mc_probs")

        st.markdown("### 📊 Tabla completa de probabilidades")
        display_cols = ["team", "wins", "wins_pct", "finals", "finals_pct",
                        "semis", "semis_pct", "quarters", "quarters_pct"]
        display_df = mc[display_cols].copy()
        display_df.columns = ["Equipo", "Campeón (#)", "Campeón (%)",
                              "Final (#)", "Final (%)", "Semis (#)",
                              "Semis (%)", "Cuartos (#)", "Cuartos (%)"]
        st.dataframe(display_df, use_container_width=True)

        st.markdown("### 📈 Distribución de favoritos")
        fig2 = px.pie(
            mc.head(8), values="wins", names="team",
            title="Top 8 favoritos al título",
            color_discrete_sequence=px.colors.qualitative.Set2,
            hole=0.4,
        )
        fig2.update_traces(textposition="inside", textinfo="label+percent")
        fig2.update_layout(
            height=400, margin=dict(l=10, r=10, t=40, b=10),
            paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
            font_color="white",
            showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True, key="mc_pie")

        st.download_button(
            "📥 Descargar resultados CSV",
            mc.to_csv(index=False),
            "worldcup_2026_montecarlo.csv",
            "text/csv",
            use_container_width=True,
        )

        if st.session_state.get("telegram_connected") and st.session_state.get("telegram_chat_id"):
            if st.button("📤 Enviar resultados a Telegram", use_container_width=True):
                from utils.telegram_bot import send_message
                top3 = mc.head(3)
                msg = (
                    f"🏆 <b>SIMULACIÓN MUNDIAL 2026</b> 🏆\n"
                    f"{'━'*30}\n"
                    f"🔄 <b>{n_sims:,} simulaciones</b>\n\n"
                    f"<b>Top Favoritos:</b>\n"
                )
                for i, (_, row) in enumerate(top3.iterrows()):
                    msg += f"{i+1}. {row['team']}: {row['wins_pct']:.1f}% 🏆\n"
                msg += (
                    f"\n<b>Probabilidades:</b>\n"
                    f"🏆 Campeón: {top3.iloc[0]['team']} ({top3.iloc[0]['wins_pct']:.1f}%)\n"
                    f"🥇 Final: {top3.iloc[0]['team']} ({top3.iloc[0]['finals_pct']:.1f}%)\n"
                    f"{'━'*30}\n"
                    f"🤖 World Cup 2026 · Monte Carlo AI"
                )
                resp = send_message(st.session_state.telegram_chat_id, msg)
                if resp.get("ok"):
                    st.success("✅ Resultados enviados a Telegram!")
                else:
                    st.error(f"❌ Error")

with tab3:
    st.markdown("### ⚔️ Partido Rápido")

    col_a, col_b = st.columns(2)
    with col_a:
        t1 = st.selectbox("Equipo A", sorted(simulator.groups.keys()), key="quick_team_a")
        team_a_name = simulator.groups[t1][0] if t1 in simulator.groups else "Argentina"
        team_a_name = st.selectbox("Seleccionar equipo",
                                   [t for grp in simulator.groups.values() for t in grp],
                                   index=0, key="qa_team")
    with col_b:
        team_b_name = st.selectbox("Seleccionar rival",
                                   [t for grp in simulator.groups.values() for t in grp],
                                   index=1, key="qb_team")

    if team_a_name == team_b_name:
        st.warning("⚠️ Selecciona dos equipos diferentes")
    else:
        if st.button("⚽ Simular Partido", type="primary", use_container_width=True):
            match = simulate_match(team_a_name, team_b_name, seed=int(np.random.randint(0, 10000)))

            st.balloons()
            st.markdown(f"## 📋 {team_a_name} {match['goals_a']} - {match['goals_b']} {team_b_name}")

            cols = st.columns(3)
            with cols[0]:
                st.markdown(f"### {team_a_name}")
                st.metric("Goles", match["goals_a"])
                st.metric("Tiros", match["shots_a"])
                st.metric("Posesión", f"{match['possession_a']}%")
                st.metric("xG", match["xg_a"])
            with cols[1]:
                st.markdown("### ⚡ Resumen")
                st.markdown(f"**{match['goals_a'] + match['goals_b']}** goles")
                st.markdown(f"**{match['shots_a'] + match['shots_b']}** tiros")
                st.markdown(f"Estilo: **{match['style_a'].title()}** vs **{match['style_b'].title()}**")
                if match["goals_a"] > match["goals_b"]:
                    st.success(f"🏆 **Gana {team_a_name}**")
                elif match["goals_a"] == match["goals_b"]:
                    st.warning("🤝 **Empate**")
                else:
                    st.success(f"🏆 **Gana {team_b_name}**")
            with cols[2]:
                st.markdown(f"### {team_b_name}")
                st.metric("Goles", match["goals_b"])
                st.metric("Tiros", match["shots_b"])
                st.metric("Posesión", f"{match['possession_b']}%")
                st.metric("xG", match["xg_b"])

            st.markdown("---")
            st.markdown("### 📊 Comparativa")

            stats_df = pd.DataFrame({
                "Métrica": ["Goles", "Tiros", "Posesión", "xG"],
                team_a_name: [match["goals_a"], match["shots_a"],
                              match["possession_a"], match["xg_a"]],
                team_b_name: [match["goals_b"], match["shots_b"],
                              match["possession_b"], match["xg_b"]],
            })

            fig3 = go.Figure()
            fig3.add_trace(go.Bar(
                name=team_a_name, x=stats_df["Métrica"],
                y=stats_df[team_a_name],
                marker_color="#00d4ff",
                text=stats_df[team_a_name],
                textposition="outside",
            ))
            fig3.add_trace(go.Bar(
                name=team_b_name, x=stats_df["Métrica"],
                y=stats_df[team_b_name],
                marker_color="#ff6b6b",
                text=stats_df[team_b_name],
                textposition="outside",
            ))
            fig3.update_layout(
                barmode="group", height=350,
                paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
                font_color="white", margin=dict(l=10, r=10, t=10, b=10),
            )
            st.plotly_chart(fig3, use_container_width=True, key="quick_match")

            if st.session_state.get("telegram_connected") and st.session_state.get("telegram_chat_id"):
                if st.button("📤 Enviar resultado a Telegram", key="tg_quick_match"):
                    from utils.telegram_bot import send_message
                    winner = team_a_name if match["goals_a"] > match["goals_b"] else (
                        team_b_name if match["goals_b"] > match["goals_a"] else "Empate"
                    )
                    msg = (
                        f"⚔️ <b>PARTIDO RÁPIDO</b> ⚔️\n"
                        f"{'━'*25}\n"
                        f"<b>{team_a_name} {match['goals_a']} - {match['goals_b']} {team_b_name}</b>\n\n"
                        f"🏆 <b>Ganador:</b> {winner}\n"
                        f"⚽ xG: {match['xg_a']} - {match['xg_b']}\n"
                        f"🎯 Tiros: {match['shots_a']} - {match['shots_b']}\n"
                        f"⚡ Posesión: {match['possession_a']}% - {match['possession_b']}%\n"
                        f"{'━'*25}\n"
                        f"🎲 World Cup 2026 · Simulación"
                    )
                    resp = send_message(st.session_state.telegram_chat_id, msg)
                    if resp.get("ok"):
                        st.success("✅ Resultado enviado a Telegram!")
