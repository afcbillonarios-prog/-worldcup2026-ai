import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

st.set_page_config(page_title="Heatmaps Tácticos - Mundial 2026", page_icon="🗺️", layout="wide")

st.markdown("# 🗺️ Mapas de Calor Tácticos")
st.markdown("### Visualización de ocupación espacial, presión y movimientos tácticos")

np.random.seed(42)

def generate_pitch_coords(n_points=200, zone="full"):
    if zone == "full":
        x = np.random.uniform(0, 105, n_points)
        y = np.random.uniform(0, 68, n_points)
    elif zone == "attack":
        x = np.random.uniform(52.5, 105, n_points)
        y = np.random.uniform(0, 68, n_points)
    elif zone == "midfield":
        x = np.random.uniform(30, 75, n_points)
        y = np.random.uniform(0, 68, n_points)
    elif zone == "defense":
        x = np.random.uniform(0, 52.5, n_points)
        y = np.random.uniform(0, 68, n_points)
    elif zone == "left_wing":
        x = np.random.uniform(0, 105, n_points)
        y = np.random.uniform(0, 25, n_points)
    elif zone == "right_wing":
        x = np.random.uniform(0, 105, n_points)
        y = np.random.uniform(43, 68, n_points)
    return x, y

def generate_pressing_coords(team_style="high"):
    n = 300
    if team_style == "high":
        x = np.random.normal(75, 20, n)
        y = np.random.uniform(0, 68, n)
    elif team_style == "mid":
        x = np.random.normal(55, 15, n)
        y = np.random.uniform(0, 68, n)
    else:
        x = np.random.normal(30, 20, n)
        y = np.random.uniform(0, 68, n)
    x = np.clip(x, 0, 105)
    return x, y

def generate_tactical_movement(formation="4-3-3"):
    positions = {
        "4-3-3": [(50, 60, 20), (50, 20, 20), (15, 40, 15), (85, 40, 15),
                  (30, 45, 15), (55, 40, 15), (75, 45, 15),
                  (20, 25, 12), (50, 15, 12), (80, 25, 12)],
        "4-4-2": [(50, 60, 20), (50, 20, 20), (15, 40, 15), (85, 40, 15),
                  (25, 50, 15), (75, 50, 15), (25, 30, 15), (75, 30, 15),
                  (35, 15, 12), (65, 15, 12)],
        "3-5-2": [(50, 60, 20), (30, 20, 18), (50, 15, 18), (70, 20, 18),
                  (15, 45, 15), (40, 40, 15), (60, 40, 15), (85, 45, 15),
                  (30, 15, 12), (70, 15, 12)],
    }
    base = positions.get(formation, positions["4-3-3"])
    coords = []
    for x, y, rad in base:
        n_pts = 20
        xs = np.random.normal(x, rad / 2, n_pts)
        ys = np.random.normal(y, rad / 2, n_pts)
        xs = np.clip(xs, 0, 105)
        ys = np.clip(ys, 0, 68)
        coords.extend(zip(xs, ys))
    xs, ys = zip(*coords) if coords else ([], [])
    return np.array(xs), np.array(ys)

st.markdown("---")
tab1, tab2, tab3 = st.tabs(["🗺️ Ocupación Espacial", "🔥 Presión Táctica", "⚽ Formaciones"])

