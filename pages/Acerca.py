"""
Página: Acerca del proyecto — metodología y pipeline.
"""

import streamlit as st

st.set_page_config(page_title="Acerca — Retinopatía Diabética", page_icon="ℹ️", layout="wide")

st.title("ℹ️ Acerca del proyecto")

st.subheader("Objetivo")
st.markdown(
    """
    Construir un pipeline de deep learning capaz de recibir una imagen de fondo de ojo
    y clasificarla en uno de 5 niveles de severidad de retinopatía diabética, con
    explicabilidad visual (Grad-CAM) para inspeccionar en qué se basa el modelo al decidir.
    """
)

st.subheader("Dataset")
st.markdown(
    """
    - **Fuente:** [EyePACS — Diabetic Retinopathy (Kaggle)](https://www.kaggle.com/c/diabetic-retinopathy-detection)
    - **Tamaño:** ~35,000 imágenes de fondo de ojo, etiquetadas en 5 niveles (0 a 4)
    - **Distribución:** fuertemente desbalanceada — la clase 0 (sin retinopatía) representa
      la mayoría de las imágenes, mientras que las clases severas (3 y 4) son minoritarias
    """
)

st.subheader("Pipeline de preprocesamiento")
st.markdown(
    """
    Cada imagen pasa por los siguientes pasos antes de llegar al modelo:

    1. **Recorte de borde negro** — elimina el margen negro alrededor del círculo de la retina.
    2. **CLAHE** (Contrast Limited Adaptive Histogram Equalization) — realza el contraste
       local, haciendo más visibles lesiones de bajo contraste como microaneurismas.
    3. **Máscara circular** — descarta cualquier artefacto fuera del círculo de la retina.
    4. **Resize a 300×300** y normalización con las estadísticas de ImageNet.

    Durante entrenamiento se agregan además aumentos de datos (flips horizontal/vertical,
    rotación, jitter de color, random erasing) para mejorar la generalización.
    """
)

st.subheader("Modelo")
st.markdown(
    """
    - **Arquitectura:** EfficientNet-B3 (preentrenada en ImageNet, vía la librería `timm`)
    - **Función de pérdida:** Focal Loss con ponderación por clase — reduce el peso de
      ejemplos ya bien clasificados y fuerza al modelo a prestar más atención a las
      clases minoritarias y a los casos difíciles
    - **Regularización:** dropout, stochastic depth (drop-path) y weight decay
    - **Entrenamiento en etapas:** primero con el backbone congelado (solo el clasificador
      nuevo), luego fine-tuning completo con learning rates diferenciados y un scheduler
      reactivo (`ReduceLROnPlateau`) basado en la métrica de validación
    """
)

st.subheader("Explicabilidad — Grad-CAM")
st.markdown(
    """
    Grad-CAM (Gradient-weighted Class Activation Mapping) genera un mapa de calor sobre
    la imagen, mostrando qué regiones influyeron más en la predicción del modelo. Esto
    permite verificar cualitativamente si el modelo está usando señales clínicamente
    relevantes (vasos sanguíneos, disco óptico, lesiones) en vez de artefactos espurios
    de la imagen — un paso de auditoría que fue clave durante el desarrollo de este
    proyecto para detectar y corregir un sesgo hacia un artefacto de borde en versiones
    anteriores del modelo.
    """
)

st.subheader("Limitaciones conocidas")
st.markdown(
    """
    - El modelo tiene mayor dificultad distinguiendo la clase "leve" (nivel 1) de
      "sin retinopatía" (nivel 0) — la frontera clínicamente más sutil.
    - Entrenado y validado sobre un solo dataset (EyePACS); su desempeño en imágenes de
      otros equipos, poblaciones o condiciones de captura no está garantizado.
    - No sustituye una evaluación oftalmológica profesional.
    """
)

st.divider()
st.caption("Proyecto académico de deep learning aplicado a salud ocular.")
