## Estructura del proyecto

```
webapp/
├── app.py                 # Servidor Flask: rutas de páginas + API JSON
├── inference.py            # Carga del modelo, preprocesamiento y Grad-CAM
├── requirements.txt
├── model/
│   └── best_model_v2.pth   # Checkpoint entrenado (EfficientNet-B3)
├── templates/               # Páginas Jinja2
│   ├── base.html            # Layout compartido (header, footer, tema oscuro)
│   ├── index.html           # Inicio
│   ├── classifier.html      # Clasificador
│   ├── metrics.html         # Métricas
│   └── about.html           # Acerca del proyecto
└── static/
    ├── css/styles.css       # Sistema de diseño completo
    ├── js/
    │   ├── app.js            # Tema oscuro/claro, menú móvil
    │   └── classifier.js     # Subida de imagen, llamada a la API, resultados
    └── img/favicon.svg
```

## Instalación

Requiere Python 3.10+.

```bash
cd webapp
python -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

> **Nota sobre PyTorch:** si tu equipo tiene GPU con CUDA, instala la variante de `torch` /
> `torchvision` correspondiente desde https://pytorch.org/get-started/locally/ *antes* de correr
> `pip install -r requirements.txt`, o edita esa línea para que apunte al índice de PyTorch con
> soporte CUDA. Sin GPU, la versión CPU funciona sin cambios adicionales (algo más lenta por
> imagen).

## Ejecución en desarrollo

```bash
python app.py
```

Esto levanta el servidor en `http://127.0.0.1:5000`. El modelo se carga de forma perezosa (la
primera petición que lo necesite tarda unos segundos más mientras se carga el checkpoint en
memoria; las siguientes son inmediatas).

## Ejecución en producción

El servidor de desarrollo de Flask (`python app.py`) no está pensado para producción. Usa
`gunicorn` (incluido en `requirements.txt`):

```bash
gunicorn -w 2 -b 0.0.0.0:8000 app:app
```

Usa `-w 1` si la memoria disponible es limitada — cada worker carga su propia copia del modelo en
memoria la primera vez que lo necesita.

## Páginas y rutas

| Ruta                | Página                                             |
|----------------------|-----------------------------------------------------|
| `/`                  | Inicio — presentación del proyecto y métricas clave |
| `/clasificador`      | Subida de imagen y resultado con Grad-CAM            |
| `/metricas`          | Métricas de validación y test (QWK, F1, AUC, etc.)   |
| `/acerca`            | Metodología, dataset, arquitectura y limitaciones    |
| `POST /api/clasificar` | API JSON: recibe una imagen, devuelve la predicción |
| `GET /api/salud`     | Estado del modelo (para monitoreo/healthchecks)      |

## Qué cambió respecto a la versión Streamlit

- **Streamlit eliminado por completo** — ya no hay `st.Page`, `st.navigation` ni widgets nativos de
  Streamlit. Todo el frontend es HTML/CSS/JS propio servido por Flask.
- **Diseño rediseñado desde cero**: paleta clínica (tinta marina + teal de instrumental oftálmico),
  tipografía editorial (Lora + Plus Jakarta Sans + IBM Plex Mono para datos), un gráfico SVG
  animado de "escaneo de retina" en el hero, tarjetas de métricas tipo instrumento, y modo
  oscuro/claro persistente (`localStorage`).
- **Subida de imagen por arrastrar-y-soltar** (drag & drop) en vez del uploader nativo de Streamlit,
  con vista previa, manejo de errores y barras de probabilidad animadas por clase.
- **Arquitectura cliente-servidor real**: la clasificación ocurre vía `fetch` a una API JSON
  (`/api/clasificar`), lo que hace mucho más simple desplegar el frontend y el backend por
  separado si se desea en el futuro.
- **La lógica de IA no cambió**: mismo backbone (EfficientNet-B3), mismo pipeline de
  preprocesamiento (recorte de borde negro → CLAHE → máscara circular → normalización), mismo
  algoritmo de Grad-CAM sobre `conv_head`, mismas métricas guardadas en el checkpoint.

## Aviso

Este proyecto es académico/demostrativo. No constituye un dispositivo médico ni debe usarse para
diagnóstico clínico real.
