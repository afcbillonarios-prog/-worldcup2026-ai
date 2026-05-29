import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from data.players import generate_players, PLAYER_NAMES
from models.scouting import ScoutingEngine

st.set_page_config(page_title="Scouting IA - Mundial 2026", page_icon="🔍", layout="wide")

st.markdown("# 🔍 Scouting IA — Detección de Talentos")
st.markdown("### Clustering K-Means + PCA para análisis de perfiles y detección de talentos ocultos")

if "players_df" not in st.session_state:
    with st.spinner("Generando base de datos de jugadores..."):
        st.session_state.players_df = generate_players(150)
        st.session_state.scouting = ScoutingEngine(st.session_state.players_df)

players = st.session_state.players_df
scouting = st.session_state.scouting

st.markdown("---")
tab1, tab2, tab3, tab4 = st.tabs(
    ["🗺️ Mapa de Talentos", "🔎 Buscar Similar", "💎 Infravalorados", "📊 Resumen Clusters"]
)

with tab1:
    st.markdown("### Mapa de talentos (PCA + K-Means)")

    col_filters, col_plot = st.columns([1, 3])

    with col_filters:
        min_overall = st.slider("Overall mínimo", 55, 99, 60, key="scout_min_overall")
        positions = st.multiselect(
            "Posiciones",
            ["POR", "DEF", "MED", "DEL", "EXT"],
            default=["DEL", "EXT", "MED"],
            key="scout_positions"
        )
        teams_filter = st.multiselect(
            "Selecciones",
            sorted(players["team"].unique()),
            default=[],
            key="scout_teams"
        )

    filtered = players[(players["overall"] >= min_overall) &
                       (players["position"].isin(positions))]
    if teams_filter:
        filtered = filtered[filtered["team"].isin(teams_filter)]

    with col_plot:
        fig = px.scatter(
            filtered, x="pca_x", y="pca_y",
            color="cluster_name", size="overall",
            hover_data=["name", "team", "position", "overall", "market_value"],
            title="Mapa dimensional de jugadores (PCA)",
            color_discrete_sequence=px.colors.qualitative.Set2,
            size_max=15,
        )
        fig.update_layout(
            height=500, margin=dict(l=10, r=10, t=40, b=10),
            paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
            font_color="white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02,
                       xanchor="right", x=1),
        )
        fig.update_xaxes(showgrid=False, zeroline=False)
        fig.update_yaxes(showgrid=False, zeroline=False)
        st.plotly_chart(fig, use_container_width=True, key="pca_clusters")

    st.markdown(f"Mostrando {len(filtered)} jugadores de {len(players)} totales")

with tab2:
    st.markdown("### Buscador de jugadores similares")

    col_search, col_result = st.columns([1, 2])

    with col_search:
        search_name = st.selectbox(
            "Jugador de referencia",
            players["name"].unique(),
            key="similar_player"
        )
        n_similar = st.slider("Cantidad de similares", 3, 15, 5, key="n_similar")

        if st.button("🔎 Buscar similares", type="primary", use_container_width=True):
            similar = scouting.find_similar(search_name, n=n_similar)
            st.session_state.similar_result = similar

        target = players[players["name"] == search_name]
        if not target.empty:
            t = target.iloc[0]
            st.markdown(f"### {t['name']}")
            st.markdown(f"**Equipo:** {t['team']}")
            st.markdown(f"**Posición:** {t['position']}")
            st.markdown(f"**Overall:** {t['overall']}")
            st.markdown(f"**Cluster:** {t['cluster_name']}")
            st.markdown(f"**Valor:** €{t['market_value']}M")

            categories = ["pace", "shooting", "passing", "dribbling", "defending", "physical"]
            values = [t[c] for c in categories]
            values += values[:1]
            angles = list(np.linspace(0, 2 * np.pi, len(categories), endpoint=False))
            angles += angles[:1]

            fig = go.Figure(go.Scatterpolar(
                r=values, theta=categories + categories[:1],
                fill="toself", name=t["name"],
                line_color="#00d4ff", fillcolor="rgba(0,212,255,0.2)"
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(range=[0, 100], visible=True)),
                showlegend=False, height=300,
                paper_bgcolor="#0e1117", font_color="white",
                margin=dict(l=10, r=10, t=10, b=10),
            )
            st.plotly_chart(fig, use_container_width=True, key="target_radar")

    with col_result:
        if "similar_result" in st.session_state:
            similar = st.session_state.similar_result
            st.markdown(f"### Jugadores similares a {search_name}")

            for _, row in similar.iterrows():
                cols = st.columns([3, 1, 1, 1])
                with cols[0]:
                    st.markdown(f"**{row['name']}**")
                    st.caption(f"{row['team']} · {row['position']}")
                with cols[1]:
                    st.metric("Overall", row["overall"])
                with cols[2]:
                    st.metric("Similitud", f"{row['similarity']:.0f}%")
                with cols[3]:
                    st.metric("Valor", f"€{row['market_value']}M")

                st.progress(row["similarity"] / 100,
                           text=f"Coincidencia: {row['similarity']:.0f}%")
                st.markdown("---")

