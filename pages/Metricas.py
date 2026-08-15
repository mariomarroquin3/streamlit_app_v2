"""
Página: Métricas — desempeño detallado del modelo.
"""

import streamlit as st

from model_utils import load_model

st.title("Métricas del Modelo")
st.caption("Evaluación cuantitativa del clasificador sobre conjuntos de validación y test.")

_, _, metadata = load_model()
val_metrics = metadata.get("val_metrics", {})
test_metrics = metadata.get("test_metrics", {})

if not test_metrics:
    st.info("No hay métricas guardadas en este checkpoint.")
else:
    # Se estiliza automáticamente gracias al CSS del stTabs
    tab1, tab2 = st.tabs(["Test (Evaluación Final)", "Validación (Entrenamiento)"])

    def render_metrics(metrics):
        cols = st.columns(3)
        rows = [
            ("QWK", metrics.get("qwk"), "Quadratic Weighted Kappa (Métrica principal)"),
            ("F1 macro", metrics.get("f1_macro"), "F1 promedio sin ponderar entre clases"),
            ("F1 weighted", metrics.get("f1_weighted"), "F1 promedio ponderado por soporte"),
            ("Balanced Acc.", metrics.get("balanced_acc"), "Exactitud balanceada por clase"),
            ("Accuracy", metrics.get("accuracy"), "Exactitud global simple"),
            ("AUC-ROC macro", metrics.get("auc_roc_macro"), "Área bajo la curva ROC (macro promedio)"),
            ("AUC-PR macro", metrics.get("auc_pr_macro"), "Área bajo curva Precisión-Recall (macro)"),
        ]
        for i, (label, value, desc) in enumerate(rows):
            with cols[i % 3]:
                display_value = f"{value:.4f}" if value is not None else "—"
                st.markdown(
                    f"""
                    <div class="premium-metric-card" style="margin-bottom: 1.2rem;">
                        <div class="metric-value">{display_value}</div>
                        <div class="metric-label">{label}</div>
                        <div class="metric-desc">{desc}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        render_metrics(test_metrics)
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        render_metrics(val_metrics)

st.divider()

# Explicaciones estilizadas con tipografía Serif
st.markdown('<div class="serif-title" style="font-size: 1.8rem; margin-top: 1.5rem; margin-bottom: 0.8rem;">¿Por qué QWK y no solo accuracy?</div>', unsafe_allow_html=True)
st.markdown(
    """
    Este problema posee **clases ordinales** (0 = sin retinopatía → 4 = proliferativa), 
    no categorías independientes. La exactitud (accuracy) simple trata todas las fallas por igual, 
    pero confundir "sin retinopatía" con "leve" es un error mucho menos grave que 
    confundirla con la etapa "proliferativa".

    El **Quadratic Weighted Kappa (QWK)** penaliza las confusiones de manera proporcional al cuadrado de 
    su distancia en la escala ordinal. Es la métrica oficial y estándar de oro en la competencia EyePACS 
    de Kaggle, en la cual se fundamenta el entrenamiento de este clasificador.
    """
)

st.markdown('<div class="serif-title" style="font-size: 1.8rem; margin-top: 2rem; margin-bottom: 0.8rem;">Estrategia frente al desbalance de clases</div>', unsafe_allow_html=True)
st.markdown(
    """
    El conjunto de datos EyePACS presenta un fuerte desbalance de clases: la categoría "sin retinopatía" 
    abarca aproximadamente el 74% de las muestras, mientras que las etapas severa y proliferativa (3 y 4) 
    juntas representan menos del 5%. Para evitar que el modelo se sesgara hacia la clase mayoritaria, se aplicaron:
    
    * **Focal Loss con pesos por clase**: Penaliza con mayor severidad las clasificaciones erróneas en clases minoritarias.
    * **Aumento extremo de datos**: Técnicas de rotación, volteo, jitter de color y random erasing aplicadas dinámicamente durante el entrenamiento.
    * **Regularización estructural**: Uso de dropout, stochastic depth (drop-path) y weight decay en el backbone de EfficientNet-B3.
    """
)

st.caption(
    "Nota: A pesar de estas mitigaciones, la clase 'leve' (nivel 1) continúa representando el desafío "
    "diagnóstico más alto debido a la sutil diferencia física en los microaneurismas tempranos."
)
