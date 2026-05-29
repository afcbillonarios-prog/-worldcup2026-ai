# 🏆 World Cup 2026 AI Analytics Platform

Plataforma profesional de análisis deportivo con Big Data, Machine Learning e Inteligencia Artificial para el Mundial 2026.

## Módulos

| Módulo | Descripción | Tecnología |
|--------|-------------|------------|
| 📊 Dashboard Live | Señales en tiempo real: xG, posesión, presión, momentum, fatiga | Streamlit + Plotly |
| 🤖 Predictor IA | Predicción de resultados con XGBoost (5,000 partidos entrenados) | XGBoost + Scikit-learn |
| 🎯 Sistema xG | Expected Goals con regresión logística (7 variables) | Logistic Regression |
| 🔍 Scouting IA | Clustering K-Means + PCA para detección de talentos | K-Means + PCA |
| 🗺️ Heatmaps Tácticos | Mapas de calor de ocupación, presión y formaciones | Plotly + KDE |
| 🏆 Simulación MC | Monte Carlo con 10,000 simulaciones del torneo | Monte Carlo |
| 👁️ Tracking CV | Pipeline de visión computacional con YOLO | OpenCV + YOLO |

## Stack Tecnológico

- **Python** 3.13+
- **Streamlit** — Interfaz web interactiva
- **XGBoost** — Modelo predictivo de partidos
- **Scikit-learn** — Clustering, regresión logística, PCA
- **Plotly** — Visualizaciones interactivas
- **OpenCV** — Procesamiento de video
- **Pandas / NumPy** — Manipulación de datos

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
cd worldcup2026
streamlit run app.py
```

## Estructura

```
worldcup2026/
├── app.py                 # Entry point
├── pages/                 # Módulos de la plataforma
│   ├── 1_Dashboard.py     # Dashboard en vivo
│   ├── 2_Predictor.py     # Predictor de partidos
│   ├── 3_xG.py            # Sistema Expected Goals
│   ├── 4_Scouting.py      # Scouting IA
│   ├── 5_Heatmaps.py      # Mapas de calor tácticos
│   ├── 6_Simulation.py    # Simulación Monte Carlo
│   └── 7_Tracking.py      # Tracking visión computacional
├── models/                # Modelos ML
├── data/                  # Datos sintéticos
└── utils/                 # Utilidades y visualizaciones
```

## Señales Disponibles

- xG Dynamics — Probabilidad de gol dinámica
- Posesión — Control del balón
- Presión Alta — Intensidad de pressing
- Momentum — Inercia del partido
- Línea Defensiva — Posición de la defensa
- Fatiga — Desgaste físico
- Peligro Ofensivo — Riesgo ofensivo generado
- Control de Juego — Dominio del encuentro
- Expected Goals — Goles esperados acumulados
- Precisión de Tiro — Efectividad ofensiva
