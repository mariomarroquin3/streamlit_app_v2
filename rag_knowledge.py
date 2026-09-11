"""
rag_knowledge.py
=================
Base de conocimiento clínico local usada como corpus de recuperación (RAG)
para explicar los resultados del clasificador. Cada fragmento (`chunk`) tiene
`tags` que se usan para la recuperación: se seleccionan los fragmentos cuyo
tag coincide con la clase predicha y/o con el estado de incertidumbre, más un
pequeño conjunto de fragmentos generales que siempre se incluyen.

El contenido es deliberadamente conservador: describe hallazgos típicos y
conducta clínica general aceptada para retinopatía diabética (escala
ICDR/ETDRS), pero nunca afirma un diagnóstico definitivo ni reemplaza la
evaluación de un profesional — eso se refuerza también en el prompt del LLM
en `rag.py` y en la plantilla de respaldo.
"""

from __future__ import annotations

CHUNKS: list[dict] = [
    {
        "id": "class_0",
        "tags": ["class_0"],
        "title": "Clase 0 — Sin retinopatía aparente",
        "text": (
            "No se observan signos de retinopatía diabética en la imagen analizada. "
            "Esto no elimina el riesgo futuro: en personas con diabetes, la retina "
            "debe revisarse con un examen de fondo de ojo dilatado al menos una vez "
            "al año, ya que la retinopatía puede desarrollarse de forma progresiva y "
            "silenciosa."
        ),
    },
    {
        "id": "class_1",
        "tags": ["class_1"],
        "title": "Clase 1 — Retinopatía diabética leve (no proliferativa)",
        "text": (
            "Se observan microaneurismas, la lesión más temprana de la retinopatía "
            "diabética: pequeñas dilataciones de los capilares retinianos. En esta "
            "etapa suele no haber síntomas visuales. La conducta habitual es control "
            "oftalmológico de seguimiento (típicamente cada 6 a 12 meses) y optimizar "
            "el control glicémico, de presión arterial y de lípidos."
        ),
    },
    {
        "id": "class_2",
        "tags": ["class_2"],
        "title": "Clase 2 — Retinopatía diabética moderada (no proliferativa)",
        "text": (
            "Además de microaneurismas, se aprecian más lesiones: hemorragias "
            "intrarretinianas puntiformes, exudados y/o alteraciones venosas leves. "
            "El riesgo de progresión aumenta respecto a la etapa leve, por lo que se "
            "recomienda una evaluación por oftalmología en un plazo de semanas a "
            "pocos meses, no esperar al control anual de rutina."
        ),
    },
    {
        "id": "class_3",
        "tags": ["class_3"],
        "title": "Clase 3 — Retinopatía diabética severa (no proliferativa)",
        "text": (
            "Hay hemorragias extensas y anomalías vasculares significativas (p. ej. "
            "arrosariamiento venoso, anomalías microvasculares intrarretinianas). "
            "Esta etapa tiene un riesgo alto de progresar a retinopatía proliferativa "
            "en poco tiempo. Se recomienda evaluación por un retinólogo de forma "
            "prioritaria (idealmente en días a pocas semanas), no diferirla."
        ),
    },
    {
        "id": "class_4",
        "tags": ["class_4"],
        "title": "Clase 4 — Retinopatía diabética proliferativa",
        "text": (
            "Es la etapa más avanzada: se ha desarrollado neovascularización (nuevos "
            "vasos sanguíneos anómalos) que pueden sangrar hacia el vítreo o traccionar "
            "la retina y desprenderla. El riesgo de pérdida de visión significativa es "
            "alto. Se recomienda atención oftalmológica urgente — idealmente en los "
            "próximos días — para valorar fotocoagulación láser, terapia anti-VEGF o "
            "cirugía vitreorretiniana según el caso."
        ),
    },
    {
        "id": "uncertainty",
        "tags": ["uncertain"],
        "title": "Resultado incierto / ambiguo",
        "text": (
            "El modelo encontró probabilidades muy similares entre varias etapas de "
            "retinopatía para esta imagen, es decir, no logró distinguir con "
            "suficiente confianza cuál es la más probable. En este caso el sistema se "
            "abstiene deliberadamente de afirmar una clase concreta, porque hacerlo "
            "podría transmitir una falsa sensación de certeza. Un resultado incierto "
            "no significa que todo esté bien ni que sea grave: significa que esta "
            "imagen requiere el criterio de un profesional. Puede deberse a calidad de "
            "imagen (enfoque, iluminación, artefactos) o a hallazgos límite entre dos "
            "etapas."
        ),
    },
    {
        "id": "gradcam",
        "tags": ["general"],
        "title": "Qué muestra el mapa de calor (Grad-CAM)",
        "text": (
            "El mapa de calor (Grad-CAM) resalta en colores cálidos las zonas de la "
            "imagen que más influyeron en la predicción del modelo. No es un diagnóstico "
            "por sí mismo: es una herramienta de explicabilidad para entender en qué se "
            "fijó la red neuronal, útil para verificar si la atención coincide con zonas "
            "clínicamente relevantes (lesiones, vasos, disco óptico) o con artefactos."
        ),
    },
    {
        "id": "urgent_signs",
        "tags": ["general", "class_3", "class_4"],
        "title": "Señales de alarma que requieren atención inmediata",
        "text": (
            "Independientemente del resultado del clasificador, acudir de urgencia a "
            "un servicio oftalmológico ante: aparición súbita de manchas oscuras "
            "flotantes ('moscas volantes') en gran cantidad, destellos de luz "
            "(fotopsias), una sombra o cortina que cubre parte del campo visual, o "
            "pérdida brusca de agudeza visual. Estos son signos posibles de hemorragia "
            "vítrea o desprendimiento de retina."
        ),
    },
    {
        "id": "limitations",
        "tags": ["general"],
        "title": "Límites de esta herramienta",
        "text": (
            "Este clasificador es un proyecto académico/demostrativo (competencia "
            "EUREKA, categoría Ciencias de la Salud). No es un dispositivo médico "
            "certificado, no sustituye el examen clínico de un oftalmólogo y su "
            "resultado no debe usarse como base única para decisiones de tratamiento."
        ),
    },
]


def retrieve(predicted_class: int, is_uncertain: bool) -> list[dict]:
    """Recupera del corpus los fragmentos relevantes para esta predicción: el
    fragmento específico de la clase (solo si el resultado NO es incierto —
    de lo contrario ese texto describiría con lenguaje seguro una etapa
    concreta que el sistema decidió no afirmar, contradiciendo la
    abstención), el de incertidumbre si aplica, y los fragmentos generales
    (Grad-CAM, señales de alarma, límites de la herramienta). Simétrico con
    _render_fallback() en rag.py, que ya excluía el fragmento de clase en la
    plantilla determinística cuando is_uncertain=True."""
    wanted_tags = {"general"}
    if is_uncertain:
        wanted_tags.add("uncertain")
    else:
        wanted_tags.add(f"class_{predicted_class}")

    return [chunk for chunk in CHUNKS if wanted_tags & set(chunk["tags"])]
