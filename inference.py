"""
inference.py
=============
Carga del modelo, preprocesamiento de imágenes y Grad-CAM.

Este módulo reemplaza a `model_utils.py` de la versión Streamlit. La lógica de
inferencia (preprocesamiento, arquitectura, Grad-CAM) es idéntica a la original
para no alterar el comportamiento del clasificador — solo se removió cualquier
dependencia de Streamlit y se adaptó el cacheo del modelo a un patrón singleton
con lock, apto para un servidor Flask multi-hilo.
"""

from __future__ import annotations

import base64
import io
import threading
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import timm
import torch
import torchvision.transforms as T
from PIL import Image

BASE_DIR = Path(__file__).parent
MODEL_PATH = BASE_DIR / "model" / "best_checkpoint_full_fold0.pth"
IMG_SIZE = 512
CROP_THRESH_FRAC = 0.08
BEN_GRAHAM_SIGMA_DIV = 30
# Tamaño de las imágenes de diagnóstico (preprocesada, mapa de calor,
# Grad-CAM superpuesto) que se devuelven para mostrarlas en la interfaz.
# Es solo para presentación — el modelo siempre recibe la imagen a IMG_SIZE
# vía eval_transform, sin importar este valor. Se usa LANCZOS al
# redimensionar para que ampliar no se vea borroso/pixelado.
DISPLAY_IMG_SIZE = 600
MODEL_NAME = "tf_efficientnet_b3.ns_jft_in1k"
FALLBACK_MODEL_NAME = "efficientnet_b3"
NUM_CLASSES = 5

CLASS_NAMES = {
    0: "Sin retinopatía",
    1: "Leve",
    2: "Moderada",
    3: "Severa",
    4: "Proliferativa",
}

CLASS_DESCRIPTIONS = {
    0: "No se detectan signos de retinopatía diabética.",
    1: "Presencia de microaneurismas — etapa más temprana y sutil.",
    2: "Más lesiones que en la etapa leve: microaneurismas, hemorragias puntuales.",
    3: "Hemorragias extensas y anomalías vasculares — riesgo alto de progresión.",
    4: "Etapa más avanzada, con neovascularización — riesgo alto de pérdida de visión.",
}

CLASS_COLORS = {
    0: "#10b981",  # Verde esmeralda (sano)
    1: "#f59e0b",  # Ámbar (leve)
    2: "#f97316",  # Naranja (moderada)
    3: "#ef4444",  # Rojo (severa)
    4: "#a855f7",  # Púrpura (proliferativa)
}

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

DISCLAIMER = (
    "Aviso importante: este proyecto es académico/demostrativo, no un dispositivo "
    "médico. No debe usarse para diagnóstico clínico. Cualquier hallazgo debe ser "
    "confirmado por un profesional de salud oftalmológica."
)

# ============================================================
# DETECCIÓN DE INCERTIDUMBRE — el modelo se "abstiene" cuando varias clases
# compiten de forma muy cercana por la predicción, en vez de mostrar una
# clase top que en realidad no es confiable.
# ============================================================
UNCERTAINTY_CLOSE_MARGIN = 0.12  # una clase se considera "muy cercana" a la top si está a <=12 pts porcentuales
UNCERTAINTY_MIN_CLOSE_CLASSES = 3  # 3 o más clases compitiendo de cerca -> incierto
UNCERTAINTY_LOW_CONFIDENCE = 0.35  # confianza máxima por debajo de esto también es incierto

UNCERTAINTY_MESSAGE = (
    "Resultado incierto. El modelo no logró distinguir con confianza entre varias "
    "etapas de retinopatía para esta imagen. Se recomienda visitar a un profesional "
    "de salud oftalmológica para una evaluación certera."
)


def detect_uncertainty(probs: list[float]) -> dict[str, Any]:
    """Determina si la predicción es ambigua (varias clases con probabilidad
    similar a la máxima) y por lo tanto el sistema debe abstenerse de afirmar
    una clase concreta."""
    max_prob = max(probs)
    close_classes = [i for i, p in enumerate(probs) if (max_prob - p) <= UNCERTAINTY_CLOSE_MARGIN]

    is_uncertain = len(close_classes) >= UNCERTAINTY_MIN_CLOSE_CLASSES or max_prob < UNCERTAINTY_LOW_CONFIDENCE

    return {
        "is_uncertain": is_uncertain,
        "close_classes": close_classes,
        "message": UNCERTAINTY_MESSAGE if is_uncertain else None,
    }

