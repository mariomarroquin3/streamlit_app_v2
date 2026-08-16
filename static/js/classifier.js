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
    originalImg.src = previewThumb.src;

    resultBadge.style.backgroundColor = data.color;
    resultBadgeText.textContent = "Clase " + data.predicted_class + " — " + data.class_name;
    resultDesc.textContent = data.description;
    confidenceValue.textContent = (data.confidence * 100).toFixed(1) + "%";

    probList.innerHTML = "";
    data.probabilities.forEach(function (p) {
      const row = document.createElement("div");
      row.className = "prob-row";
      row.innerHTML =
        '<span class="prob-name">' + p.class_index + " — " + p.class_name + "</span>" +
        '<span class="prob-track"><span class="prob-fill" style="background:' + p.color + '"></span></span>' +
        '<span class="prob-pct">' + (p.value * 100).toFixed(1) + "%</span>";
      probList.appendChild(row);
      // pequeño retraso para que la transición de ancho sea visible
      requestAnimationFrame(function () {
        row.querySelector(".prob-fill").style.width = (p.value * 100).toFixed(1) + "%";
      });
    });

    processedImg.src = data.processed_image;
    heatmapImg.src = data.heatmap_image;
    overlayImg.src = data.overlay_image;
    downloadBtn.href = data.overlay_image;

    resultsWrap.classList.add("is-visible");
    resultsWrap.scrollIntoView({ behavior: "smooth", block: "start" });
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
