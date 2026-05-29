import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import cv2

st.set_page_config(page_title="Tracking CV - Mundial 2026", page_icon="👁️", layout="wide")

st.markdown("# 👁️ Tracking con Visión Computacional")
st.markdown("### Simulación del pipeline de tracking de jugadores con YOLO + OpenCV")

st.markdown("---")
tab1, tab2, tab3 = st.tabs(["📡 Tracking en Vivo", "🎯 Pipeline CV", "📊 Métricas Físicas"])

with tab1:
    st.markdown("### Simulación de tracking en tiempo real")

    col1, col2 = st.columns([1, 2])

    with col1:
        formation = st.selectbox("Formación a visualizar",
                                ["4-3-3", "4-4-2", "3-5-2", "5-3-2"], key="track_form")
        show_ball = st.checkbox("Mostrar balón", value=True, key="show_ball")
        show_movement = st.checkbox("Mostrar vectores de movimiento", value=True, key="show_movement")

        n_frames = st.slider("Frames a simular", 10, 200, 50, key="n_frames")
        speed_factor = st.slider("Velocidad de simulación", 1, 10, 5, key="speed_factor")

        if st.button("▶️ Iniciar Tracking", type="primary", use_container_width=True):
            st.session_state.tracking_active = True

        if st.button("⏹️ Detener", use_container_width=True):
            st.session_state.tracking_active = False

    formations_pos = {
        "4-3-3": [(20, 60), (15, 35), (50, 70), (85, 35),
                  (30, 50), (50, 50), (70, 50),
                  (20, 20), (50, 15), (80, 20)],
        "4-4-2": [(20, 60), (15, 35), (50, 70), (85, 35),
                  (25, 55), (75, 55), (25, 25), (75, 25),
                  (35, 15), (65, 15)],
        "3-5-2": [(20, 60), (50, 70), (80, 60),
                  (15, 50), (35, 55), (50, 50), (65, 55), (85, 50),
                  (30, 20), (70, 20)],
        "5-3-2": [(20, 68), (10, 45), (25, 35), (50, 30), (75, 35), (90, 45),
                  (30, 55), (50, 55), (70, 55),
                  (30, 20), (70, 20)],
    }

    with col2:
        plot_placeholder = st.empty()

        if st.session_state.get("tracking_active", False):
            base_pos = np.array(formations_pos.get(formation, formations_pos["4-3-3"]))
            ball_pos = np.array([52.5, 34.0])
            velocities = np.random.uniform(-3, 3, size=(len(base_pos), 2))
            ball_vel = np.random.uniform(-2, 2, size=(2,))
            frame = 0

            for frame in range(min(n_frames, 200)):
                if not st.session_state.get("tracking_active", False):
                    break

                base_pos = base_pos + velocities * 0.5
                base_pos = np.clip(base_pos, [0, 0], [105, 68])
                velocities = velocities + np.random.uniform(-1, 1, size=(len(base_pos), 2))
                velocities = np.clip(velocities, -4, 4)

                if frame % 5 == 0:
                    ball_pos = ball_pos + ball_vel
                    ball_vel = ball_vel + np.random.uniform(-1, 1, size=(2,))
                    ball_vel = np.clip(ball_vel, -3, 3)
                ball_pos = np.clip(ball_pos, [10, 10], [95, 58])

                fig = go.Figure()

                fig.add_shape(type="rect", x0=0, y0=0, x1=105, y1=68,
                              line=dict(color="rgba(255,255,255,0.4)", width=2),
                              fillcolor="rgba(26,71,42,0.7)")

                for x_line in [0, 16.5, 30, 52.5, 75, 88.5, 105]:
                    fig.add_shape(type="line", x0=x_line, y0=0,
                                 x1=x_line, y1=68,
                                 line=dict(color="rgba(255,255,255,0.2)", width=1))

                for y_line in [0, 13.85, 34, 54.15, 68]:
                    fig.add_shape(type="line", x0=0, y0=y_line,
                                 x1=105, y1=y_line,
                                 line=dict(color="rgba(255,255,255,0.2)", width=1))

                colors = plt.cm.rainbow(np.linspace(0, 1, len(base_pos)))
                for i, (x, y) in enumerate(base_pos):
                    player_id = i + 1
                    fig.add_trace(go.Scatter(
                        x=[x], y=[y],
                        mode="markers+text",
                        marker=dict(size=14, color=f"rgba({255-i*20},{i*30},{200},{0.9})",
                                    line=dict(color="white", width=1.5)),
                        text=str(player_id),
                        textposition="middle center",
                        textfont=dict(size=9, color="white"),
                        name=f"Jugador {player_id}",
                        hovertemplate=f"Jugador {player_id}<br>x: {{x:.1f}}<br>y: {{y:.1f}}<extra></extra>",
                        showlegend=False,
                    ))

                    if show_movement:
                        fig.add_annotation(
                            x=x + velocities[i, 0] * 2,
                            y=y + velocities[i, 1] * 2,
                            ax=x, ay=y,
                            xref="x", yref="y",
                            axref="x", ayref="y",
                            showarrow=True,
                            arrowhead=2, arrowsize=1,
                            arrowcolor="rgba(255,255,255,0.3)",
                            arrowwidth=1,
                        )

                if show_ball:
                    fig.add_trace(go.Scatter(
                        x=[ball_pos[0]], y=[ball_pos[1]],
                        mode="markers",
                        marker=dict(size=10, color="white",
                                    symbol="circle",
                                    line=dict(color="black", width=2)),
                        name="Balón",
                        hovertemplate=f"Balón<br>x: {{x:.1f}}<br>y: {{y:.1f}}<extra></extra>",
                    ))

                fig.update_layout(
                    title=f"Tracking en vivo - Frame {frame + 1}/{n_frames} | Formación: {formation}",
                    width=750, height=480,
                    paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
                    font_color="white",
                    xaxis=dict(range=[0, 105], showgrid=False, zeroline=False,
                              tickvals=[0, 25, 50, 75, 100], title=""),
                    yaxis=dict(range=[0, 68], showgrid=False, zeroline=False,
                              tickvals=[0, 17, 34, 51, 68], title="",
                              scaleanchor="x", scaleratio=1),
                    margin=dict(l=10, r=10, t=40, b=10),
                    hovermode="closest",
                )

                plot_placeholder.plotly_chart(fig, use_container_width=True, key=f"track_{frame}")

                if frame < min(n_frames, 200) - 1:
                    time.sleep(0.1 / speed_factor)

            st.session_state.tracking_active = False
            st.success("✅ Simulación de tracking completada")