with tab3:
    st.markdown("### 💎 Talentos Infravalorados")
    st.markdown("Jugadores con alto rendimiento relativo a su valor de mercado")

    min_ovr = st.slider("Overall mínimo", 70, 90, 75, key="undervalued_min")
    undervalued = scouting.find_undervalued(min_overall=min_ovr, n=15)

    col1, col2 = st.columns([2, 1])

    with col1:
        fig = px.scatter(
            undervalued, x="market_value", y="overall",
            size="overall", color="position",
            hover_data=["name", "team", "age"],
            text="name",
            title="Relación Valor de Mercado vs Overall",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig.update_traces(textposition="top center", textfont=dict(size=10))
        fig.update_layout(
            height=450, margin=dict(l=10, r=10, t=40, b=10),
            paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
            font_color="white",
        )
        st.plotly_chart(fig, use_container_width=True, key="undervalued_chart")

    with col2:
        st.markdown("### Top Infravalorados")
        for i, (_, row) in enumerate(undervalued.head(10).iterrows()):
            st.markdown(f"**{i+1}. {row['name']}**")
            st.caption(f"{row['team']} · {row['position']} · {row['age']} años")
            st.markdown(f"Overall: {row['overall']} | Valor: €{row['market_value']}M")
            ratio = row["overall"] / (row["market_value"] + 1)
            st.progress(min(ratio / 3, 1), text=f"Relación: {ratio:.1f}")
            st.markdown("---")

    st.dataframe(
        undervalued[["name", "team", "position", "age", "overall", "market_value"]],
        use_container_width=True,
        column_config={"market_value": st.column_config.NumberColumn("Valor (€M)", format="€%.1fM")},
    )

with tab4:
    st.markdown("### 📊 Resumen por Cluster")

    summary = scouting.get_cluster_summary()
    st.dataframe(summary, use_container_width=True)

    cluster_colors = {
        "Creadores": "#00d4ff", "Finalizadores": "#ff6b6b",
        "Destructores": "#ff8c00", "Velocistas": "#ffd93d",
        "Técnicos": "#7b2ff7", "Versátiles": "#00ff88"
    }
    color_seq = [cluster_colors.get(c, "#00d4ff") for c in summary.index]

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Distribución de Clusters", "Overall promedio"),
        specs=[[{"type": "pie"}, {"type": "bar"}]]
    )

    fig.add_trace(
        go.Pie(labels=summary.index, values=summary["count"],
               marker_colors=color_seq, hole=0.4,
               textinfo="label+percent"),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(x=summary.index, y=summary["avg_overall"],
               marker_color=color_seq,
               text=summary["avg_overall"].round(1),
               textposition="outside"),
        row=1, col=2
    )

    fig.update_layout(
        height=400, margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font_color="white",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, key="cluster_summary")

    cluster_df = players.groupby("cluster_name").agg(
        Jugadores=("id", "count"),
        Overall_Prom=("overall", "mean"),
        Edad_Prom=("age", "mean"),
        Valor_Prom=("market_value", "mean"),
        Mejor_Jugador=("name", lambda x: x.iloc[players.loc[x.index, "overall"].idxmax()]),
    ).round(1)
    st.dataframe(cluster_df, use_container_width=True)
