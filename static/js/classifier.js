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
  const probList = document.getElementById("probList");
  const processedImg = document.getElementById("processedImg");
  const heatmapImg = document.getElementById("heatmapImg");
  const overlayImg = document.getElementById("overlayImg");
  const downloadBtn = document.getElementById("downloadBtn");

  const printReportBtn = document.getElementById("printReportBtn");
  const printReportDate = document.getElementById("printReportDate");

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