with tab2:
    st.markdown("### Pipeline de Computer Vision para tracking")

    st.markdown("""
    ```
    🎥 Video del partido
         │
         ▼
    ┌─────────────┐
    │  Frame      │  OpenCV: captura frame a frame
    │  Extraction │
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │  YOLOv8     │  Ultralytics: detección de jugadores + balón
    │  Detection  │
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │  Tracking   │  ByteTrack / DeepSORT: seguimiento individual
    │  (SORT)     │
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │  Position   │  Mapeo de coordenadas pixel → campo
    │  Mapping    │
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │  Tactical   │  Análisis: formaciones, presión, espacios
    │  Analytics  │
    └──────┬──────┘
           │
           ▼
    📊 Dashboard en tiempo real
    ```
    """)

    st.markdown("### 🔬 Código del pipeline (concepto)")
    code = '''
import cv2
from ultralytics import YOLO

# Cargar modelo YOLOv8 pre-entrenado
model = YOLO("yolov8n.pt")

# Pipeline de tracking
cap = cv2.VideoCapture("worldcup_match.mp4")
tracker = cv2.TrackerCSRT_create()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # 1. Detección de objetos
    results = model(frame, classes=[0])  # clase 0 = persona
    
    # 2. Extraer bounding boxes
    for r in results:
        boxes = r.boxes.xyxy.cpu().numpy()
    
    # 3. Tracking individual
    # 4. Mapeo a coordenadas de campo
    # 5. Calcular métricas tácticas
    
    # Visualización
    annotated_frame = results[0].plot()
    cv2.imshow("World Cup Tracking", annotated_frame)
    
    if cv2.waitKey(1) == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
'''
    st.code(code, language="python", line_numbers=True)

    st.markdown("### 📊 Métricas extraíbles del pipeline")
    metrics_df = pd.DataFrame({
        "Métrica": ["Velocidad instantánea", "Aceleración", "Distancia recorrida",
                    "Mapa de posiciones", "Formación", "Presión", "Espacios"],
        "Descripción": ["m/s por jugador en cada frame",
                        "Cambio de velocidad entre frames",
                        "Suma acumulada de desplazamientos",
                        "Heatmap de ocupación espacial",
                        "Detección de forma táctica",
                        "Distancia a rivales con balón",
                        "Zonas descubiertas en campo rival"],
        "Tecnología": ["YOLO + Optical Flow", "Diferencia temporal",
                       "Integración numérica", "KDE + Plotly",
                       "Clustering posicional", "Distance transform",
                       "Grid analysis"],
    })
    st.dataframe(metrics_df, use_container_width=True)

