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
import logging

from flask import Flask, jsonify, render_template, request
from PIL import Image, UnidentifiedImageError

import inference

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("retinopathy-app")

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB por imagen subida

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}


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


# ============================================================
# API
# ============================================================
@app.route("/api/clasificar", methods=["POST"])
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
