"""
Página: Clasificador — sube una imagen y obtén predicción + Grad-CAM.
"""

import io

import streamlit as st
from PIL import Image

from model_utils import (
    CLASS_NAMES,
    CLASS_DESCRIPTIONS,
    DISCLAIMER,
    NUM_CLASSES,
    load_model,
    run_inference_with_gradcam,
)

st.set_page_config(page_title="Clasificador — Retinopatía Diabética", page_icon="🔬", layout="wide")

st.title("🔬 Clasificador")
st.caption("Sube una imagen de fondo de ojo para analizarla con el modelo.")
st.warning(DISCLAIMER)

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
    st.header("Preprocesamiento aplicado")
    st.markdown(
        """
        1. Recorte de borde negro
        2. CLAHE (realce de contraste local)
        3. Máscara circular
        4. Resize + normalización ImageNet
        """
    )

uploaded_file = st.file_uploader(
    "Sube una imagen de fondo de ojo (fondoscopía)",
    type=["jpg", "jpeg", "png"],
)

st.caption("¿No tienes una imagen a la mano? Puedes usar cualquier fotografía de fondoscopía retinal de dominio público para probar la app.")

if uploaded_file is not None:
    image_pil = Image.open(io.BytesIO(uploaded_file.read())).convert("RGB")

    with st.spinner("Analizando imagen..."):
        result = run_inference_with_gradcam(model, device, image_pil)

    predicted_class = result["predicted_class"]
    probs = result["probs"]

    st.divider()
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Imagen original")
        st.image(image_pil, use_container_width=True)

    with col2:
        st.subheader("Resultado")
        st.markdown(f"### Clase {predicted_class} — {CLASS_NAMES[predicted_class]}")
        st.markdown(CLASS_DESCRIPTIONS[predicted_class])
        st.markdown(f"**Confianza:** {probs[predicted_class] * 100:.1f}%")

        st.markdown("**Distribución de probabilidades:**")
        for cls_idx in range(NUM_CLASSES):
            st.progress(
                float(probs[cls_idx]),
                text=f"{cls_idx} — {CLASS_NAMES[cls_idx]}: {probs[cls_idx] * 100:.1f}%",
            )

    st.divider()
    st.subheader("Grad-CAM — ¿en qué se fijó el modelo?")
    st.caption(
        "El mapa de calor muestra las regiones que más influyeron en la predicción. "
        "Idealmente debería concentrarse en el disco óptico, vasos sanguíneos y lesiones "
        "retinales — no en bordes o artefactos de la imagen."
    )

    col3, col4, col5 = st.columns(3)
    with col3:
        st.image(result["processed_image"], caption="Imagen preprocesada", use_container_width=True)
    with col4:
        st.image(result["heatmap_image"], caption="Mapa de activación", use_container_width=True)
    with col5:
        st.image(result["overlay_image"], caption="Grad-CAM superpuesto", use_container_width=True)

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
