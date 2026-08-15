"""
Página: Acerca del proyecto — metodología y pipeline.
"""

import streamlit as st

from model_utils import inject_custom_css

st.title("Acerca del Proyecto")
st.caption("Detalles técnicos, dataset, arquitectura del modelo y limitaciones.")

# ============================================================
# OBJETIVO Y DATASET
# ============================================================
col_obj, col_data = st.columns([1.1, 1])

with col_obj:
    st.markdown('<div class="serif-title" style="font-size: 1.8rem; margin-top: 1.5rem; margin-bottom: 0.8rem;">Objetivo del Proyecto</div>', unsafe_allow_html=True)
    st.markdown(
        """
        El propósito principal de este proyecto es construir un pipeline de deep learning robusto, capaz de recibir 
        una imagen digital de fondo de ojo y clasificarla en uno de los 5 niveles de severidad de la retinopatía diabética.
        
        Además, se incorpora explicabilidad visual mediante el algoritmo **Grad-CAM** con el fin de auditar la toma 
        de decisiones de la red, asegurando que el modelo se enfoque en características retinales anómalas (microhemorragias, 
        exudados duros, neovasos) en lugar de artefactos visuales irrelevantes.
        """
    )

with col_data:
    st.markdown('<div class="serif-title" style="font-size: 1.8rem; margin-top: 1.5rem; margin-bottom: 0.8rem;">Dataset EyePACS</div>', unsafe_allow_html=True)
    st.markdown(
        """
        * **Fuente:** Base de datos pública [EyePACS — Diabetic Retinopathy (Kaggle)](https://www.kaggle.com/c/diabetic-retinopathy-detection).
        * **Tamaño:** Aproximadamente 35,000 imágenes etiquetadas del fondo del ojo.
        * **Desbalance de Clases:** Altamente desbalanceado. La clase 0 (sin retinopatía) representa la mayoría abrumadora del dataset, mientras que los estadios severo y proliferativo (clases 3 y 4) son sumamente escasos, lo cual requirió estrategias avanzadas durante el entrenamiento.
        """
    )

st.divider()

# ============================================================
# PIPELINE DE PREPROCESAMIENTO
# ============================================================
st.markdown('<div class="serif-title" style="font-size: 1.8rem; margin-bottom: 1rem;">Pipeline de Preprocesamiento</div>', unsafe_allow_html=True)
st.markdown(
    "Con el fin de estandarizar las fotografías provenientes de distintos tipos de cámaras y condiciones lumínicas, "
    "cada imagen de entrada es preprocesada a través de las siguientes fases antes de ser analizada por la red neural:"
)

c1, c2, c3, c4 = st.columns(4)
steps = [
    ("1", "Recorte de borde negro", "Elimina los márgenes inactivos de la fotografía para centrarse únicamente en el círculo retinal."),
    ("2", "Realce CLAHE", "Histograma local adaptativo que incrementa el contraste local, resaltando lesiones pequeñas o microaneurismas."),
    ("3", "Máscara circular", "Aplica un filtro que enmascara y remueve cualquier ruido o artefacto fuera del área circular de la retina."),
    ("4", "Normalización", "Redimensiona la imagen a 300x300 píxeles y aplica normalización estadística estándar del dataset ImageNet."),
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
# MODELO Y EXPLICABILIDAD
# ============================================================
col_mod, col_cam = st.columns([1, 1])

with col_mod:
    st.markdown('<div class="serif-title" style="font-size: 1.8rem; margin-bottom: 0.8rem;">Detalles del Modelo</div>', unsafe_allow_html=True)
    st.markdown(
        """
        * **Arquitectura:** Backbone convolucional **EfficientNet-B3**, preentrenado en ImageNet (librería `timm`).
        * **Pérdida (Loss Function):** Focal Loss ponderada por clase. Ayuda a ignorar muestras ya aprendidas con facilidad y obliga al modelo a concentrarse en las clases raras y casos limítrofes.
        * **Regularización:** Uso de Stochastic Depth (drop-path), Dropout y Weight Decay para mitigar sobreajustes hacia la clase mayoritaria.
        * **Entrenamiento:** Realizado en dos fases (congelación inicial del extractor y fine-tuning completo posterior) utilizando tasas de aprendizaje diferenciadas y scheduler `ReduceLROnPlateau`.
        """
    )

with col_cam:
    st.markdown('<div class="serif-title" style="font-size: 1.8rem; margin-bottom: 0.8rem;">Explicabilidad — Grad-CAM</div>', unsafe_allow_html=True)
    st.markdown(
        """
        Grad-CAM (Gradient-weighted Class Activation Mapping) calcula la importancia de cada píxel respecto a la clase predicha, 
        analizando los gradientes que fluyen hacia la última capa convolucional de la red (`conv_head` de la EfficientNet).
        
        Esto genera un mapa de calor intuitivo para el clínico. Si el modelo predice retinopatía proliferativa, el médico puede 
        validar visualmente si la red está reaccionando a neovascularizaciones y hemorragias reales, o a un sesgo indeseado 
        (como reflejos del lente en el borde retinal), garantizando un sistema auditable.
        """
    )

st.divider()

# ============================================================
# LIMITACIONES
# ============================================================
st.markdown('<div class="serif-title" style="font-size: 1.8rem; margin-bottom: 0.8rem;">Limitaciones Conocidas</div>', unsafe_allow_html=True)
st.markdown(
    """
    * **Frontera Normal vs Leve:** La diferencia clínica entre clase 0 y clase 1 (presencia de un único o muy pocos microaneurismas) es en ocasiones extremadamente sutil, siendo el punto donde el clasificador presenta mayor índice de confusión.
    * **Sensibilidad de Dominio:** Entrenado exclusivamente con imágenes de EyePACS. El desempeño en equipos médicos no representados en el dataset de entrenamiento podría verse alterado.
    * **No Diagnóstico:** Esta aplicación tiene exclusivamente fines educativos e investigativos. Las predicciones del clasificador no deben ser tomadas bajo ningún concepto como diagnóstico clínico formal.
    """
)

st.divider()
st.caption("Proyecto académico de deep learning aplicado a salud ocular.")
