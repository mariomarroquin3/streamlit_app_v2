"""
app.py
======
Servidor Flask para el Clasificador de Retinopatía Diabética.

Sustituye a la aplicación Streamlit original. Sirve cuatro páginas (Inicio,
Clasificador, Métricas, Acerca) renderizadas con Jinja2 y expone una API JSON
para ejecutar la inferencia del modelo desde el navegador (fetch + FormData),
manteniendo exactamente la misma lógica de negocio (preprocesamiento, modelo,
Grad-CAM) que la versión anterior.
"""

from __future__ import annotations

import io
import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

# Debe cargarse ANTES de importar rag: ese módulo lee OPENROUTER_MODEL de
# os.environ como constante a nivel de módulo (en el momento del import), así
# que si load_dotenv() se llama después, el valor de .env nunca se ve y
# siempre se usa el default hardcodeado en rag.py.
# override=True: el reloader de Werkzeug (debug=True) reinicia el proceso
# hijo heredando el os.environ del proceso monitor, que ya pudo haber
# cargado una versión vieja de .env en un arranque anterior. Sin
# override=True, load_dotenv() no pisa una variable que ya exista en el
# entorno, así que un cambio en .env nunca se reflejaría tras un reinicio
# del reloader sin matar el proceso por completo.
load_dotenv(override=True)

from flask import Flask, jsonify, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from PIL import Image, UnidentifiedImageError

import inference
import rag

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("retinopathy-app")

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB por imagen subida

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

# Almacén simple (JSON Lines) para reportes de "esta clasificación no parece
# correcta". No es una base de datos de verdad: es material crudo para
# revisión manual y, a futuro, para decidir si conviene reentrenar con casos
# difíciles reales (ver nota de Kaggle en CLAUDE.md). No se guarda la imagen
# (el cliente no la reenvía tras clasificar), solo los metadatos numéricos de
# la predicción y un comentario opcional de la persona usuaria.
FEEDBACK_DIR = Path(__file__).parent / "feedback"
FEEDBACK_LOG = FEEDBACK_DIR / "reportes.jsonl"
MAX_FEEDBACK_COMMENT_LENGTH = 500

# Límite de tasa por IP — protege el cómputo de inferencia/Grad-CAM y las
# llamadas a la API de OpenRouter contra abuso o denegación de servicio
# (OWASP API4:2023 Unrestricted Resource Consumption / LLM04 Model DoS).
# Almacenamiento en memoria: suficiente para un solo proceso de desarrollo o
# demo; con varios workers (gunicorn -w >1) cada uno lleva su propio
# contador, así que el límite real efectivo se multiplica por el número de
# workers — para producción real conviene un backend compartido (Redis).
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["60 per minute"],
    storage_uri="memory://",
)


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _safe_metadata() -> dict:
    """Intenta cargar los metadatos del modelo sin tumbar la página si el
    checkpoint o las dependencias de ML no están disponibles todavía."""
    try:
        return inference.get_metadata()
    except Exception as exc:  # pragma: no cover - defensivo para despliegue
        logger.warning("No se pudieron cargar los metadatos del modelo: %s", exc)
        return {}


# ============================================================
# PÁGINAS
# ============================================================
@app.route("/")
def index():
    metadata = _safe_metadata()
    return render_template(
        "index.html",
        active_page="inicio",
        test_metrics=metadata.get("test_metrics", {}),
        disclaimer=inference.DISCLAIMER,
        class_names=inference.CLASS_NAMES,
        class_descriptions=inference.CLASS_DESCRIPTIONS,
        class_colors=inference.CLASS_COLORS,
    )


@app.route("/clasificador")
def classifier_page():
    metadata = _safe_metadata()
    return render_template(
        "classifier.html",
        active_page="clasificador",
        disclaimer=inference.DISCLAIMER,
        img_size=metadata.get("img_size", inference.IMG_SIZE),
        test_metrics=metadata.get("test_metrics", {}),
        num_classes=inference.NUM_CLASSES,
    )


@app.route("/metricas")
def metrics_page():
    metadata = _safe_metadata()
    return render_template(
        "metrics.html",
        active_page="metricas",
        val_metrics=metadata.get("val_metrics", {}),
        test_metrics=metadata.get("test_metrics", {}),
    )


@app.route("/acerca")
def about_page():
    return render_template("about.html", active_page="acerca")


@app.route("/lugares-de-ayuda")
def help_centers_page():
    return render_template("help_centers.html", active_page="lugares")