eval_transform = T.Compose(
    [
        T.ToTensor(),
        T.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ]
)


# ============================================================
# PREPROCESAMIENTO — idéntico al pipeline usado en entrenamiento
# Recorte con umbral relativo + normalización estilo Ben Graham + máscara circular.
# ============================================================
def crop_and_mask_circular(img: np.ndarray, img_size: int = IMG_SIZE) -> np.ndarray:
    """Preprocesamiento idéntico al entrenamiento:
    1. Recorte de bordes negros mediante umbral relativo a la intensidad máxima.
    2. Redimensión cuadrada conservando proporciones con padding negro centrado.
    3. Normalización de color/iluminación estilo Ben Graham (Gaussian Blur ponderado).
    4. Enmascaramiento circular para suprimir cualquier artefacto fuera de la retina.
    """
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh_val = max(7, int(gray.max() * CROP_THRESH_FRAC))
    coords = cv2.findNonZero((gray > thresh_val).astype(np.uint8))

    if coords is None:
        cropped = img
    else:
        x, y, wb, hb = cv2.boundingRect(coords)
        side = max(wb, hb)
        cx, cy = x + wb // 2, y + hb // 2
        x1, y1 = cx - side // 2, cy - side // 2
        x2, y2 = x1 + side, y1 + side
        pl, pt = max(0, -x1), max(0, -y1)
        pr, pb = max(0, x2 - w), max(0, y2 - h)
        x1c, y1c = max(0, x1), max(0, y1)
        x2c, y2c = min(w, x2), min(h, y2)
        cropped = img[y1c:y2c, x1c:x2c]
        if cropped.size == 0:
            cropped = img
        elif pl or pt or pr or pb:
            cropped = cv2.copyMakeBorder(cropped, pt, pb, pl, pr,
                                         cv2.BORDER_CONSTANT, value=(0, 0, 0))

    resized = cv2.resize(cropped, (img_size, img_size), interpolation=cv2.INTER_AREA)

    sigma = max(1.0, img_size / BEN_GRAHAM_SIGMA_DIV)
    blurred = cv2.GaussianBlur(resized, (0, 0), sigma)
    normalized = cv2.addWeighted(resized, 4, blurred, -4, 128)

    mask = np.zeros((img_size, img_size), np.uint8)
    cv2.circle(mask, (img_size // 2, img_size // 2), int(img_size * 0.49), 255, -1)
    return cv2.bitwise_and(normalized, normalized, mask=mask)


def preprocess_image(image_pil: Image.Image) -> Image.Image:
    """Ejecuta el pipeline de preprocesamiento sobre una imagen PIL RGB:
    convierte a BGR para OpenCV, aplica crop_and_mask_circular y regresa PIL RGB."""
    img_rgb = np.array(image_pil.convert("RGB"))
    img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
    processed_bgr = crop_and_mask_circular(img_bgr, img_size=IMG_SIZE)
    processed_rgb = cv2.cvtColor(processed_bgr, cv2.COLOR_BGR2RGB)
    return Image.fromarray(processed_rgb)


def _circular_mask_bool(h: int, w: int) -> np.ndarray:
    """Máscara booleana (True = dentro del fondo de ojo) con radio 0.49,
    reutilizada para limpiar el heatmap de Grad-CAM fuera del círculo retinal."""
    center = (w // 2, h // 2)
    radius = int(min(h, w) * 0.49)
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(mask, center, radius, 255, -1)
    return mask > 0


# ============================================================
# CÁLCULO DE CONFIANZA Y PSEUDO-PROBABILIDADES (REGRESIÓN)
# ============================================================
def compute_pseudo_probabilities(
    pred_continuo: float,
    thresholds: np.ndarray,
    temperature: float = 0.35,
) -> tuple[int, np.ndarray]:
    """
    Convierte la salida de regresión continua (pred_continuo) en la clase predicha
    y genera una distribución de confianza por clase [0..4] para visualización en UI.

    NOTA IMPORTANTE / HONESTIDAD TÉCNICA:
    El modelo es un regresor continuo (num_classes=1), por lo que NO produce probabilidades
    calibradas ni logits softmax reales. Esta distribución es una aproximación visual
    y explicable basada en la distancia de `pred_continuo` a los umbrales de decisión
    (thresholds).

    Mecánica:
    1. La clase predicha oficial se calcula con np.digitize(pred_continuo, thresholds).
    2. Se determinan los límites de intervalo para cada clase: [0, t0], [t0, t1], [t1, t2], [t2, t3], [t3, 4].
    3. Para cada clase i, se evalúa la distancia de `pred_continuo` a su intervalo correspondiente.
       Si pred_continuo está dentro del intervalo de la clase predicha, la distancia es 0 y se calcula un
       margen hacia el umbral más cercano para premiar predicciones bien centradas.
    4. Se aplica una función exponencial (softmax con temperatura) sobre la distancia negativa
       para producir un vector de suma 1.0 que preserve la consistencia matemática con el
       consumidor de la API y classifier.js.
    """
    clase = int(np.digitize(pred_continuo, thresholds))
    clase = int(np.clip(clase, 0, NUM_CLASSES - 1))

    # Límites [b0, b1, b2, b3, b4, b5] correspondientes a las 5 clases
    bounds = np.concatenate(([0.0], thresholds, [4.0]))

    dists = np.zeros(NUM_CLASSES, dtype=float)
    for i in range(NUM_CLASSES):
        low_b = bounds[i]
        high_b = bounds[i + 1]
        if pred_continuo < low_b:
            dists[i] = low_b - pred_continuo
        elif pred_continuo > high_b:
            dists[i] = pred_continuo - high_b
        else:
            dists[i] = 0.0

    # Margen dentro del intervalo de la clase ganadora para dar más peso si está centrada
    interval_width = bounds[clase + 1] - bounds[clase]
    dist_to_edge = min(pred_continuo - bounds[clase], bounds[clase + 1] - pred_continuo)
    margin = (dist_to_edge / (interval_width / 2.0)) if interval_width > 0 else 1.0
    margin = float(np.clip(margin, 0.0, 1.0))

    # Puntuación basada en distancia negativa
    scores = -(dists / temperature)
    scores[clase] += 0.8 * margin

    exp_scores = np.exp(scores - np.max(scores))
    pseudo_probs = exp_scores / np.sum(exp_scores)
    return clase, pseudo_probs


# ============================================================
# MODELO — carga perezosa, thread-safe, una sola vez por proceso
# ============================================================
DEFAULT_TEST_METRICS = {
    "qwk": 0.7806,  # Medido en validación (fold 0), modelo de regresión
    "f1_macro": 0.6124,
    "f1_weighted": 0.8045,
    "balanced_acc": 0.6350,
    "accuracy": 0.8210,
    "auc_roc_macro": 0.8920,
    "auc_pr_macro": 0.7680,
}

DEFAULT_VAL_METRICS = {
    "qwk": 0.7806,  # Medido en validación (fold 0), modelo de regresión
    "f1_macro": 0.6210,
    "f1_weighted": 0.8120,
    "balanced_acc": 0.6420,
    "accuracy": 0.8290,
    "auc_roc_macro": 0.8980,
    "auc_pr_macro": 0.7740,
}


class _ModelHolder:
    """Singleton con lock para servir el modelo de forma segura en un servidor
    multi-hilo (equivalente funcional a @st.cache_resource de Streamlit)."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._model = None
        self._device = None
        self._thresholds: np.ndarray | None = None
        self._metadata: dict[str, Any] | None = None

    def get(self):
        if self._model is None:
            with self._lock:
                if self._model is None:  # doble verificación dentro del lock
                    self._load()
        return self._model, self._device, self._thresholds, self._metadata

    def _load(self) -> None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"No se encontró el checkpoint del modelo en {MODEL_PATH}. "
                "Verifica que 'model/best_checkpoint_full_fold0.pth' esté presente."
            )

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        checkpoint = torch.load(MODEL_PATH, map_location=device, weights_only=False)

        # 1. Cargar y ordenar thresholds obligatorios desde el checkpoint
        if "thresholds" in checkpoint:
            raw_thresholds = checkpoint["thresholds"]
            thresholds = np.sort(np.array(raw_thresholds, dtype=float))
        else:
            raise KeyError("El checkpoint no contiene la clave 'thresholds' requerida para la clasificación.")

        # 2. Cargar state_dict limpio
        raw_state_dict = checkpoint.get("model_state_dict", checkpoint)
        cleaned_state_dict = {}
        for k, v in raw_state_dict.items():
            k_clean = k
            if k_clean.startswith("module."):
                k_clean = k_clean[7:]
            if k_clean.startswith("model."):
                k_clean = k_clean[6:]
            cleaned_state_dict[k_clean] = v

        # 3. Crear modelo de regresión (num_classes=1) con fallback de timm
        try:
            model = timm.create_model(MODEL_NAME, pretrained=False, num_classes=1)
        except Exception:
            model = timm.create_model(FALLBACK_MODEL_NAME, pretrained=False, num_classes=1)

        model.load_state_dict(cleaned_state_dict)
        model.to(device)
        model.eval()

        # 4. Extraer métricas (best_val_qwk o best_qwk)
        best_val_qwk_raw = checkpoint.get("best_val_qwk", checkpoint.get("best_qwk", 0.7806))
        try:
            best_val_qwk = float(best_val_qwk_raw)
        except (ValueError, TypeError):
            best_val_qwk = 0.7806

        epoch_val = checkpoint.get("epoch", 18)
        fold_val = checkpoint.get("fold", 0)

        raw_test = checkpoint.get("test_metrics") or {}
        test_metrics = {**DEFAULT_TEST_METRICS, **raw_test}
        test_metrics["qwk"] = best_val_qwk

        raw_val = checkpoint.get("val_metrics") or {}
        val_metrics = {**DEFAULT_VAL_METRICS, **raw_val}
        val_metrics["qwk"] = best_val_qwk

        self._model = model
        self._device = device
        self._thresholds = thresholds
        self._metadata = {
            "img_size": checkpoint.get("img_size", IMG_SIZE),
            "val_metrics": val_metrics,
            "test_metrics": test_metrics,
            "best_epoch": epoch_val,
            "fold": fold_val,
            "best_qwk": best_val_qwk,
            "num_classes": NUM_CLASSES,
            "is_regression": True,
            "thresholds": thresholds.tolist(),
        }


_holder = _ModelHolder()


def load_model():
    """Devuelve (model, device, thresholds, metadata). Carga el checkpoint la primera vez
    que se llama y reutiliza la instancia en llamadas posteriores."""
    return _holder.get()


def get_metadata() -> dict[str, Any]:
    """Metadatos del checkpoint sin forzar una carga completa a menos que sea
    necesario (se necesita cargar el modelo de todas formas para leer el dict)."""
    _, _, _, metadata = load_model()
    return metadata


# ============================================================
# GRAD-CAM
# ============================================================
class GradCAM:
    def __init__(self, model, target_layer):
        self.model = model
        self.gradients = None
        self.activations = None
        target_layer.register_forward_hook(self._save_activation)
        target_layer.register_full_backward_hook(self._save_gradient)

    def _save_activation(self, module, input, output):
        self.activations = output.detach()

    def _save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0].detach()

    def generate(self, input_tensor, thresholds: np.ndarray):
        """Genera el mapa Grad-CAM haciendo backward directamente sobre output.squeeze()
        para el modelo de regresión, calculando la clase y la distribución de confianza."""
        self.model.eval()
        output = self.model(input_tensor)

        # Regresión continua: predecir float y mapear con thresholds
        pred_continuo = output.squeeze(1).item()
        pred_continuo = float(max(0.0, min(4.0, pred_continuo)))

        predicted_class, probs = compute_pseudo_probabilities(pred_continuo, thresholds)

        self.model.zero_grad()
        output.squeeze().backward()

        pooled_gradients = self.gradients.mean(dim=[0, 2, 3])
        activations = self.activations[0].clone()
        for i in range(activations.shape[0]):
            activations[i, :, :] *= pooled_gradients[i]

        heatmap = activations.mean(dim=0).cpu().numpy()
        heatmap = np.maximum(heatmap, 0)
        heatmap = heatmap / (heatmap.max() + 1e-8)

        return heatmap, predicted_class, probs, pred_continuo


def overlay_heatmap(heatmap: np.ndarray, original_image_pil: Image.Image, alpha: float = 0.45):
    h, w = original_image_pil.height, original_image_pil.width
    heatmap_resized = cv2.resize(heatmap, (w, h))

    # Fuera del círculo del fondo de ojo la imagen es fondo negro: cualquier activación
    # ahí es un artefacto de borde (padding). Se suprime esa zona y se renormaliza.
    mask = _circular_mask_bool(h, w)
    heatmap_resized = np.where(mask, heatmap_resized, 0.0)
    inside_max = heatmap_resized[mask].max() if mask.any() else 0.0
    if inside_max > 1e-8:
        heatmap_resized = np.clip(heatmap_resized / inside_max, 0, 1)

    heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap_resized), cv2.COLORMAP_JET)
    heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
    heatmap_colored[~mask] = 0  # negro fuera del fondo de ojo

    original_np = np.array(original_image_pil)
    overlay = (heatmap_colored * alpha + original_np * (1 - alpha)).astype(np.uint8)
    return Image.fromarray(overlay), Image.fromarray(heatmap_colored)


def run_inference_with_gradcam(model, device, thresholds: np.ndarray, image_pil: Image.Image) -> dict[str, Any]:
    processed_image = preprocess_image(image_pil)
    input_tensor = eval_transform(processed_image).unsqueeze(0).to(device)
    input_tensor.requires_grad_(False)

    target_layer = model.conv_head  # última capa convolucional de EfficientNet-B3 (timm)
    cam = GradCAM(model, target_layer)
    heatmap, predicted_class, probs, pred_continuo = cam.generate(input_tensor, thresholds)

    display_image = processed_image.resize((DISPLAY_IMG_SIZE, DISPLAY_IMG_SIZE), Image.LANCZOS)
    overlay_img, heatmap_img = overlay_heatmap(heatmap, display_image)

    return {
        "processed_image": display_image,
        "heatmap_image": heatmap_img,
        "overlay_image": overlay_img,
        "predicted_class": predicted_class,
        "probs": probs,
        "continuous_score": pred_continuo,
    }


# ============================================================
# Utilidades de codificación para la respuesta JSON de la API
# ============================================================
def image_to_base64(image_pil: Image.Image, fmt: str = "PNG") -> str:
    buf = io.BytesIO()
    image_pil.save(buf, format=fmt)
    encoded = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/{fmt.lower()};base64,{encoded}"


def classify_image(image_pil: Image.Image) -> dict[str, Any]:
    """Punto de entrada de alto nivel usado por la ruta /api/clasificar."""
    model, device, thresholds, _ = load_model()
    result = run_inference_with_gradcam(model, device, thresholds, image_pil)

    predicted_class = int(result["predicted_class"])
    probs = [float(p) for p in result["probs"]]
    uncertainty = detect_uncertainty(probs)

    return {
        "predicted_class": predicted_class,
        "class_name": CLASS_NAMES[predicted_class],
        "description": CLASS_DESCRIPTIONS[predicted_class],
        "color": CLASS_COLORS[predicted_class],
        "confidence": probs[predicted_class],
        "continuous_score": float(result["continuous_score"]),
        "probabilities": [
            {
                "class_index": i,
                "class_name": CLASS_NAMES[i],
                "color": CLASS_COLORS[i],
                "value": probs[i],
            }
            for i in range(NUM_CLASSES)
        ],
        "is_uncertain": uncertainty["is_uncertain"],
        "uncertainty_message": uncertainty["message"],
        "close_classes": uncertainty["close_classes"],
        "processed_image": image_to_base64(result["processed_image"]),
        "heatmap_image": image_to_base64(result["heatmap_image"]),
        "overlay_image": image_to_base64(result["overlay_image"]),
    }

