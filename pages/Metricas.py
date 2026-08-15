"""
Página: Métricas — desempeño detallado del modelo.
"""

import streamlit as st

from model_utils import load_model

st.set_page_config(page_title="Métricas — Retinopatía Diabética", page_icon="📊", layout="wide")

st.title("📊 Métricas del modelo")
st.caption("Desempeño medido sobre el conjunto de test (nunca visto durante entrenamiento).")

_, _, metadata = load_model()
val_metrics = metadata.get("val_metrics", {})
test_metrics = metadata.get("test_metrics", {})

if not test_metrics:
    st.info("No hay métricas guardadas en este checkpoint.")
else:
    tab1, tab2 = st.tabs(["Test", "Validación"])

    def render_metrics(metrics):
        cols = st.columns(3)
        rows = [
            ("QWK (Quadratic Weighted Kappa)", metrics.get("qwk")),
            ("F1 macro", metrics.get("f1_macro")),
            ("F1 weighted", metrics.get("f1_weighted")),
            ("Balanced Accuracy", metrics.get("balanced_acc")),
            ("Accuracy", metrics.get("accuracy")),
            ("AUC-ROC macro", metrics.get("auc_roc_macro")),
            ("AUC-PR macro", metrics.get("auc_pr_macro")),
        ]
        for i, (label, value) in enumerate(rows):
            with cols[i % 3]:
                st.metric(label, f"{value:.4f}" if value is not None else "—")

    with tab1:
        render_metrics(test_metrics)
    with tab2:
        render_metrics(val_metrics)

st.divider()

st.subheader("¿Por qué QWK y no solo accuracy?")
st.markdown(
    """
    Este problema tiene **clases ordinales** (0 = sin retinopatía → 4 = proliferativa),
    no categorías independientes. La accuracy simple trata todos los errores por igual,
    pero confundir "sin retinopatía" con "leve" es un error mucho menos grave que
    confundirla con "proliferativa".

    El **Quadratic Weighted Kappa (QWK)** penaliza los errores según qué tan lejos están
    en la escala ordinal, y es la métrica oficial usada en la competencia EyePACS de Kaggle,
    en la que se basa el dataset de entrenamiento de este modelo.
    """
)

st.subheader("Sobre el desbalance de clases")
st.markdown(
    """
    El dataset original está fuertemente desbalanceado: la clase "sin retinopatía"
    representa cerca del 74% de las imágenes, mientras que las clases más severas
    (3 y 4) juntas representan menos del 5%. Para mitigar esto, el entrenamiento usó:

    - **Focal Loss** con ponderación por clase, en vez de Cross-Entropy simple
    - **Aumentos de datos** (flips, rotación, jitter de color, random erasing)
    - **Regularización** (dropout, drop-path, weight decay) para reducir sobreajuste
      hacia la clase mayoritaria
    """
)

st.caption(
    "Nota: incluso con estas técnicas, la clase 'leve' (nivel 1) sigue siendo la más "
    "difícil de distinguir de 'sin retinopatía' — es la frontera clínicamente más sutil."
)
