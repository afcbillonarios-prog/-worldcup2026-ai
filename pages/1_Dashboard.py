import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import numpy as np
from datetime import datetime
from utils.signals import SignalGenerator
from utils.visualizations import create_gauge

st.set_page_config(page_title="Dashboard Live - Mundial 2026", page_icon="📊", layout="wide")

st.markdown("""
<style>
    .signal-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
                   border-radius: 10px; padding: 12px; margin: 4px 0; }
    .signal-label { color: #8892b0; font-size: 0.8rem; }
    .signal-value { font-size: 1.6rem; font-weight: 700; }
    .telegram-sent { background: rgba(0,200,100,0.1); border: 1px solid rgba(0,200,100,0.3);
                     border-radius: 6px; padding: 4px 8px; font-size: 0.75rem; color: #00ff88; }
    .event-badge { display: inline-block; padding: 2px 8px; border-radius: 10px;
                   font-size: 0.7rem; font-weight: 600; }
    .st-emotion-cache-1v7f65g { background: rgba(10,14,23,0.95); }
</style>
""", unsafe_allow_html=True)

st.markdown("# 📊 Dashboard de Señales en Vivo")
st.markdown("### Monitoreo en tiempo real + Telegram Alerts")

if "signal_gen" not in st.session_state:
    st.session_state.signal_gen = SignalGenerator()
    st.session_state.signal_history = []
    st.session_state.events_log = []
    st.session_state.running = False
    st.session_state.telegram_sent_count = 0
    st.session_state.last_auto_send_minute = -5

gen = st.session_state.signal_gen
history = st.session_state.signal_history

team_a = st.session_state.get("team_a", "Argentina")
team_b = st.session_state.get("team_b", "Francia")

control_cols = st.columns([1, 1, 1, 2, 1])
with control_cols[0]:
    if st.button("▶️ Iniciar", use_container_width=True, type="primary"):
        st.session_state.running = True
with control_cols[1]:
    if st.button("⏸️ Pausar", use_container_width=True):
        st.session_state.running = False
with control_cols[2]:
    if st.button("⏹️ Reset", use_container_width=True):
        gen.reset()
        st.session_state.signal_history = []
        st.session_state.events_log = []
        st.session_state.running = False
        st.session_state.telegram_sent_count = 0
        st.session_state.last_auto_send_minute = -5
        st.rerun()
with control_cols[3]:
    st.markdown(f"### ⏱️ Minuto {gen.time}  |  ⚔️ {team_a} vs {team_b}")
with control_cols[4]:
    if st.session_state.telegram_connected:
        st.markdown(f"<span class='telegram-sent'>📤 {st.session_state.telegram_sent_count} enviadas</span>",
                    unsafe_allow_html=True)
    else:
        st.markdown("<span style='color:#ff6b6b;font-size:0.8rem;'>🔴 Telegram no conectado</span>",
                    unsafe_allow_html=True)

st.markdown("---")

state = gen.get_state()

gauge_cols = st.columns(5)
signal_config = [
    ("xG Dinámico", state.get("xG_dynamics", 0), "#00d4ff", 0.8, 0.5),
    ("Posesión %", state.get("possession", 50), "#7b2ff7", 100, 55),
    ("Presión Alta", state.get("pressing_intensity", 65), "#ff6b6b", 100, 60),
    ("Momentum", state.get("momentum", 50), "#ffd93d", 100, 55),
    ("Fatiga", state.get("fatigue", 30), "#ff8c00", 100, 40),
]

for i, (label, val, color, mx, threshold) in enumerate(signal_config):
    with gauge_cols[i]:
        fig = create_gauge(val, label, mx)
        fig.update_traces(gauge=dict(
            bar=dict(color=color),
            axis=dict(range=[0, mx], tickcolor="white", dtick=mx/5),
        ))
        st.plotly_chart(fig, use_container_width=True, key=f"gauge_{i}")

st.markdown("---")

detail_cols = st.columns(4)
detail_signals = [
    ("Línea Defensiva", state.get("defensive_line", 35), "m", 100),
    ("Peligro Ofensivo", state.get("attack_danger", 40), "oranges", 100),
    ("Control Juego", state.get("control_index", 50), "teal", 100),
    ("xG Esperado", state.get("expected_goals", 1.2), "purples", 5),
]
for i, (label, val, cm, mx) in enumerate(detail_signals):
    with detail_cols[i]:
        fig = create_gauge(val, label, mx)
        st.plotly_chart(fig, use_container_width=True, key=f"detail_{i}")