# ============================================================
# API
# ============================================================
@app.route("/api/clasificar", methods=["POST"])
@limiter.limit("15 per minute")
def api_classify():
    if "file" not in request.files:
        return jsonify({"error": "No se recibió ningún archivo."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No se seleccionó ningún archivo."}), 400

    if not _allowed_file(file.filename):
        return jsonify({"error": "Formato no soportado. Usa JPG o PNG."}), 400

    try:
        image_bytes = file.read()
        image_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except UnidentifiedImageError:
        return jsonify({"error": "El archivo no es una imagen válida."}), 400

    try:
        result = inference.classify_image(image_pil)
    except FileNotFoundError as exc:
        logger.error("Checkpoint del modelo no encontrado: %s", exc)
        return jsonify({"error": "El modelo no está disponible en el servidor."}), 503
    except Exception:  # pragma: no cover - defensivo
        logger.exception("Fallo durante la inferencia")
        return jsonify({"error": "Ocurrió un error al analizar la imagen."}), 500

    return jsonify(result)


@app.route("/api/explicar", methods=["POST"])
@limiter.limit("10 per minute")
def api_explain():
    """Genera una explicación en lenguaje natural (RAG) del resultado que ya
    devolvió /api/clasificar. Recibe de vuelta los campos numéricos de esa
    respuesta (para no mantener estado de la última clasificación en el
    servidor), pero NUNCA usa texto libre enviado por el cliente dentro del
    prompt del LLM: class_name y las etiquetas de cada probabilidad se
    reconstruyen aquí a partir de inference.CLASS_NAMES usando solo los
    índices numéricos. Esto cierra una vía de prompt injection (OWASP
    LLM01): sin esta validación, alguien podría mandar cualquier texto en
    "class_name" o en el nombre de una probabilidad y ese texto terminaría
    incrustado tal cual en el mensaje que se le manda al modelo de lenguaje."""
    data = request.get_json(silent=True) or {}

    try:
        predicted_class = int(data["predicted_class"])
        confidence = float(data["confidence"])
        raw_probabilities = data["probabilities"]
        is_uncertain = bool(data.get("is_uncertain", False))
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "Faltan datos del resultado de clasificación o tienen un formato inválido."}), 400

    if not (0 <= predicted_class < inference.NUM_CLASSES):
        return jsonify({"error": "Clase predicha fuera de rango."}), 400
    if not (0.0 <= confidence <= 1.0):
        return jsonify({"error": "Confianza fuera de rango."}), 400

    if not isinstance(raw_probabilities, list) or len(raw_probabilities) != inference.NUM_CLASSES:
        return jsonify({"error": "Formato de probabilidades inválido."}), 400

    try:
        seen_indices = set()
        probabilities = []
        for entry in raw_probabilities:
            class_index = int(entry["class_index"])
            value = float(entry["value"])
            if not (0 <= class_index < inference.NUM_CLASSES) or not (0.0 <= value <= 1.0):
                raise ValueError("class_index o value fuera de rango")
            seen_indices.add(class_index)
            probabilities.append(
                {
                    "class_index": class_index,
                    "class_name": inference.CLASS_NAMES[class_index],
                    "value": value,
                }
            )
        if seen_indices != set(range(inference.NUM_CLASSES)):
            raise ValueError("Faltan índices de clase o están repetidos")
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "Formato de probabilidades inválido."}), 400

    class_name = inference.CLASS_NAMES[predicted_class]

    try:
        result = rag.generate_explanation(
            predicted_class=predicted_class,
            class_name=class_name,
            confidence=confidence,
            probabilities=probabilities,
            is_uncertain=is_uncertain,
        )
    except Exception:  # pragma: no cover - defensivo
        logger.exception("Fallo inesperado al generar la explicación")
        return jsonify({"error": "Ocurrió un error al generar la explicación."}), 500

    return jsonify(result)


@app.route("/api/reportar", methods=["POST"])
@limiter.limit("5 per minute")
def api_report_feedback():
    """Registra un reporte de "esta clasificación no parece correcta" para
    revisión manual posterior. No reconstruye ningún prompt ni se conecta al
    LLM — es solo persistencia de datos, con la misma validación estricta de
    índices/rangos que /api/explicar (nunca confía en class_name de texto
    libre del cliente)."""
    data = request.get_json(silent=True) or {}

    try:
        predicted_class = int(data["predicted_class"])
        confidence = float(data["confidence"])
        is_uncertain = bool(data.get("is_uncertain", False))
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "Faltan datos del resultado de clasificación o tienen un formato inválido."}), 400

    if not (0 <= predicted_class < inference.NUM_CLASSES):
        return jsonify({"error": "Clase predicha fuera de rango."}), 400
    if not (0.0 <= confidence <= 1.0):
        return jsonify({"error": "Confianza fuera de rango."}), 400

    comment = data.get("comment", "")
    if not isinstance(comment, str):
        return jsonify({"error": "Formato de comentario inválido."}), 400
    comment = comment.strip()[:MAX_FEEDBACK_COMMENT_LENGTH]

    entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "predicted_class": predicted_class,
        "class_name": inference.CLASS_NAMES[predicted_class],
        "confidence": confidence,
        "is_uncertain": is_uncertain,
        "comment": comment,
    }

    try:
        FEEDBACK_DIR.mkdir(exist_ok=True)
        with FEEDBACK_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        logger.exception("No se pudo guardar el reporte de retroalimentación")
        return jsonify({"error": "No se pudo guardar el reporte."}), 500

    return jsonify({"status": "ok"})


@app.route("/api/salud")
def api_health():
    """Endpoint simple de salud / disponibilidad del modelo."""
    try:
        inference.load_model()
        return jsonify({"status": "ok", "model_loaded": True})
    except Exception as exc:  # pragma: no cover - defensivo
        return jsonify({"status": "degraded", "model_loaded": False, "detail": str(exc)}), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
