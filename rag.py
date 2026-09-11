"""
rag.py
======
Explicación en lenguaje natural del resultado del clasificador, con enfoque
RAG (Retrieval-Augmented Generation):

1. Recuperación: `rag_knowledge.retrieve()` selecciona los fragmentos clínicos
   relevantes para la clase predicha y el estado de incertidumbre.
2. Generación: esos fragmentos se pasan como contexto obligatorio a la API de
   OpenRouter (https://openrouter.ai), que redacta una explicación en español
   dirigida a la persona usuaria, cerrando siempre con la recomendación de
   acudir a un profesional. Por defecto usa "openrouter/free", el router
   gratuito de OpenRouter que selecciona automáticamente entre los modelos
   sin costo disponibles (no requiere elegir un modelo específico ni pagar).

Si no hay `OPENROUTER_API_KEY` configurada, o la llamada a la API falla por
cualquier motivo (sin conexión, key inválida, modelo no disponible, etc.),
se usa un *fallback* determinístico que arma la explicación directamente a
partir de los mismos fragmentos recuperados — la función nunca lanza una
excepción hacia el llamador y la funcionalidad sigue disponible sin key.
"""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from typing import Any

import rag_knowledge

logger = logging.getLogger("retinopathy-app.rag")

OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "openrouter/free")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = (
    "Eres un asistente de explicación clínica dentro de una herramienta académica "
    "de apoyo (no diagnóstica) para retinopatía diabética. Debes redactar en "
    "español, en un tono claro, cálido y sin tecnicismos innecesarios, una "
    "explicación breve (máximo 3 párrafos cortos) del resultado del clasificador "
    "para la persona que subió la imagen.\n\n"
    "Reglas estrictas:\n"
    "- Usa ÚNICAMENTE la información clínica que se te entrega en el contexto. "
    "No inventes hallazgos, estadísticas ni recomendaciones que no estén ahí.\n"
    "- Nunca afirmes un diagnóstico definitivo. El resultado es una predicción de "
    "un modelo de IA, no un diagnóstico médico.\n"
    "- Si el resultado es incierto, exprésalo claramente y no elijas 'la clase más "
    "probable' como si fuera confiable.\n"
    "- Siempre termina recomendando explícitamente acudir a un profesional de "
    "salud oftalmológica, ajustando la urgencia sugerida al contenido del "
    "contexto (control de rutina vs. evaluación pronta vs. urgencia).\n"
    "- No uses encabezados ni listas largas; escribe en prosa natural."
)


def _format_context(chunks: list[dict]) -> str:
    return "\n\n".join(f"### {c['title']}\n{c['text']}" for c in chunks)


def _build_user_message(
    predicted_class: int,
    class_name: str,
    confidence: float,
    probabilities: list[dict],
    is_uncertain: bool,
    chunks: list[dict],
) -> str:
    prob_lines = "\n".join(
        f"- {p['class_name']} (clase {p['class_index']}): {p['value'] * 100:.1f}%"
        for p in probabilities
    )
    return (
        f"Resultado del clasificador:\n"
        f"- Clase predicha: {predicted_class} — {class_name}\n"
        f"- Confianza en la clase predicha: {confidence * 100:.1f}%\n"
        f"- ¿Marcado como incierto por el sistema?: {'Sí' if is_uncertain else 'No'}\n\n"
        f"Distribución completa de probabilidades:\n{prob_lines}\n\n"
        f"Contexto clínico recuperado (única fuente de información permitida):\n"
        f"{_format_context(chunks)}\n\n"
        f"Redacta la explicación para la persona usuaria siguiendo las reglas del sistema."
    )


def _render_fallback(
    predicted_class: int,
    class_name: str,
    confidence: float,
    is_uncertain: bool,
    chunks: list[dict],
) -> str:
    """Explicación determinística (sin LLM) construida a partir de los mismos
    fragmentos recuperados. Se usa cuando no hay API key o la llamada falla."""
    by_id = {c["id"]: c["text"] for c in chunks}

    if is_uncertain:
        parts = [by_id.get("uncertainty", "")]
    else:
        parts = [
            f"El modelo clasificó la imagen como '{class_name}' con una confianza "
            f"de {confidence * 100:.1f}%.",
            by_id.get(f"class_{predicted_class}", ""),
        ]

    if "gradcam" in by_id:
        parts.append(by_id["gradcam"])
    if "urgent_signs" in by_id:
        parts.append(by_id["urgent_signs"])
    if "limitations" in by_id:
        parts.append(by_id["limitations"])

    parts.append(
        "Recomendación: comparte este resultado con un profesional de salud "
        "oftalmológica para una evaluación certera; esta herramienta no "
        "sustituye ese examen."
    )

    return "\n\n".join(p for p in parts if p)


def _try_llm_generation(user_message: str) -> str | None:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        logger.info("OPENROUTER_API_KEY no configurada; usando explicación por plantilla.")
        return None

    payload = json.dumps(
        {
            "model": OPENROUTER_MODEL,
            # "openrouter/free" a veces enruta a un modelo de razonamiento
            # (piensa en un campo "reasoning" antes de responder, gastando
            # tokens de max_tokens en el proceso). Con un presupuesto bajo el
            # modelo puede agotarlo pensando y devolver content=null. Se usa
            # un máximo generoso para dejarle espacio de sobra al contenido
            # final; sigue siendo gratuito.
            "max_tokens": 1600,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        OPENROUTER_URL,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            # OpenRouter recomienda estos dos headers para identificar la app
            # en su dashboard; no son secretos ni afectan la respuesta.
            "HTTP-Referer": "https://github.com/mariomarroquin3/retinovision-ai",
            "X-Title": "RetinoVision AI",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
        content = data["choices"][0]["message"].get("content")
        if not content:
            # content vacío/null: típicamente el modelo (de razonamiento)
            # agotó max_tokens pensando y nunca llegó a responder. Se cae al
            # fallback por plantilla en vez de fallar.
            logger.warning(
                "OpenRouter devolvió contenido vacío (modelo: %s, finish_reason: %s)",
                data.get("model"),
                data.get("choices", [{}])[0].get("finish_reason"),
            )
            return None
        text = content.strip()
        return text or None
    except (urllib.error.URLError, KeyError, IndexError, ValueError, TimeoutError, AttributeError, TypeError):
        logger.exception("Fallo al generar explicación con la API de OpenRouter")
        return None


def generate_explanation(
    predicted_class: int,
    class_name: str,
    confidence: float,
    probabilities: list[dict],
    is_uncertain: bool,
) -> dict[str, Any]:
    """Punto de entrada usado por la ruta /api/explicar. Nunca lanza excepción:
    ante cualquier fallo del LLM, devuelve la explicación por plantilla."""
    chunks = rag_knowledge.retrieve(predicted_class, is_uncertain)

    user_message = _build_user_message(
        predicted_class, class_name, confidence, probabilities, is_uncertain, chunks
    )

    llm_text = _try_llm_generation(user_message)

    if llm_text:
        return {
            "explanation": llm_text,
            "source": "llm",
            "model": OPENROUTER_MODEL,
            "retrieved_sources": [c["id"] for c in chunks],
        }

    return {
        "explanation": _render_fallback(predicted_class, class_name, confidence, is_uncertain, chunks),
        "source": "template",
        "model": None,
        "retrieved_sources": [c["id"] for c in chunks],
    }