with tab1:
    st.markdown("### Ocupación espacial por zona de juego")

    col1, col2, col3 = st.columns(3)
    with col1:
        zone = st.selectbox("Zona del campo",
                           ["full", "attack", "midfield", "defense", "left_wing", "right_wing"],
                           format_func=lambda x: {
                               "full": "Campo completo",
                               "attack": "Ataque",
                               "midfield": "Mediocampo",
                               "defense": "Defensa",
                               "left_wing": "Banda izquierda",
                               "right_wing": "Banda derecha"
                           }.get(x, x),
                           key="zone_select")
    with col2:
        n_points = st.slider("Cantidad de eventos", 100, 1000, 300, key="n_heat_points")
    with col3:
        team_name = st.text_input("Nombre del equipo", "Selección Nacional", key="heat_team")
        color_scheme = st.selectbox("Esquema de color",
                                   ["Reds", "Blues", "Greens", "Purples", "Oranges", "Viridis"],
                                   key="color_scheme")

    x, y = generate_pitch_coords(n_points, zone)

    fig = go.Figure()

    fig.add_shape(type="rect", x0=0, y0=0, x1=105, y1=68,
                  line=dict(color="rgba(255,255,255,0.3)", width=2),
                  fillcolor="rgba(26,71,42,0.5)")

    fig.add_shape(type="line", x0=52.5, y0=0, x1=52.5, y1=68,
                  line=dict(color="rgba(255,255,255,0.3)", width=1.5, dash="dash"))

    for x_pos in [0, 16.5, 30]:
        fig.add_shape(type="rect", x0=x_pos, y0=13.85, x1=x_pos + 5.5 if x_pos == 0 else x_pos + 40 if x_pos == 16.5 else x_pos + 5.5,
                     y1=54.15 if x_pos in [0, 30] else 54.15,
                     line=dict(color="rgba(255,255,255,0.2)", width=1))

    fig.add_trace(go.Histogram2dContour(
        x=x, y=y,
        colorscale=color_scheme,
        ncontours=15,
        contours=dict(coloring="heatmap"),
        hovertemplate="x: %{x:.0f}<br>y: %{y:.0f}<br>Densidad: %{z}<extra></extra>",
        showscale=True,
        colorbar=dict(title="Densidad", tickfont=dict(color="white"),
                     titlefont=dict(color="white")),
    ))

    fig.update_layout(
        title=f"Mapa de calor - {team_name} ({zone})",
        width=700, height=450,
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font_color="white",
        xaxis=dict(range=[0, 105], showgrid=False, zeroline=False,
                   tickvals=[0, 25, 50, 75, 100], title=""),
        yaxis=dict(range=[0, 68], showgrid=False, zeroline=False,
                   tickvals=[0, 17, 34, 51, 68], title="",
                   scaleanchor="x", scaleratio=1),
        margin=dict(l=10, r=10, t=40, b=10),
    )
    st.plotly_chart(fig, use_container_width=True, key="heatmap_main")

    st.markdown("### Distribución por zonas")
    zones_x = ["Defensa (0-35m)", "Mediocampo (35-70m)", "Ataque (70-105m)"]
    zones_counts = [
        sum((x >= 0) & (x < 35)),
        sum((x >= 35) & (x < 70)),
        sum((x >= 70) & (x <= 105)),
    ]
    zone_df = pd.DataFrame({"Zona": zones_x, "Eventos": zones_counts})
    fig2 = px.bar(zone_df, x="Zona", y="Eventos",
                  color="Zona", text_auto=True,
                  color_discrete_sequence=["#ff6b6b", "#ffd93d", "#00d4ff"])
    fig2.update_layout(
        height=250, margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font_color="white", showlegend=False,
    )
    st.plotly_chart(fig2, use_container_width=True, key="zone_dist")

with tab2:
    st.markdown("### Mapa de presión táctica")

    col1, col2 = st.columns(2)
    with col1:
        press_style = st.selectbox("Estilo de presión",
                                  ["high", "mid", "low"],
                                  format_func=lambda x: {
                                      "high": "Presión alta (contraataque)",
                                      "mid": "Presión media (equilibrado)",
                                      "low": "Presión baja (repliegue)"
                                  }.get(x, x),
                                  key="press_style")
    with col2:
        formation = st.selectbox("Formación", ["4-3-3", "4-4-2", "3-5-2"], key="press_formation")

    px_coords, py_coords = generate_pressing_coords(press_style)
    tx_coords, ty_coords = generate_tactical_movement(formation)

    fig = go.Figure()

    fig.add_shape(type="rect", x0=0, y0=0, x1=105, y1=68,
                  line=dict(color="rgba(255,255,255,0.3)", width=2),
                  fillcolor="rgba(26,71,42,0.5)")

    fig.add_trace(go.Histogram2dContour(
        x=px_coords, y=py_coords,
        colorscale="Hot",
        ncontours=12,
        contours=dict(coloring="heatmap"),
        name="Presión",
        hovertemplate="x: %{x:.0f}<br>y: %{y:.0f}<br>Intensidad: %{z}<extra></extra>",
        showscale=True,
        colorbar=dict(title="Presión", tickfont=dict(color="white"),
                     titlefont=dict(color="white")),
    ))

    if st.checkbox("Mostrar posición de jugadores", value=True):
        fig.add_trace(go.Scatter(
            x=tx_coords, y=ty_coords,
            mode="markers",
            marker=dict(color="#00d4ff", size=8, symbol="x",
                       line=dict(color="white", width=1)),
            name=f"Jugadores ({formation})",
            hovertemplate="x: %{x:.0f}<br>y: %{y:.0f}<extra></extra>",
        ))

    fig.update_layout(
        title=f"Presión táctica: {press_style.upper()} | Formación: {formation}",
        width=700, height=450,
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font_color="white",
        xaxis=dict(range=[0, 105], showgrid=False, zeroline=False,
                   tickvals=[0, 25, 50, 75, 100], title=""),
        yaxis=dict(range=[0, 68], showgrid=False, zeroline=False,
                   tickvals=[0, 17, 34, 51, 68], title="",
                   scaleanchor="x", scaleratio=1),
        margin=dict(l=10, r=10, t=40, b=10),
    )
    st.plotly_chart(fig, use_container_width=True, key="press_heatmap")

    st.markdown("### 📊 Intensidad de presión por sector")
    sectors = ["Defensa baja", "Defensa alta", "Mediocampo", "Ataque"]
    intensity = {
        "high": [20, 40, 80, 90],
        "mid": [40, 60, 70, 40],
        "low": [70, 60, 30, 10],
    }
    intens = intensity.get(press_style, intensity["mid"])
    df_int = pd.DataFrame({"Sector": sectors, "Intensidad": intens})

    fig3 = px.line(df_int, x="Sector", y="Intensidad", markers=True,
                   title="Intensidad de presión por sector del campo")
    fig3.update_traces(line_color="#ff6b6b", marker=dict(size=10, color="#ff6b6b"))
    fig3.update_layout(
        height=250, margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font_color="white",
        yaxis=dict(range=[0, 100]),
    )
    st.plotly_chart(fig3, use_container_width=True, key="press_intensity")