if st.session_state.running:
    for _ in range(3):
        events = gen.tick()
        new_state = gen.get_state()
        history.append(new_state)
        st.session_state.events_log.extend(events)

        for ev in events:
            if st.session_state.telegram_connected and st.session_state.telegram_chat_id:
                from utils.telegram_bot import send_event_alert, send_signal_alert
                if ev["type"] == "goal":
                    resp = send_event_alert(
                        st.session_state.telegram_chat_id, "goal",
                        f"⚽ ¡GOL! Minuto {ev['minute']} — {team_a if np.random.random() > 0.5 else team_b}",
                        team_a, team_b
                    )
                    if resp.get("ok"):
                        st.session_state.telegram_sent_count += 1
                        st.session_state.telegram_signal_log.append(
                            f"⚽ Gol {ev['minute']}' — {datetime.now().strftime('%H:%M:%S')}"
                        )

    if st.session_state.telegram_connected and st.session_state.telegram_auto_send:
        if gen.time - st.session_state.last_auto_send_minute >= 5:
            from utils.telegram_bot import send_signal_alert
            resp = send_signal_alert(
                st.session_state.telegram_chat_id, gen.get_state(),
                gen.time, team_a, team_b
            )
            if resp.get("ok"):
                st.session_state.telegram_sent_count += 1
                st.session_state.last_auto_send_minute = gen.time
                st.session_state.telegram_signal_log.append(
                    f"📊 Señales min {gen.time}' — {datetime.now().strftime('%H:%M:%S')}"
                )

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📈 Evolución de Señales")

    if history:
        df_hist = pd.DataFrame(history)

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            subplot_titles=("Momentum & Control", "xG & Peligro Ofensivo"))

        if "minute" in df_hist.columns and "momentum" in df_hist.columns:
            fig.add_trace(
                go.Scatter(x=df_hist["minute"], y=df_hist["momentum"],
                          mode="lines", name="Momentum",
                          line=dict(color="#ffd93d", width=2)),
                row=1, col=1
            )
        if "control_index" in df_hist.columns:
            fig.add_trace(
                go.Scatter(x=df_hist["minute"], y=df_hist["control_index"],
                          mode="lines", name="Control",
                          line=dict(color="#00d4ff", width=2)),
                row=1, col=1
            )
        if "possession" in df_hist.columns:
            fig.add_trace(
                go.Scatter(x=df_hist["minute"], y=df_hist["possession"],
                          mode="lines", name="Posesión",
                          line=dict(color="#7b2ff7", width=2, dash="dot")),
                row=1, col=1
            )
        if "attack_danger" in df_hist.columns:
            fig.add_trace(
                go.Scatter(x=df_hist["minute"], y=df_hist["attack_danger"],
                          mode="lines", name="Peligro Ofensivo",
                          line=dict(color="#ff6b6b", width=2)),
                row=2, col=1
            )
        if "expected_goals" in df_hist.columns:
            fig.add_trace(
                go.Scatter(x=df_hist["minute"], y=df_hist["expected_goals"],
                          mode="lines", name="xG Esperado",
                          line=dict(color="#7b2ff7", width=2),
                          fill="tozeroy"),
                row=2, col=1
            )
        if "xG_dynamics" in df_hist.columns:
            fig.add_trace(
                go.Scatter(x=df_hist["minute"], y=df_hist["xG_dynamics"],
                          mode="lines", name="xG Dinámico",
                          line=dict(color="#00d4ff", width=2, dash="dot")),
                row=2, col=1
            )

        fig.update_layout(height=420, margin=dict(l=10, r=10, t=30, b=10),
                          paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
                          font_color="white",
                          hovermode="x unified",
                          legend=dict(orientation="h", yanchor="bottom", y=1.02,
                                     xanchor="right", x=1, font=dict(size=10)))
        fig.update_xaxes(title_text="Minuto", row=2, col=1)
        fig.update_yaxes(row=1, col=1, range=[0, 100])
        st.plotly_chart(fig, use_container_width=True, key="evolution_chart")

        st.subheader("📊 Señales Actuales")
        display_signals = [
            ("🎯 xG Dinámico", state.get("xG_dynamics", 0), "0.00", 0.5, "#00d4ff"),
            ("⚽ Posesión", state.get("possession", 50), "0%", 100, "#7b2ff7"),
            ("🔥 Presión Alta", state.get("pressing_intensity", 65), "0", 100, "#ff6b6b"),
            ("📈 Momentum", state.get("momentum", 50), "0", 100, "#ffd93d"),
            ("🛡️ Línea Defensiva", state.get("defensive_line", 35), "0m", 100, "#ff8c00"),
            ("😰 Fatiga", state.get("fatigue", 30), "0%", 100, "#ff4444"),
            ("⚡ Peligro Ofensivo", state.get("attack_danger", 40), "0", 100, "#ff6b6b"),
            ("🎮 Control", state.get("control_index", 50), "0", 100, "#00ff88"),
            ("🥅 xG Esperado", state.get("expected_goals", 1.2), "0.00", 5, "#7b2ff7"),
            ("🎯 Precisión Tiro", state.get("shot_accuracy", 45), "0%", 100, "#00d4ff"),
        ]

        sig_cols = st.columns(2)
        for idx, (label, val, suf, mx, color) in enumerate(display_signals):
            with sig_cols[idx % 2]:
                pct = min(val / mx * 100, 100) if mx > 0 else 0
                bar_color = "#00ff88" if pct > 66 else "#ffd93d" if pct > 33 else "#ff4444"
                val_str = f"{val:.2f}" if isinstance(val, float) and val < 10 else f"{val:.1f}"
                st.markdown(
                    f"<div class='signal-card'>"
                    f"<div style='display:flex;justify-content:space-between;'>"
                    f"<span class='signal-label'>{label}</span>"
                    f"<span class='signal-value' style='color:{color};'>{val_str}</span>"
                    f"</div>"
                    f"<div style='background:rgba(255,255,255,0.05);border-radius:4px;height:6px;margin-top:6px;'>"
                    f"<div style='background:{bar_color};width:{pct}%;height:6px;border-radius:4px;"
                    f"transition:width 0.3s ease;'></div></div></div>",
                    unsafe_allow_html=True
                )

