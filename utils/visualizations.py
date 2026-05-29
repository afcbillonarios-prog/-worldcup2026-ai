import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd

def create_pitch_figure():
    fig = go.Figure()
    fig.update_xaxis(range=[0, 105], visible=False)
    fig.update_yaxis(range=[0, 68], visible=False)
    fig.update_layout(
        width=700, height=450,
        plot_bgcolor="#1a472a",
        paper_bgcolor="#1a472a",
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
    )
    return fig

def create_heatmap(x_coords, y_coords, team_name="", color="reds"):
    fig = px.density_heatmap(
        x=x_coords, y=y_coords,
        nbinsx=20, nbinsy=20,
        color_continuous_scale=color,
        title=f"Mapa de calor - {team_name}"
    )
    fig.update_layout(
        xaxis_title="Campo (x)", yaxis_title="Campo (y)",
        width=700, height=450,
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        font_color="white",
    )
    fig.update_yaxes(autorange="reversed")
    return fig

def create_gauge(value, title="", max_val=100, color_scale="RdYlGn"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={"text": title, "font": {"color": "white", "size": 14}},
        number={"font": {"color": "white", "size": 24}},
        gauge={
            "axis": {"range": [0, max_val], "tickcolor": "white"},
            "bar": {"color": "rgba(0,200,100,0.8)"},
            "steps": [
                {"range": [0, max_val * 0.33], "color": "rgba(255,50,50,0.3)"},
                {"range": [max_val * 0.33, max_val * 0.66], "color": "rgba(255,200,50,0.3)"},
                {"range": [max_val * 0.66, max_val], "color": "rgba(50,200,50,0.3)"},
            ],
        }
    ))
    fig.update_layout(
        height=220, margin=dict(l=30, r=30, t=50, b=30),
        paper_bgcolor="#0e1117", font={"color": "white"},
    )
    return fig

def create_player_radar(player_stats, categories, title=""):
    values = [player_stats.get(c, 50) for c in categories]
    values += values[:1]
    angles = list(np.linspace(0, 2 * np.pi, len(categories), endpoint=False))
    angles += angles[:1]

    fig = go.Figure(go.Scatterpolar(
        r=values, theta=categories + categories[:1],
        fill="toself", name=title,
        line_color="#00d4ff", fillcolor="rgba(0,212,255,0.2)"
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(range=[0, 100], showticklabels=False, visible=True),
            bgcolor="rgba(14,17,23,0.8)",
        ),
        showlegend=False,
        paper_bgcolor="#0e1117",
        font_color="white",
        height=350,
        margin=dict(l=40, r=40, t=30, b=30),
    )
    return fig

def create_bar_chart(df, x, y, title="", color="#00d4ff"):
    fig = px.bar(df, x=x, y=y, title=title, color_discrete_sequence=[color])
    fig.update_layout(
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font_color="white", height=350,
        xaxis_title="", yaxis_title="",
    )
    fig.update_traces(marker_line_width=0)
    return fig

def create_match_timeline(events_df):
    fig = go.Figure()
    for _, event in events_df.iterrows():
        color = "#00d4ff" if event["type"] == "goal" else \
                "#ff6b6b" if event["type"] == "card" else "#ffd93d"
        fig.add_trace(go.Scatter(
            x=[event["minute"]], y=[event["team"]],
            mode="markers",
            marker=dict(size=12 if event["type"] == "goal" else 8,
                       color=color, symbol="star" if event["type"] == "goal" else "circle"),
            name=f"{event['minute']}' - {event['description']}",
            hoverinfo="text",
            hovertext=f"{event['minute']}': {event['description']}",
            showlegend=False,
        ))
    fig.update_layout(
        height=200, margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font_color="white",
        xaxis_title="Minuto", yaxis_title="",
        xaxis=dict(range=[0, 105], dtick=15),
    )
    return fig

def create_signal_card(value, label, delta=None, color="#00d4ff"):
    fig = go.Figure(go.Indicator(
        mode="number" + ("+delta" if delta else ""),
        value=value,
        number={"font": {"color": color, "size": 36}, "suffix": ""},
        title={"text": label, "font": {"color": "white", "size": 12}},
        delta={"reference": delta, "increasing": {"color": "#00ff88"},
               "decreasing": {"color": "#ff4444"}} if delta else None,
    ))
    fig.update_layout(
        height=120, margin=dict(l=20, r=20, t=40, b=10),
        paper_bgcolor="rgba(14,17,23,0.6)",
        font={"color": "white"},
    )
    return fig
