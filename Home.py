"""
Landing page — Clasificador de Retinopatía Diabética.
"""

import streamlit as st

from model_utils import DISCLAIMER, load_model

st.set_page_config(
    page_title="Retinopatía Diabética — IA",
    page_icon="👁️",
    layout="wide",
)

# ============================================================
# ESTILOS
# ============================================================
st.markdown(
    """
    <style>
    .hero {
        padding: 2.5rem 2rem;
        border-radius: 16px;
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        color: white;
        margin-bottom: 1.5rem;
    }
    .hero h1 {
        font-size: 2.3rem;
        margin-bottom: 0.3rem;
    }
    .hero p {
        font-size: 1.05rem;
        color: #d8e6ef;
        max-width: 700px;
    }
    .metric-card {
        background: #f7f9fb;
        border: 1px solid #e3e8ee;
        border-radius: 12px;
        padding: 1.1rem;
        text-align: center;
    }
    .metric-card .value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #203a43;
    }
    .metric-card .label {
        font-size: 0.85rem;
        color: #667;
        margin-top: 0.2rem;
    }
    .step-card {
        background: white;
        border: 1px solid #e3e8ee;
        border-radius: 12px;
        padding: 1.2rem;
        height: 100%;
    }
    .step-number {
        display: inline-block;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background: #2c5364;
        color: white;
        text-align: center;
        line-height: 28px;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# HERO
# ============================================================
st.markdown(
    """
    <div class="hero">
        <h1>👁️ Clasificador de Retinopatía Diabética</h1>
        <p>
        Un modelo de deep learning (EfficientNet-B3) que analiza imágenes de fondo de ojo
        y estima el nivel de severidad de la retinopatía diabética en una escala de 5 niveles,
        con explicabilidad visual mediante Grad-CAM.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.warning(DISCLAIMER)

# ============================================================
# MÉTRICAS DESTACADAS
# ============================================================
try:
    _, _, metadata = load_model()
    test_metrics = metadata.get("test_metrics", {})
except Exception:
    test_metrics = {}

st.subheader("Desempeño del modelo (conjunto de test)")

col1, col2, col3, col4 = st.columns(4)
metric_defs = [
    (col1, "QWK", test_metrics.get("qwk"), "Quadratic Weighted Kappa"),
    (col2, "F1 macro", test_metrics.get("f1_macro"), "Promedio no ponderado entre clases"),
    (col3, "Balanced Acc.", test_metrics.get("balanced_acc"), "Exactitud balanceada por clase"),
    (col4, "AUC-ROC", test_metrics.get("auc_roc_macro"), "Área bajo la curva ROC (macro)"),
]

for col, label, value, help_text in metric_defs:
    with col:
        display_value = f"{value:.3f}" if value is not None else "—"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="value">{display_value}</div>
                <div class="label">{label}</div>
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
# CÓMO FUNCIONA
# ============================================================
st.subheader("¿Cómo funciona?")

c1, c2, c3, c4 = st.columns(4)
steps = [
    ("1", "Sube una imagen", "Una fotografía de fondo de ojo (fondoscopía), en formato JPG o PNG."),
    ("2", "Preprocesamiento", "Se recorta el borde negro, se realza el contraste (CLAHE) y se aplica una máscara circular."),
    ("3", "Clasificación", "EfficientNet-B3 estima la probabilidad de cada uno de los 5 niveles de severidad."),
    ("4", "Explicabilidad", "Grad-CAM muestra qué regiones de la retina influyeron más en la predicción."),
]
for col, (num, title, desc) in zip([c1, c2, c3, c4], steps):
    with col:
        st.markdown(
            f"""
            <div class="step-card">
                <div class="step-number">{num}</div>
                <b>{title}</b>
                <p style="font-size:0.88rem; color:#555;">{desc}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.divider()

# ============================================================
# LOS 5 NIVELES
# ============================================================
st.subheader("Los 5 niveles de severidad")

from model_utils import CLASS_NAMES, CLASS_DESCRIPTIONS, CLASS_COLORS

level_cols = st.columns(5)
for col, idx in zip(level_cols, range(5)):
    with col:
        st.markdown(
            f"""
            <div style="border-left: 5px solid {CLASS_COLORS[idx]}; padding: 0.6rem 0.8rem;
                        background: #fafbfc; border-radius: 6px; height: 100%;">
                <b>{idx} — {CLASS_NAMES[idx]}</b>
                <p style="font-size:0.82rem; color:#555; margin-top:0.3rem;">
                    {CLASS_DESCRIPTIONS[idx]}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.divider()

# ============================================================
# CALL TO ACTION
# ============================================================
st.subheader("Prueba el clasificador")
st.markdown(
    "Ve a la página **🔬 Clasificador** en el menú lateral para subir una imagen y "
    "obtener un análisis completo con Grad-CAM."
)

if st.button("🔬 Ir al Clasificador", type="primary"):
    st.switch_page("pages/Clasificador.py")

st.divider()
st.caption(
    "Proyecto académico de deep learning aplicado a salud ocular · Dataset: EyePACS "
    "(retinopatía diabética) · Arquitectura: EfficientNet-B3 · Explicabilidad: Grad-CAM"
)
