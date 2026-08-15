"""
Módulo compartido: carga del modelo, preprocesamiento y Grad-CAM.
Usado por Home.py y las páginas en pages/.
"""

from pathlib import Path

import cv2
import numpy as np
import streamlit as st
import timm
import torch
import torchvision.transforms as T
from PIL import Image

MODEL_PATH = Path(__file__).parent / "model" / "best_model_v2.pth"
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
    0: "#10b981",  # Emerald Green (Healthy)
    1: "#f59e0b",  # Amber (Mild)
    2: "#f97316",  # Orange (Moderate)
    3: "#ef4444",  # Red (Severe)
    4: "#a855f7",  # Purple (Proliferative)
}

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

DISCLAIMER = (
    "Aviso Importante: Este proyecto es académico/demostrativo, NO un dispositivo médico. "
    "No debe usarse para diagnóstico clínico. Cualquier hallazgo debe ser confirmado por "
    "un profesional de salud oftalmológica."
)


def inject_custom_css():
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False
        
    col_empty, col_toggle = st.columns([8, 2])
    with col_toggle:
        dark_mode = st.toggle("Modo Oscuro", value=st.session_state.dark_mode, key="top_dark_mode_toggle")
        
    # Guardamos el estado; Streamlit ya recarga automáticamente al tocar el toggle
    st.session_state.dark_mode = dark_mode

    css_path = Path(__file__).parent / "style.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
        
    if st.session_state.dark_mode:
        dark_css_path = Path(__file__).parent / "dark_style.css"
        if dark_css_path.exists():
            with open(dark_css_path, "r", encoding="utf-8") as f:
                dark_css_content = f.read()
            st.markdown(f"<style>{dark_css_content}</style>", unsafe_allow_html=True)

# ============================================================
# PREPROCESAMIENTO
# ============================================================
def remove_black_border(img_array, threshold=10, min_crop_ratio=0.5):
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


def apply_clahe(img_array, clip_limit=2.0, tile_grid_size=(8, 8)):
    lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    l_eq = clahe.apply(l)
    lab_eq = cv2.merge((l_eq, a, b))
    return cv2.cvtColor(lab_eq, cv2.COLOR_LAB2RGB)


def apply_circular_mask(img_array):
    h, w = img_array.shape[:2]
    center = (w // 2, h // 2)
    radius = min(center[0], center[1])
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(mask, center, radius, 255, -1)
    return cv2.bitwise_and(img_array, img_array, mask=mask)


def preprocess_image(image_pil):
    """Recorte de borde negro + CLAHE + máscara circular — mismo pipeline del entrenamiento."""
    img_array = np.array(image_pil.convert("RGB"))
    img_array = remove_black_border(img_array)
    img_array = apply_clahe(img_array)
    img_array = apply_circular_mask(img_array)
    return Image.fromarray(img_array)


eval_transform = T.Compose(
    [
        T.Resize((IMG_SIZE, IMG_SIZE)),
        T.ToTensor(),
        T.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ]
)


# ============================================================
# MODELO
# ============================================================
@st.cache_resource(show_spinner="Cargando modelo...")
def load_model():
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

    metadata = {
        "img_size": checkpoint.get("img_size", IMG_SIZE),
        "val_metrics": checkpoint.get("val_metrics", {}),
        "test_metrics": checkpoint.get("test_metrics", {}),
        "best_epoch": checkpoint.get("best_epoch"),
    }
    return model, device, metadata


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


def overlay_heatmap(heatmap, original_image_pil, alpha=0.45):
    heatmap_resized = cv2.resize(heatmap, (original_image_pil.width, original_image_pil.height))
    heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap_resized), cv2.COLORMAP_JET)
    heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)

    original_np = np.array(original_image_pil)
    overlay = (heatmap_colored * alpha + original_np * (1 - alpha)).astype(np.uint8)
    return Image.fromarray(overlay), Image.fromarray(heatmap_colored)


def run_inference_with_gradcam(model, device, image_pil):
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
