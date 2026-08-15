# Clasificador de Retinopatía Diabética — App Streamlit (multipágina)

App completa con landing page, clasificador con Grad-CAM, dashboard de métricas y
página de metodología.

## Estructura

```
streamlit_app_v2/
├── Home.py                        # Landing page (punto de entrada)
├── model_utils.py                 # Módulo compartido: modelo, preprocesamiento, Grad-CAM
├── requirements.txt
├── .streamlit/
│   └── config.toml                # Tema visual
├── model/
│   └── best_model_v2.pth          # Checkpoint entrenado (~40 MB)
└── pages/
    ├── 1_🔬_Clasificador.py       # Sube imagen → predicción + Grad-CAM
    ├── 2_📊_Métricas.py           # Dashboard de métricas (test/validación)
    └── 3_ℹ️_Acerca.py             # Metodología, dataset, limitaciones
```

Streamlit detecta automáticamente la carpeta `pages/` y genera la navegación lateral
con esos archivos, en el orden dado por el prefijo numérico.

## Probar localmente

```bash
cd streamlit_app_v2
pip install -r requirements.txt
streamlit run Home.py
```

Abre `http://localhost:8501`. La navegación entre páginas aparece en el sidebar.

## Desplegar en Streamlit Community Cloud

### 1. Sube el proyecto a GitHub

```bash
cd streamlit_app_v2
git init
git add .
git commit -m "Diabetic retinopathy classifier — multipage app"
git remote add origin https://github.com/<tu-usuario>/<nombre-repo>.git
git branch -M main
git push -u origin main
```

`best_model_v2.pth` pesa ~40 MB, dentro del límite de GitHub (100 MB) — no necesitas Git LFS.

### 2. Conecta el repo a Streamlit Cloud

1. Ve a [share.streamlit.io](https://share.streamlit.io) e inicia sesión con GitHub.
2. **"New app"** → selecciona el repo y la rama `main`.
3. **Archivo principal:** `Home.py` (no `app.py` — cambió el punto de entrada en esta versión).
4. **Deploy.**

### 3. Si falla por memoria

Si ves errores de memoria en el tier gratuito (~1 GB RAM), fija una versión CPU-only de
PyTorch al inicio de `requirements.txt`:

```
--extra-index-url https://download.pytorch.org/whl/cpu
torch>=2.2
```

## Qué cambió respecto a la versión anterior (app.py único)

- **Landing page** (`Home.py`) con hero, métricas destacadas, explicación del pipeline
  en 4 pasos, y tarjetas para los 5 niveles de severidad.
- **Navegación multipágina** — Clasificador, Métricas y Acerca del proyecto separados.
- **`model_utils.py`** centraliza el modelo/preprocesamiento/Grad-CAM para que todas
  las páginas usen exactamente la misma lógica (nada duplicado).
- **Tema visual** vía `.streamlit/config.toml`.
- **Botón de descarga** de la imagen Grad-CAM resultante en la página del clasificador.

## Notas técnicas

- El preprocesamiento (recorte de borde negro + CLAHE + máscara circular) replica
  exactamente el usado en entrenamiento — no modificarlo sin volver a entrenar.
- Grad-CAM apunta a `model.conv_head`, la última capa convolucional de EfficientNet-B3 en `timm`.
- `@st.cache_resource` en `load_model()` evita recargar el modelo en cada interacción
  o al cambiar de página — se carga una sola vez por sesión.
