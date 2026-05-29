import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from models.xg_model import XGModel

st.set_page_config(page_title="Sistema xG - Mundial 2026", page_icon="🎯", layout="wide")

st.markdown("# 🎯 Sistema de Expected Goals (xG)")
st.markdown("### Modelo de regresión logística: probabilidad de gol basada en 7 variables")

if "xg_model" not in st.session_state:
    with st.spinner("Entrenando modelo xG..."):
        st.session_state.xg_model = XGModel()
model = st.session_state.xg_model

st.markdown("---")
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### ⚙️ Parámetros del tiro")
    distance = st.slider("Distancia al arco (metros)", 0.5, 35.0, 15.0, 0.5)
    angle = st.slider("Ángulo del tiro (grados)", 0.0, 90.0, 30.0, 1.0)
    pressure = st.slider("Presión defensiva (0-1)", 0.0, 1.0, 0.3, 0.05)
    speed = st.slider("Velocidad del balón (km/h)", 0.0, 30.0, 20.0, 0.5)
    is_header = st.checkbox("Remate de cabeza")
    through_ball = st.checkbox("Pase filtrado / asistencia")
    strong_foot = st.checkbox("Pie dominante")

    if st.button("🎯 Calcular xG", type="primary", use_container_width=True):
        xg_value = model.predict_xg(
            distance, angle, pressure, speed,
            is_header, through_ball, strong_foot
        )

        st.markdown("---")
        st.markdown("### 📊 Resultado")

        percentage = xg_value * 100

        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=percentage,
            number={"suffix": "%", "font": {"color": "white", "size": 36}},
            title={"text": "Probabilidad de Gol (xG)", "font": {"color": "white", "size": 16}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "white", "dtick": 10},
                "bar": {"color": "rgba(0,212,255,0.9)", "thickness": 0.6},
                "bgcolor": "rgba(0,0,0,0.3)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 10], "color": "rgba(255,50,50,0.3)"},
                    {"range": [10, 30], "color": "rgba(255,200,50,0.3)"},
                    {"range": [30, 60], "color": "rgba(50,200,100,0.3)"},
                    {"range": [60, 100], "color": "rgba(0,200,255,0.3)"},
                ],
                "threshold": {
                    "line": {"color": "white", "width": 4},
                    "thickness": 0.75,
                    "value": percentage,
                },
            }
        ))
        fig.update_layout(
            height=300, margin=dict(l=30, r=30, t=50, b=30),
            paper_bgcolor="#0e1117", font={"color": "white"},
        )
        st.plotly_chart(fig, use_container_width=True, key="xg_gauge")

        if xg_value > 0.5:
            st.success(f"🔴 ¡CLARÍSIMA! xG = {xg_value:.2%}")
        elif xg_value > 0.25:
            st.warning(f"🟡 Buena oportunidad. xG = {xg_value:.2%}")
        elif xg_value > 0.1:
            st.info(f"🔵 Oportunidad moderada. xG = {xg_value:.2%}")
        else:
            st.error(f"⚪ Baja probabilidad. xG = {xg_value:.2%}")

with col2:
    st.markdown("### 🧠 Superficie de xG")

    dist_range = np.linspace(1, 35, 30)
    angle_range = np.linspace(0, 90, 30)
    D, A = np.meshgrid(dist_range, angle_range)

    Z = np.zeros_like(D)
    for i in range(len(dist_range)):
        for j in range(len(angle_range)):
            Z[j, i] = model.predict_xg(
                float(D[j, i]), float(A[j, i]),
                pressure=pressure, speed=speed,
                is_header=is_header, through_ball=through_ball,
                strong_foot=strong_foot
            )

    fig = go.Figure(data=[
        go.Contour(z=Z * 100, x=dist_range, y=angle_range,
                   colorscale="Hot", contours=dict(coloring="heatmap"),
                   hovertemplate="Dist: %{x:.0f}m<br>Ángulo: %{y:.0f}°<br>xG: %{z:.1f}%<extra></extra>",
                   line=dict(width=0.5, color="rgba(255,255,255,0.3)"),
                   ncontours=20)
    ])
    fig.update_layout(
        title="xG por distancia y ángulo",
        xaxis_title="Distancia (m)",
        yaxis_title="Ángulo (°)",
        height=400, margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font_color="white",
        xaxis=dict(range=[0, 35]),
        yaxis=dict(range=[0, 90]),
    )
    st.plotly_chart(fig, use_container_width=True, key="xg_surface")

st.markdown("---")
st.markdown("### 📊 Simulador de Tiros")

if st.button("🔄 Generar tiros aleatorios", use_container_width=True):
    n_shots = st.number_input("Cantidad de tiros", 5, 50, 15, key="n_shots_display")
    shots = []
    for _ in range(15):
        shots.append(model.simulate_shot())

    df_shots = pd.DataFrame(shots)
    df_shots["goal_label"] = df_shots["goal"].map({True: "⚽ Gol", False: "❌ No gol"})

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("xG por tiro", "Distribución de xG"),
        column_widths=[0.6, 0.4]
    )

    colors = ["#00ff88" if g else "#ff4444" for g in df_shots["goal"]]
    fig.add_trace(
        go.Bar(x=list(range(len(df_shots))), y=df_shots["xG"],
               marker_color=colors,
               text=[f'{v:.1%}' for v in df_shots["xG"]],
               textposition="outside",
               name="xG"),
        row=1, col=1
    )

    goals = df_shots[df_shots["goal"] == True]
    nogoals = df_shots[df_shots["goal"] == False]
    fig.add_trace(
        go.Histogram(x=df_shots["xG"], nbinsx=15,
                     marker_color="#00d4ff", name="Distribución"),
        row=1, col=2
    )

    fig.update_layout(
        height=350, margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font_color="white",
        showlegend=False,
        xaxis1_title="Tiro #", yaxis1_title="xG",
        xaxis2_title="xG", yaxis2_title="Frecuencia",
        bargap=0.3,
    )
    fig.update_xaxes(range=[-0.5, len(df_shots) - 0.5], row=1, col=1)
    st.plotly_chart(fig, use_container_width=True, key="shots_chart")

    st.markdown(f"**Total:** {df_shots['xG'].sum():.2f} xG | "
                f"⚽ Goles: {df_shots['goal'].sum()}/{len(df_shots)} | "
                f"📊 xG promedio: {df_shots['xG'].mean():.3f}")

    st.dataframe(
        df_shots.style.applymap(
            lambda x: "color: #00ff88" if x else "color: #ff4444",
            subset=["goal"]
        ),
        use_container_width=True,
        column_config={
            "xG": st.column_config.NumberColumn(format="%.1%"),
            "goal": st.column_config.CheckboxColumn(),
        }
    )