with col2:
    st.subheader("⚡ Eventos del Partido")
    events_container = st.container()
    with events_container:
        if st.session_state.events_log:
            recent = st.session_state.events_log[-15:]
            for ev in reversed(recent):
                icon_map = {"goal": "⚽", "shot": "🔫", "card": "🟨", "foul": "🟠", "var": "📺"}
                icon = icon_map.get(ev.get("type", ""), "📌")
                mins = ev.get("minute", ev.get("time", 0))
                desc = ev.get("description", "Evento")
                impact_color = "#ff6b6b" if ev.get("impact") == "high" else "#ffd93d"

                tg_tag = ""
                if ev.get("type") == "goal" and st.session_state.telegram_connected:
                    tg_tag = "<span style='color:#00ff88;font-size:0.65rem;margin-left:4px;'>📤</span>"

                st.markdown(
                    f"<div style='padding:5px 10px;margin:3px 0;border-left:3px solid {impact_color};"
                    f"background:rgba(255,255,255,0.03);border-radius:4px;'>"
                    f"<strong>{icon} {mins}'</strong> "
                    f"<span style='color:#8892b0;font-size:0.85rem;'>{desc}</span>{tg_tag}</div>",
                    unsafe_allow_html=True
                )
        else:
            st.info("⏳ Inicia la simulación para ver eventos...")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📤 Envío a Telegram")

    if st.session_state.telegram_connected and st.session_state.telegram_chat_id:
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📤 Enviar señales ahora", use_container_width=True, type="primary"):
                from utils.telegram_bot import send_signal_alert
                with st.spinner("Enviando..."):
                    resp = send_signal_alert(
                        st.session_state.telegram_chat_id,
                        gen.get_state(), gen.time, team_a, team_b
                    )
                    if resp.get("ok"):
                        st.success("✅ Enviado!")
                        st.session_state.telegram_sent_count += 1
                        st.session_state.telegram_signal_log.append(
                            f"📊 Manual min {gen.time}' — {datetime.now().strftime('%H:%M:%S')}"
                        )
                    else:
                        st.error(f"❌ Error")
        with col_b:
            auto_val = st.checkbox("Auto-cada 5 min", key="tg_auto",
                                   value=st.session_state.telegram_auto_send)
            st.session_state.telegram_auto_send = auto_val
    else:
        st.warning("⚠️ Conectá Telegram en la barra lateral")
        if st.button("🔌 Ir a configuración Telegram"):
            st.switch_page("app.py")

    if st.session_state.telegram_signal_log:
        with st.expander("📋 Historial de envíos", expanded=False):
            for entry in st.session_state.telegram_signal_log[-10:]:
                st.caption(entry)

st.markdown("---")
telegram_connected = st.session_state.get("telegram_connected", False)
tg_status = "✅ Conectado" if telegram_connected else "❌ Desconectado"
tg_auto = " · Auto-envío activo" if st.session_state.get("telegram_auto_send") else ""
st.caption(f"🔄 Señales en tiempo real | Telegram: {tg_status}{tg_auto} | "
           f"{st.session_state.telegram_sent_count} señales enviadas")
