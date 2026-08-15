"""
Página: Clasificador — sube una imagen y obtén predicción + Grad-CAM.
"""

import io

import streamlit as st
from PIL import Image

from model_utils import (
    CLASS_COLORS,
    CLASS_DESCRIPTIONS,
    CLASS_NAMES,
    DISCLAIMER,
    NUM_CLASSES,
    inject_custom_css,
    load_model,
    run_inference_with_gradcam,
)

st.set_page_config(
    page_title="Clasificador — Retinopatía Diabética",
    layout="wide",
)

# Inyectar estilos centralizados
inject_custom_css()

st.title("Clasificador Retinal")
st.caption("Sube una imagen digital de fondo de ojo para su evaluación automatizada por el modelo.")

# Descargo de Responsabilidad Estilizado
st.markdown(f'<div class="custom-disclaimer">{DISCLAIMER}</div>', unsafe_allow_html=True)

# Cargar modelo y metadatos
model, device, metadata = load_model()

with st.sidebar:
    st.header("Sobre el modelo")
    st.markdown(
        f"""
        - **Arquitectura:** EfficientNet-B3
        - **Resolución de entrada:** {metadata['img_size']}x{metadata['img_size']}
        - **Clases:** 5 (0 a 4, severidad ordinal)
        """
    )
    if metadata.get("test_metrics"):
        tm = metadata["test_metrics"]
        st.subheader("Métricas en test")
        st.metric("QWK", f"{tm.get('qwk', 0):.3f}")
        st.metric("F1 macro", f"{tm.get('f1_macro', 0):.3f}")
        st.metric("Balanced Accuracy", f"{tm.get('balanced_acc', 0):.3f}")
        st.metric("AUC-ROC macro", f"{tm.get('auc_roc_macro', 0):.3f}")

    st.divider()
    st.header("Preprocesamiento")
    st.markdown(
        """
        1. Recorte de borde negro
        2. CLAHE (realce local de contraste)
        3. Máscara circular retinal
        4. Redimensión + Normalización ImageNet
        """
    )

uploaded_file = st.file_uploader(
    "Sube una imagen de fondo de ojo (fondoscopía)",
    type=["jpg", "jpeg", "png"],
)

st.caption(
    "¿No tienes una imagen a la mano? Puedes buscar y descargar cualquier fotografía de "
    "fondoscopía retinal de dominio público para probar la herramienta."
)

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    file_id = f"{uploaded_file.name}_{len(file_bytes)}"
    
    if st.session_state.get("last_file_id") != file_id:
        image_pil = Image.open(io.BytesIO(file_bytes)).convert("RGB")
        with st.spinner("Analizando imagen y calculando Grad-CAM..."):
            result = run_inference_with_gradcam(model, device, image_pil)
        
        st.session_state["last_file_id"] = file_id
        st.session_state["last_image"] = image_pil
        st.session_state["last_result"] = result
        
    image_pil = st.session_state["last_image"]
    result = st.session_state["last_result"]

    predicted_class = result["predicted_class"]
    probs = result["probs"]

    st.divider()
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Imagen original")
        st.markdown('<div class="image-preview-container">', unsafe_allow_html=True)
        st.image(image_pil, width='stretch')
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        color = CLASS_COLORS[predicted_class]
        st.markdown(
            f"""
            <div class="result-card">
                <div class="result-header">Análisis Completado</div>
                <div class="result-label" style="background-color: {color};">
                    Clase {predicted_class} — {CLASS_NAMES[predicted_class]}
                </div>
                <p class="result-desc">
                    {CLASS_DESCRIPTIONS[predicted_class]}
                </p>
                <div class="result-confidence">
                    Nivel de confianza: <strong>{probs[predicted_class] * 100:.1f}%</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<br><b>Distribución de probabilidades por clase:</b>", unsafe_allow_html=True)
        for cls_idx in range(NUM_CLASSES):
            st.progress(
                float(probs[cls_idx]),
                text=f"{cls_idx} — {CLASS_NAMES[cls_idx]}: {probs[cls_idx] * 100:.1f}%",
            )

    st.divider()
    st.markdown("<h3>Mapa de Calor y Explicabilidad (Grad-CAM)</h3>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#475569; font-size:0.95rem; margin-bottom:1.5rem;'>"
        "El mapa de calor (Grad-CAM) resalta las regiones de la retina que tuvieron el mayor peso en la decisión "
        "de clasificación del modelo. Un diagnóstico confiable suele correlacionarse con la activación de áreas "
        "con lesiones, hemorragias o la vecindad del disco óptico."
        "</p>",
        unsafe_allow_html=True,
    )

    col3, col4, col5 = st.columns(3)
    with col3:
        st.markdown('<div class="image-preview-container">', unsafe_allow_html=True)
        st.image(result["processed_image"], caption="1. Imagen preprocesada", width='stretch')
        st.markdown('</div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="image-preview-container">', unsafe_allow_html=True)
        st.image(result["heatmap_image"], caption="2. Mapa de activación (Capa final)", width='stretch')
        st.markdown('</div>', unsafe_allow_html=True)
    with col5:
        st.markdown('<div class="image-preview-container">', unsafe_allow_html=True)
        st.image(result["overlay_image"], caption="3. Grad-CAM superpuesto", width='stretch')
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("Descargar resultados"):
        buf = io.BytesIO()
        result["overlay_image"].save(buf, format="PNG")
        st.download_button(
            "Descargar imagen Grad-CAM",
            data=buf.getvalue(),
            file_name="gradcam_resultado.png",
            mime="image/png",
        )

else:
    st.info("Sube una imagen de fondo de ojo para comenzar el análisis.")
