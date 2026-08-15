"""
Landing page — Clasificador de Retinopatía Diabética.
"""

import streamlit as st

from model_utils import (
    CLASS_COLORS,
    CLASS_DESCRIPTIONS,
    CLASS_NAMES,
    DISCLAIMER,
    load_model,
)

# ============================================================
# HERO BANNER
# ============================================================
st.markdown(
    """
    <div class="hero-banner">
        <h1>Clasificador de Retinopatía Diabética</h1>
        <p>
        Un modelo de deep learning basado en EfficientNet-B3 que analiza imágenes de fondo de ojo
        y estima el nivel de severidad de la retinopatía diabética en una escala de 5 niveles,
        proporcionando mapas de explicabilidad visual mediante Grad-CAM.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Botones de Acción del Hero
col_btn1, col_btn2, _ = st.columns([2.5, 2.5, 3])
with col_btn1:
    if st.button("Probar Clasificador", type="primary", key="hero_btn_class"):
        st.switch_page("pages/Clasificador.py")
with col_btn2:
    if st.button("Acerca del Proyecto", type="secondary", key="hero_btn_about"):
        st.switch_page("pages/Acerca.py")

st.markdown("<br>", unsafe_allow_html=True)

# Descargo de Responsabilidad Estilizado
st.markdown(f'<div class="custom-disclaimer">{DISCLAIMER}</div>', unsafe_allow_html=True)

# ============================================================
# DESEMPEÑO DEL MODELO (MÉTRICAS)
# ============================================================
try:
    _, _, metadata = load_model()
    test_metrics = metadata.get("test_metrics", {})
except Exception:
    test_metrics = {}

st.subheader("Desempeño del modelo (conjunto de test)")

col1, col2, col3, col4 = st.columns(4)
metric_defs = [
    (col1, "QWK", test_metrics.get("qwk"), "Quadratic Weighted Kappa (métrica principal)"),
    (col2, "F1 macro", test_metrics.get("f1_macro"), "Promedio no ponderado entre las 5 clases"),
    (col3, "Balanced Acc.", test_metrics.get("balanced_acc"), "Exactitud ajustada por desbalance de clases"),
    (col4, "AUC-ROC", test_metrics.get("auc_roc_macro"), "Área bajo la curva ROC (macro promedio)"),
]

for col, label, value, help_text in metric_defs:
    with col:
        display_value = f"{value:.3f}" if value is not None else "—"
        st.markdown(
            f"""
            <div class="premium-metric-card">
                <div class="metric-value">{display_value}</div>
                <div class="metric-label">{label}</div>
                <div class="metric-desc">{help_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.caption(
    "QWK (Quadratic Weighted Kappa) es la métrica estándar para este problema porque las "
    "clases son ordinales — penaliza más confundir 'sin retinopatía' con 'proliferativa' "
    "que confundir niveles adyacentes."
)

st.divider()

# ============================================================
# ¿CÓMO FUNCIONA?
# ============================================================
st.subheader("¿Cómo funciona el análisis?")

c1, c2, c3, c4 = st.columns(4)
steps = [
    ("1", "Sube una imagen", "Una fotografía digital de fondo de ojo (fondoscopía), en formato JPG o PNG."),
    ("2", "Preprocesamiento", "Se recorta el borde negro, se realza el contraste (CLAHE) y se aplica una máscara circular."),
    ("3", "Clasificación", "EfficientNet-B3 estima la probabilidad de cada uno de los 5 niveles de severidad."),
    ("4", "Explicabilidad", "Grad-CAM genera un mapa de calor sobre las zonas que más influyeron en la predicción."),
]
for col, (num, title, desc) in zip([c1, c2, c3, c4], steps):
    with col:
        st.markdown(
            f"""
            <div class="step-card">
                <div class="step-number">{num}</div>
                <b>{title}</b>
                <p>{desc}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.divider()

# ============================================================
# SECCIÓN EDITORIAL (DOS COLUMNAS ESTILO MAYO CLINIC)
# ============================================================
col_ed1, col_ed2 = st.columns([1.2, 1])
with col_ed1:
    st.markdown('<div class="editorial-title">La recuperación empieza con un diagnóstico preciso</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="editorial-heading">IA al Servicio de la Salud Ocular</div>
        <p class="editorial-text">
        El diagnóstico oportuno de la retinopatía diabética puede prevenir la ceguera en millones de pacientes. 
        Este modelo evalúa de forma automatizada las alteraciones en la retina a partir de una sola toma digital,
        proporcionando una herramienta de soporte clínico inmediata.
        </p>
        
        <div class="editorial-heading">Mapas de Explicabilidad Clínica</div>
        <p class="editorial-text">
        El modelo no solo arroja un veredicto. Gracias al algoritmo Grad-CAM, los médicos pueden ver un mapa de calor
        que resalta las microhemorragias, exudados o vasos anormales que justifican la decisión,
        añadiendo una capa de auditoría clave.
        </p>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Comenzar análisis ahora", type="secondary", key="editorial_cta_home"):
        st.switch_page("pages/Clasificador.py")
with col_ed2:
    st.markdown(
        """
        <div class="editorial-image-container">
            <img src="https://images.unsplash.com/photo-1579684385127-1ef15d508118?auto=format&fit=crop&q=80&w=600" style="width:100%; height:auto;" alt="Oftalmólogo examinando fondo de ojo">
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

# ============================================================
# LOS 5 NIVELES DE SEVERIDAD
# ============================================================
st.subheader("Los 5 niveles de severidad de la retinopatía diabética")

level_cols = st.columns(5)
for col, idx in zip(level_cols, range(5)):
    with col:
        st.markdown(
            f"""
            <div class="severity-card" style="border-left: 5px solid {CLASS_COLORS[idx]};">
                <div class="severity-card-title">{idx} — {CLASS_NAMES[idx]}</div>
                <p class="severity-card-desc">{CLASS_DESCRIPTIONS[idx]}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.divider()
st.caption(
    "Proyecto académico de deep learning aplicado a salud ocular · Dataset: EyePACS "
    "(retinopatía diabética) · Arquitectura: EfficientNet-B3 · Explicabilidad: Grad-CAM"
)