with tab3:
    st.markdown("### Comparador de formaciones tácticas")

    col1, col2 = st.columns(2)
    with col1:
        form1 = st.selectbox("Formación A", ["4-3-3", "4-4-2", "3-5-2"], index=0, key="form1")
    with col2:
        form2 = st.selectbox("Formación B", ["4-3-3", "4-4-2", "3-5-2"], index=1, key="form2")

    fx1, fy1 = generate_tactical_movement(form1)
    fx2, fy2 = generate_tactical_movement(form2)

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(f"Formación {form1}", f"Formación {form2}"),
        specs=[[{"type": "scatter"}, {"type": "scatter"}]],
        horizontal_spacing=0.05,
    )

    for fig_data, f, fx, fy, color, tag in [
        (fig, form1, fx1, fy1, "#00d4ff", "A"),
        (fig, form2, fx2, fy2, "#ff6b6b", "B")
    ]:
        row = 1 if tag == "A" else 1
        col = 1 if tag == "A" else 2
        fig_data.add_trace(
            go.Scatter(x=fx, y=fy, mode="markers",
                      marker=dict(color=color, size=7, symbol="x",
                                 line=dict(color="white", width=0.5)),
                      name=f, showlegend=False),
            row=row, col=col
        )
        fig_data.add_shape(type="rect", x0=0, y0=0, x1=105, y1=68,
                          line=dict(color="rgba(255,255,255,0.2)", width=1),
                          fillcolor="rgba(26,71,42,0.3)",
                          row=row, col=col)
        fig_data.add_shape(type="line", x0=52.5, y0=0, x1=52.5, y1=68,
                          line=dict(color="rgba(255,255,255,0.2)", width=1, dash="dash"),
                          row=row, col=col)

    fig.update_layout(
        height=400, margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font_color="white",
    )
    fig.update_xaxes(range=[0, 105], showgrid=False, zeroline=False, tickvals=[],
                     row=1, col=1)
    fig.update_xaxes(range=[0, 105], showgrid=False, zeroline=False, tickvals=[],
                     row=1, col=2)
    fig.update_yaxes(range=[0, 68], showgrid=False, zeroline=False, tickvals=[],
                     scaleanchor="x", scaleratio=1, row=1, col=1)
    fig.update_yaxes(range=[0, 68], showgrid=False, zeroline=False, tickvals=[],
                     scaleanchor="x", scaleratio=1, row=1, col=2)
    st.plotly_chart(fig, use_container_width=True, key="formations")

    st.markdown("### ⚙️ Análisis táctico comparativo")
    analysis = {
        "Métrica": ["Cobertura ofensiva", "Cobertura defensiva", "Amplitud",
                    "Ocupación mediocampo", "Profundidad"],
        form1: [8, 7, 9, 7, 8],
        form2: [7, 8, 7, 8, 7],
    }
    df_analysis = pd.DataFrame(analysis)
    fig4 = px.line_polar(df_analysis, r=form1, theta="Métrica",
                         line_close=True, range_r=[0, 10],
                         color_discrete_sequence=["#00d4ff"])
    fig4.add_trace(go.Scatterpolar(
        r=df_analysis[form2], theta=df_analysis["Métrica"],
        fill="toself", name=form2,
        line_color="#ff6b6b", fillcolor="rgba(255,107,107,0.1)"
    ))
    fig4.update_layout(
        height=400, margin=dict(l=40, r=40, t=10, b=10),
        paper_bgcolor="#0e1117", font_color="white",
        polar=dict(bgcolor="rgba(0,0,0,0.3)",
                   radialaxis=dict(range=[0, 10], showticklabels=True,
                                  tickfont=dict(color="white"))),
        showlegend=True, legend=dict(font=dict(color="white")),
    )
    st.plotly_chart(fig4, use_container_width=True, key="tactical_radar")
