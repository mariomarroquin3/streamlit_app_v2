/**
 * classifier.js
 * Maneja la subida de imagen (arrastrar/soltar o selección), llama a la API
 * /api/clasificar y renderiza la predicción, las probabilidades por clase y
 * las imágenes de Grad-CAM.
 */
(function () {
  "use strict";

  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("fileInput");
  const previewStrip = document.getElementById("previewStrip");
  const previewThumb = document.getElementById("previewThumb");
  const previewName = document.getElementById("previewName");
  const previewMeta = document.getElementById("previewMeta");
  const clearBtn = document.getElementById("clearBtn");
  const analyzing = document.getElementById("analyzing");
  const errorBanner = document.getElementById("errorBanner");
  const resultsWrap = document.getElementById("resultsWrap");

  const originalImg = document.getElementById("originalImg");
  const resultBadge = document.getElementById("resultBadge");
  const resultBadgeText = document.getElementById("resultBadgeText");
  const resultDesc = document.getElementById("resultDesc");
  const confidenceValue = document.getElementById("confidenceValue");
  const confidenceTag = document.getElementById("confidenceTag");
  const probList = document.getElementById("probList");
  const processedImg = document.getElementById("processedImg");
  const heatmapImg = document.getElementById("heatmapImg");
  const overlayImg = document.getElementById("overlayImg");
  const downloadBtn = document.getElementById("downloadBtn");

  const printReportBtn = document.getElementById("printReportBtn");
  const printReportDate = document.getElementById("printReportDate");
  const printReportId = document.getElementById("printReportId");

  const historyPanel = document.getElementById("historyPanel");
  const historyList = document.getElementById("historyList");
  const historyClearBtn = document.getElementById("historyClearBtn");
  const historyTrend = document.getElementById("historyTrend");

  const reportIssueBtn = document.getElementById("reportIssueBtn");
  const reportForm = document.getElementById("reportForm");
  const reportComment = document.getElementById("reportComment");
  const reportCancelBtn = document.getElementById("reportCancelBtn");
  const reportSubmitBtn = document.getElementById("reportSubmitBtn");
  const reportStatus = document.getElementById("reportStatus");

  const uncertaintyBanner = document.getElementById("uncertaintyBanner");
  const uncertaintyBannerText = document.getElementById("uncertaintyBannerText");
  const explainBtn = document.getElementById("explainBtn");
  const explanationHint = document.getElementById("explanationHint");
  const explanationLoading = document.getElementById("explanationLoading");
  const explanationError = document.getElementById("explanationError");
  const explanationText = document.getElementById("explanationText");
  const explanationSource = document.getElementById("explanationSource");

  let lastClassificationResult = null;

  if (!dropzone) return; // esta página no está activa

  // Etiqueta cualitativa de confianza: un número crudo como "43.8%" no deja
  // claro por sí solo si es una predicción confiable o no — el banner de
  // incertidumbre solo se activa cuando varias clases compiten muy de
  // cerca, así que un resultado "no técnicamente incierto" pero con
  // confianza baja (p. ej. 43.8%) podía leerse como más confiable de lo
  // que realmente es.
  function confidenceTagInfo(confidence) {
    if (confidence >= 0.7) return { text: "Confianza alta", cls: "conf-high" };
    if (confidence >= 0.45) return { text: "Confianza moderada", cls: "conf-moderate" };
    return { text: "Confianza baja", cls: "conf-low" };
  }

  // --- Historial local de clasificaciones (localStorage, sin backend) ---
  // Permite comparar el resultado actual contra visitas anteriores en el
  // mismo navegador — útil para una enfermedad progresiva como la
  // retinopatía diabética, donde lo relevante suele ser el cambio en el
  // tiempo, no solo una foto aislada. No se envía a ningún servidor.
  const HISTORY_KEY = "retinovision_history_v1";
  const HISTORY_MAX_ENTRIES = 20;
  const HISTORY_THUMB_SIZE = 72;

  function loadHistory() {
    try {
      const raw = localStorage.getItem(HISTORY_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch (e) {
      return []; // localStorage no disponible (modo privado, cuota, etc.) — la app sigue funcionando sin historial
    }
  }

  function saveHistoryEntry(entry) {
    try {
      const history = loadHistory();
      history.unshift(entry);
      if (history.length > HISTORY_MAX_ENTRIES) history.length = HISTORY_MAX_ENTRIES;
      localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
    } catch (e) {
      // Cuota excedida o storage deshabilitado: se pierde el historial de esta clasificación, pero no rompe el flujo principal
    }
  }

  function clearHistoryStorage() {
    try {
      localStorage.removeItem(HISTORY_KEY);
    } catch (e) {
      /* no-op */
    }
  }

  function makeThumbnail(imgEl, size) {
    try {
      const canvas = document.createElement("canvas");
      canvas.width = size;
      canvas.height = size;
      const ctx = canvas.getContext("2d");
      const s = Math.min(imgEl.naturalWidth, imgEl.naturalHeight);
      const sx = (imgEl.naturalWidth - s) / 2;
      const sy = (imgEl.naturalHeight - s) / 2;
      ctx.drawImage(imgEl, sx, sy, s, s, 0, 0, size, size);
      return canvas.toDataURL("image/jpeg", 0.55);
    } catch (e) {
      return null; // p. ej. imagen cross-origin que "mancha" el canvas — el historial se guarda sin miniatura
    }
  }

  function formatHistoryDate(isoString) {
    try {
      return new Date(isoString).toLocaleDateString("es-SV", { day: "numeric", month: "short", year: "numeric" });
    } catch (e) {
      return "";
    }
  }

  function renderHistoryPanel() {
    if (!historyPanel || !historyList) return;
    const history = loadHistory();

    if (history.length === 0) {
      historyPanel.style.display = "none";
      return;
    }

    historyPanel.style.display = "block";
    historyList.innerHTML = "";
    history.forEach(function (entry) {
      const item = document.createElement("div");
      item.className = "history-item";
      item.innerHTML =
        (entry.thumbnail ? '<img src="' + entry.thumbnail + '" alt="">' : '<img alt="">') +
        '<div class="history-item-info">' +
        '<div class="history-item-class"><span class="history-dot" style="background:' + entry.color + '"></span>' +
        "Clase " + entry.predicted_class + " — " + entry.class_name + "</div>" +
        '<div class="history-item-meta">' + formatHistoryDate(entry.timestamp) + " · " + (entry.confidence * 100).toFixed(1) + "%</div>" +
        "</div>";
      historyList.appendChild(item);
    });
  }

  // Compara el resultado nuevo contra la entrada más reciente ANTERIOR a
  // él (no contra sí mismo). Si cualquiera de los dos resultados es
  // incierto, no se afirma una tendencia — no es información confiable
  // para comparar.
  function renderHistoryTrend(newEntry, previousEntry) {
    if (!historyTrend) return;
    if (!previousEntry || newEntry.is_uncertain || previousEntry.is_uncertain) {
      historyTrend.style.display = "none";
      return;
    }

    let cls, text, icon;
    if (newEntry.predicted_class < previousEntry.predicted_class) {
      cls = "trend-down";
      text = "Mejoró respecto a tu última clasificación (" + formatHistoryDate(previousEntry.timestamp) + ": Clase " + previousEntry.predicted_class + ")";
      icon = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/></svg>';
    } else if (newEntry.predicted_class > previousEntry.predicted_class) {
      cls = "trend-up";
      text = "Empeoró respecto a tu última clasificación (" + formatHistoryDate(previousEntry.timestamp) + ": Clase " + previousEntry.predicted_class + ") — considera una revisión profesional";
      icon = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>';
    } else {
      cls = "trend-same";
      text = "Se mantuvo igual que tu última clasificación (" + formatHistoryDate(previousEntry.timestamp) + ")";
      icon = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"/></svg>';
    }

    historyTrend.className = "history-trend " + cls;
    historyTrend.innerHTML = icon + "<span>" + text + "</span>";
    historyTrend.style.display = "flex";
  }

  if (historyClearBtn) {
    historyClearBtn.addEventListener("click", function () {
      if (!confirm("¿Borrar tu historial local de clasificaciones? Esta acción no se puede deshacer.")) return;
      clearHistoryStorage();
      renderHistoryPanel();
      if (historyTrend) historyTrend.style.display = "none";
    });
  }

  renderHistoryPanel(); // mostrar historial previo (si existe) al cargar la página

  function formatBytes(bytes) {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(0) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  }

  function showError(message) {
    errorBanner.textContent = message;
    errorBanner.classList.add("is-visible");
  }

  function hideError() {
    errorBanner.classList.remove("is-visible");
    errorBanner.textContent = "";
  }

  function resetResults() {
    resultsWrap.classList.remove("is-visible");
  }

  function handleFile(file) {
    hideError();
    resetResults();

    if (!file) return;

    const validTypes = ["image/jpeg", "image/png"];
    if (!validTypes.includes(file.type)) {
      showError("Formato no soportado. Usa una imagen JPG o PNG.");
      return;
    }

    previewThumb.src = URL.createObjectURL(file);
    previewName.textContent = file.name;
    previewMeta.textContent = formatBytes(file.size);
    previewStrip.style.display = "flex";

    uploadAndClassify(file);
  }

  function uploadAndClassify(file) {
    const formData = new FormData();
    formData.append("file", file);

    analyzing.classList.add("is-visible");

    fetch("/api/clasificar", {
      method: "POST",
      body: formData,
    })
      .then(function (response) {
        return response.json().then(function (data) {
          if (!response.ok) {
            throw new Error(data.error || "No se pudo analizar la imagen.");
          }
          return data;
        });
      })
      .then(renderResult)
      .catch(function (err) {
        showError(err.message || "Ocurrió un error al analizar la imagen.");
      })
      .finally(function () {
        analyzing.classList.remove("is-visible");
      });
  }

  function renderResult(data) {
    lastClassificationResult = data;

    originalImg.src = previewThumb.src;

    resultBadge.style.backgroundColor = data.color;
    resultBadgeText.textContent = "Clase " + data.predicted_class + " — " + data.class_name;
    resultDesc.textContent = data.description;
    confidenceValue.textContent = (data.confidence * 100).toFixed(1) + "%";
    if (confidenceTag) {
      const tagInfo = confidenceTagInfo(data.confidence);
      confidenceTag.textContent = tagInfo.text;
      confidenceTag.className = "confidence-tag " + tagInfo.cls;
    }

    if (data.is_uncertain) {
      uncertaintyBannerText.textContent = data.uncertainty_message || "Se recomienda visitar a un profesional.";
      uncertaintyBanner.style.display = "flex";
    } else {
      uncertaintyBanner.style.display = "none";
    }

    // Reiniciar el panel de explicación para el nuevo resultado
    explanationHint.style.display = "block";
    explanationError.style.display = "none";
    explanationText.style.display = "none";
    explanationText.textContent = "";
    explanationSource.style.display = "none";
    explainBtn.disabled = false;

    // Reiniciar el panel de reporte de retroalimentación
    if (reportForm) {
      reportForm.style.display = "none";
      reportComment.value = "";
      reportStatus.style.display = "none";
      reportSubmitBtn.disabled = false;
    }

    if (printReportDate) {
      printReportDate.textContent =
        "Generado el " + new Date().toLocaleString("es-SV", { dateStyle: "long", timeStyle: "short" });
    }
    if (printReportId) {
      printReportId.textContent = "RV-" + Date.now().toString(36).toUpperCase();
    }

    probList.innerHTML = "";
    data.probabilities.forEach(function (p) {
      const row = document.createElement("div");
      row.className = "prob-row";
      row.innerHTML =
        '<span class="prob-name">' + p.class_index + " — " + p.class_name + "</span>" +
        '<span class="prob-track"><span class="prob-fill" style="background:' + p.color + '"></span></span>' +
        '<span class="prob-pct">' + (p.value * 100).toFixed(1) + "%</span>";
      probList.appendChild(row);

      const fill = row.querySelector(".prob-fill");
      // Forzar reflow antes de fijar el ancho final para que la transición de
      // CSS se anime desde 0% (en vez de requestAnimationFrame, que algunos
      // navegadores pausan si la pestaña no está visible/enfocada).
      void fill.offsetWidth;
      fill.style.width = (p.value * 100).toFixed(1) + "%";
    });

    processedImg.src = data.processed_image;
    heatmapImg.src = data.heatmap_image;
    overlayImg.src = data.overlay_image;
    downloadBtn.href = data.overlay_image;

    resultsWrap.classList.add("is-visible");
    resultsWrap.scrollIntoView({ behavior: "smooth", block: "start" });

    recordHistoryEntry(data);
  }

  function recordHistoryEntry(data) {
    function save() {
      const previousEntry = loadHistory()[0] || null;
      const entry = {
        id: Date.now().toString(36) + Math.random().toString(36).slice(2, 8),
        timestamp: new Date().toISOString(),
        predicted_class: data.predicted_class,
        class_name: data.class_name,
        confidence: data.confidence,
        is_uncertain: !!data.is_uncertain,
        color: data.color,
        thumbnail: makeThumbnail(originalImg, HISTORY_THUMB_SIZE),
      };
      saveHistoryEntry(entry);
      renderHistoryPanel();
      renderHistoryTrend(entry, previousEntry);
    }

    if (originalImg.complete && originalImg.naturalWidth > 0) {
      save();
    } else {
      originalImg.addEventListener("load", save, { once: true });
    }
  }

  // --- Explicación del resultado vía RAG ---
  function requestExplanation() {
    if (!lastClassificationResult) return;

    explainBtn.disabled = true;
    explanationHint.style.display = "none";
    explanationError.style.display = "none";
    explanationText.style.display = "none";
    explanationSource.style.display = "none";
    explanationLoading.style.display = "flex";

    fetch("/api/explicar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        predicted_class: lastClassificationResult.predicted_class,
        class_name: lastClassificationResult.class_name,
        confidence: lastClassificationResult.confidence,
        probabilities: lastClassificationResult.probabilities,
        is_uncertain: lastClassificationResult.is_uncertain,
      }),
    })
      .then(function (response) {
        return response.json().then(function (data) {
          if (!response.ok) {
            throw new Error(data.error || "No se pudo generar la explicación.");
          }
          return data;
        });
      })
      .then(function (data) {
        explanationText.textContent = data.explanation;
        explanationText.style.display = "block";
        explanationSource.textContent =
          data.source === "llm"
            ? "Explicación generada con IA (" + (data.model || "OpenRouter") + ") a partir de la guía clínica de la herramienta."
            : "Explicación generada localmente a partir de la guía clínica de la herramienta.";
        explanationSource.style.display = "block";
      })
      .catch(function (err) {
        explanationError.textContent = err.message || "Ocurrió un error al generar la explicación.";
        explanationError.style.display = "block";
        explanationHint.style.display = "block";
      })
      .finally(function () {
        explanationLoading.style.display = "none";
        explainBtn.disabled = false;
      });
  }

  if (explainBtn) {
    explainBtn.addEventListener("click", requestExplanation);
  }

  // --- Reporte de retroalimentación clínica ---
  function submitFeedbackReport() {
    if (!lastClassificationResult) return;

    reportSubmitBtn.disabled = true;
    reportStatus.style.display = "none";

    fetch("/api/reportar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        predicted_class: lastClassificationResult.predicted_class,
        confidence: lastClassificationResult.confidence,
        is_uncertain: lastClassificationResult.is_uncertain,
        comment: reportComment.value,
      }),
    })
      .then(function (response) {
        return response.json().then(function (data) {
          if (!response.ok) {
            throw new Error(data.error || "No se pudo enviar el reporte.");
          }
          return data;
        });
      })
      .then(function () {
        reportStatus.textContent = "Gracias, tu reporte quedó registrado para revisión.";
        reportStatus.className = "feedback-status is-success";
        reportStatus.style.display = "block";
      })
      .catch(function (err) {
        reportStatus.textContent = err.message || "Ocurrió un error al enviar el reporte.";
        reportStatus.className = "feedback-status is-error";
        reportStatus.style.display = "block";
        reportSubmitBtn.disabled = false;
      });
  }

  if (reportIssueBtn) {
    reportIssueBtn.addEventListener("click", function () {
      reportForm.style.display = reportForm.style.display === "none" ? "block" : "none";
    });
    reportCancelBtn.addEventListener("click", function () {
      reportForm.style.display = "none";
    });
    reportSubmitBtn.addEventListener("click", submitFeedbackReport);
  }

  // --- Reporte descargable en PDF (vía diálogo de impresión) ---
  if (printReportBtn) {
    printReportBtn.addEventListener("click", function () {
      window.print();
    });
  }

  // --- Interacciones de subida ---
  dropzone.addEventListener("click", function () {
    fileInput.click();
  });
  dropzone.addEventListener("keydown", function (e) {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      fileInput.click();
    }
  });

  ["dragenter", "dragover"].forEach(function (evt) {
    dropzone.addEventListener(evt, function (e) {
      e.preventDefault();
      dropzone.classList.add("is-dragover");
    });
  });
  ["dragleave", "drop"].forEach(function (evt) {
    dropzone.addEventListener(evt, function (e) {
      e.preventDefault();
      dropzone.classList.remove("is-dragover");
    });
  });
  dropzone.addEventListener("drop", function (e) {
    const file = e.dataTransfer.files && e.dataTransfer.files[0];
    handleFile(file);
  });

  fileInput.addEventListener("change", function () {
    handleFile(fileInput.files[0]);
  });

  clearBtn.addEventListener("click", function () {
    fileInput.value = "";
    previewStrip.style.display = "none";
    hideError();
    resetResults();
  });
})();