with tab3:
    st.markdown("### Métricas físicas de los jugadores")

    np.random.seed(42)
    n_players = 22
    player_data = []
    for i in range(n_players):
        total_dist = np.random.uniform(8, 13)
        max_speed = np.random.uniform(25, 35)
        avg_speed = np.random.uniform(5, 9)
        sprints = int(np.random.uniform(5, 25))
        accelerations = int(np.random.uniform(10, 40))
        fatigue_idx = np.random.uniform(10, 40)

        player_data.append({
            "Jugador": f"J{i+1}",
            "Distancia (km)": round(total_dist, 1),
            "Vel. Máx (km/h)": round(max_speed, 1),
            "Vel. Media (km/h)": round(avg_speed, 1),
            "Sprints": sprints,
            "Aceleraciones": accelerations,
            "Fatiga (%)": round(fatigue_idx, 1),
        })
    df_physical = pd.DataFrame(player_data)

    col1, col2 = st.columns(2)

    with col1:
        metric_choice = st.selectbox(
            "Métrica física",
            ["Distancia (km)", "Vel. Máx (km/h)", "Sprints", "Fatiga (%)"],
            key="phys_metric"
        )

        fig = px.bar(
            df_physical.sort_values(metric_choice, ascending=False),
            x="Jugador", y=metric_choice,
            color=metric_choice,
            color_continuous_scale="Viridis",
            title=f"{metric_choice} por jugador",
            text_auto=True,
        )
        fig.update_layout(
            height=350, margin=dict(l=10, r=10, t=40, b=10),
            paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
            font_color="white",
            showlegend=False,
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True, key="phys_bar")

    with col2:
        fig = px.scatter(
            df_physical, x="Distancia (km)", y="Vel. Máx (km/h)",
            size="Sprints", color="Fatiga (%)",
            hover_data=["Jugador", "Aceleraciones"],
            title="Relación distancia, velocidad y fatiga",
            color_continuous_scale="RdYlGn_r",
            size_max=20,
        )
        fig.update_layout(
            height=350, margin=dict(l=10, r=10, t=40, b=10),
            paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
            font_color="white",
        )
        st.plotly_chart(fig, use_container_width=True, key="phys_scatter")

    st.markdown("### 📋 Tabla de rendimiento físico")
    st.dataframe(
        df_physical.style.background_gradient(
            subset=["Distancia (km)", "Vel. Máx (km/h)", "Sprints", "Fatiga (%)"],
            cmap="RdYlGn",
        ),
        use_container_width=True,
    )

    st.markdown("---")
    st.markdown("### 🧠 Zonas de riesgo de lesión")
    df_physical["Riesgo Lesión"] = (
        (df_physical["Fatiga (%)"] / 40 * 0.4) +
        (df_physical["Sprints"] / 30 * 0.3) +
        (df_physical["Distancia (km)"] / 14 * 0.3)
    ) * 100
    df_physical["Riesgo Lesión"] = df_physical["Riesgo Lesión"].clip(0, 100).round(1)

    fig = go.Figure()
    for _, row in df_physical.iterrows():
        color = "#00ff88" if row["Riesgo Lesión"] < 30 else \
                "#ffd93d" if row["Riesgo Lesión"] < 60 else "#ff4444"
        fig.add_trace(go.Bar(
            x=[row["Jugador"]], y=[row["Riesgo Lesión"]],
            marker_color=color,
            name=row["Jugador"],
            showlegend=False,
            text=[f"{row['Riesgo Lesión']:.0f}%"],
            textposition="outside",
        ))

    fig.add_hline(y=30, line_dash="dash", line_color="#ffd93d",
                  annotation_text="Bajo riesgo")
    fig.add_hline(y=60, line_dash="dash", line_color="#ff4444",
                  annotation_text="Alto riesgo")
    fig.update_layout(
        title="Predicción de riesgo de lesión por jugador",
        height=350, margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font_color="white",
    )
    st.plotly_chart(fig, use_container_width=True, key="injury_risk")

import matplotlib.pyplot as plt
import matplotlib
