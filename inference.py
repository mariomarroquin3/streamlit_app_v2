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
MODEL_PATH = BASE_DIR / "model" / "best_model_v2.pth"
IMG_SIZE = 300
MODEL_NAME = "efficientnet_b3"
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

eval_transform = T.Compose(
    [
        T.Resize((IMG_SIZE, IMG_SIZE)),
        T.ToTensor(),
        T.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ]
)


# ============================================================
# PREPROCESAMIENTO — idéntico al pipeline usado en entrenamiento
# ============================================================
def remove_black_border(img_array: np.ndarray, threshold: int = 10, min_crop_ratio: float = 0.5) -> np.ndarray:
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    mask = gray > threshold
    coords = np.argwhere(mask)
    if coords.size == 0:
        return img_array
    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0)
    cropped = img_array[y0:y1, x0:x1]
    h, w = img_array.shape[:2]
    ch, cw = cropped.shape[:2]
    if ch < h * min_crop_ratio or cw < w * min_crop_ratio:
        return img_array
    return cropped


def apply_clahe(img_array: np.ndarray, clip_limit: float = 2.0, tile_grid_size=(8, 8)) -> np.ndarray:
    lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    l_eq = clahe.apply(l)
    lab_eq = cv2.merge((l_eq, a, b))
    return cv2.cvtColor(lab_eq, cv2.COLOR_LAB2RGB)


def apply_circular_mask(img_array: np.ndarray) -> np.ndarray:
    h, w = img_array.shape[:2]
    center = (w // 2, h // 2)
    radius = min(center[0], center[1])
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(mask, center, radius, 255, -1)
    return cv2.bitwise_and(img_array, img_array, mask=mask)


def preprocess_image(image_pil: Image.Image) -> Image.Image:
    """Recorte de borde negro + CLAHE + máscara circular — mismo pipeline del entrenamiento."""
    img_array = np.array(image_pil.convert("RGB"))
    img_array = remove_black_border(img_array)
    img_array = apply_clahe(img_array)
    img_array = apply_circular_mask(img_array)
    return Image.fromarray(img_array)


# ============================================================
# MODELO — carga perezosa, thread-safe, una sola vez por proceso
# ============================================================
class _ModelHolder:
    """Singleton con lock para servir el modelo de forma segura en un servidor
    multi-hilo (equivalente funcional a @st.cache_resource de Streamlit)."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._model = None
        self._device = None
        self._metadata: dict[str, Any] | None = None

    def get(self):
        if self._model is None:
            with self._lock:
                if self._model is None:  # doble verificación dentro del lock
                    self._load()
        return self._model, self._device, self._metadata

    def _load(self) -> None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"No se encontró el checkpoint del modelo en {MODEL_PATH}. "
                "Verifica que 'model/best_model_v2.pth' esté presente."
            )

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        checkpoint = torch.load(MODEL_PATH, map_location=device, weights_only=False)

        model = timm.create_model(
            checkpoint.get("model_name", MODEL_NAME),
            pretrained=False,
            num_classes=checkpoint.get("num_classes", NUM_CLASSES),
        )
        model.load_state_dict(checkpoint["model_state_dict"])
        model.to(device)
        model.eval()

        self._model = model
        self._device = device
        self._metadata = {
            "img_size": checkpoint.get("img_size", IMG_SIZE),
            "val_metrics": checkpoint.get("val_metrics", {}),
            "test_metrics": checkpoint.get("test_metrics", {}),
            "best_epoch": checkpoint.get("best_epoch"),
        }


_holder = _ModelHolder()


def load_model():
    """Devuelve (model, device, metadata). Carga el checkpoint la primera vez
    que se llama y reutiliza la instancia en llamadas posteriores."""
    return _holder.get()


def get_metadata() -> dict[str, Any]:
    """Metadatos del checkpoint sin forzar una carga completa a menos que sea
    necesario (se necesita cargar el modelo de todas formas para leer el dict)."""
    _, _, metadata = load_model()
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

    def generate(self, input_tensor, target_class=None):
        self.model.eval()
        output = self.model(input_tensor)
        if target_class is None:
            target_class = output.argmax(dim=1).item()

        self.model.zero_grad()
        output[0, target_class].backward()

        pooled_gradients = self.gradients.mean(dim=[0, 2, 3])
        activations = self.activations[0].clone()
        for i in range(activations.shape[0]):
            activations[i, :, :] *= pooled_gradients[i]

        heatmap = activations.mean(dim=0).cpu().numpy()
        heatmap = np.maximum(heatmap, 0)
        heatmap = heatmap / (heatmap.max() + 1e-8)

        probs = torch.softmax(output, dim=1)[0].detach().cpu().numpy()
        return heatmap, target_class, probs


def overlay_heatmap(heatmap: np.ndarray, original_image_pil: Image.Image, alpha: float = 0.45):
    heatmap_resized = cv2.resize(heatmap, (original_image_pil.width, original_image_pil.height))
    heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap_resized), cv2.COLORMAP_JET)
    heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)

    original_np = np.array(original_image_pil)
    overlay = (heatmap_colored * alpha + original_np * (1 - alpha)).astype(np.uint8)
    return Image.fromarray(overlay), Image.fromarray(heatmap_colored)


def run_inference_with_gradcam(model, device, image_pil: Image.Image) -> dict[str, Any]:
    processed_image = preprocess_image(image_pil)
    input_tensor = eval_transform(processed_image).unsqueeze(0).to(device)
    input_tensor.requires_grad_(False)

    target_layer = model.conv_head  # última capa convolucional de EfficientNet-B3 (timm)
    cam = GradCAM(model, target_layer)
    heatmap, predicted_class, probs = cam.generate(input_tensor)

    display_image = processed_image.resize((IMG_SIZE, IMG_SIZE))
    overlay_img, heatmap_img = overlay_heatmap(heatmap, display_image)

    return {
        "processed_image": display_image,
        "heatmap_image": heatmap_img,
        "overlay_image": overlay_img,
        "predicted_class": predicted_class,
        "probs": probs,
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
    model, device, _ = load_model()
    result = run_inference_with_gradcam(model, device, image_pil)

    predicted_class = int(result["predicted_class"])
    probs = [float(p) for p in result["probs"]]

    return {
        "predicted_class": predicted_class,
        "class_name": CLASS_NAMES[predicted_class],
        "description": CLASS_DESCRIPTIONS[predicted_class],
        "color": CLASS_COLORS[predicted_class],
        "confidence": probs[predicted_class],
        "probabilities": [
            {
                "class_index": i,
                "class_name": CLASS_NAMES[i],
                "color": CLASS_COLORS[i],
                "value": probs[i],
            }
            for i in range(NUM_CLASSES)
        ],
        "processed_image": image_to_base64(result["processed_image"]),
        "heatmap_image": image_to_base64(result["heatmap_image"]),
        "overlay_image": image_to_base64(result["overlay_image"]),
    }
