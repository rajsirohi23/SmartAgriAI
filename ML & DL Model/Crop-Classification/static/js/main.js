/* ================================================================
   SMART AGRICULTURE AI — disease.js
   Handles: drag-drop upload, image preview, mock analysis UI,
            result reveal, confidence bar, prediction list
   ================================================================ */

(function () {
  "use strict";

  /* ---------------------------------------------------------------
     DOM refs
  --------------------------------------------------------------- */
  const dropzone        = document.getElementById("dropzone");
  const imageInput      = document.getElementById("imageInput");
  const dropzoneFilename = document.getElementById("dropzoneFilename");
  const dropzonePreview  = document.getElementById("dropzonePreview");
  const analyzeBtn       = document.getElementById("analyzeBtn");

  // Result section
  const resultSection    = document.getElementById("resultSection");
  const resultImage      = document.getElementById("resultImage");
  const resultStatusCard = document.getElementById("resultStatusCard");
  const resultBadge      = document.getElementById("resultBadge");
  const resultHeadline   = document.getElementById("resultHeadline");
  const resultSummary    = document.getElementById("resultSummary");
  const resultDiseaseMeta = document.getElementById("resultDiseaseMeta");
  const resultDiseaseName = document.getElementById("resultDiseaseName");
  const resultConfidence = document.getElementById("resultConfidence");
  const confidenceBar    = document.getElementById("confidenceBar");
  const predictionsList  = document.getElementById("predictionsList");

  // Holds the current selected file
  let selectedFile = null;

  /* ---------------------------------------------------------------
     1. FILE SELECTION — input change
  --------------------------------------------------------------- */
  imageInput.addEventListener("change", function () {
    if (this.files && this.files[0]) {
      handleFile(this.files[0]);
    }
  });

  /* ---------------------------------------------------------------
     2. DRAG & DROP
  --------------------------------------------------------------- */
  dropzone.addEventListener("dragover", function (e) {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });

  dropzone.addEventListener("dragleave", function () {
    dropzone.classList.remove("dragover");
  });

  dropzone.addEventListener("drop", function (e) {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith("image/")) {
      handleFile(file);
    } else {
      showToast("Please drop a valid image file (JPG, PNG).", "error");
    }
  });

  /* ---------------------------------------------------------------
     3. HANDLE FILE — preview + store
  --------------------------------------------------------------- */
  function handleFile(file) {
    // Validate type
    const validTypes = ["image/jpeg", "image/jpg", "image/png", "image/webp"];
    if (!validTypes.includes(file.type)) {
      showToast("Unsupported format. Please use JPG, PNG, or WebP.", "error");
      return;
    }
    // Validate size (10 MB)
    if (file.size > 10 * 1024 * 1024) {
      showToast("File too large. Max size is 10 MB.", "error");
      return;
    }

    selectedFile = file;

    // Show filename
    dropzoneFilename.textContent = "📎 " + file.name;
    dropzoneFilename.classList.add("visible");

    // Show image preview
    const reader = new FileReader();
    reader.onload = function (e) {
      dropzonePreview.src = e.target.result;
      dropzonePreview.classList.add("visible");
    };
    reader.readAsDataURL(file);

    // Update dropzone icon to show selection
    dropzone.querySelector(".dropzone-icon").textContent = "✅";

    // Enable analyze button visual cue
    analyzeBtn.style.animation = "none";
    analyzeBtn.style.boxShadow = "0 0 40px rgba(239,68,68,0.7)";
  }

  /* ---------------------------------------------------------------
     4. ANALYZE BUTTON — simulate analysis with loading state
        In production, replace the mock with a real fetch() to Flask
  --------------------------------------------------------------- */
  analyzeBtn.addEventListener("click", function () {
    if (!selectedFile) {
      showToast("Please select a leaf image first!", "warning");
      // Shake the dropzone
      dropzone.classList.add("shake");
      setTimeout(() => dropzone.classList.remove("shake"), 600);
      return;
    }

    // --- Show loading state ---
    const originalHTML = analyzeBtn.innerHTML;
    analyzeBtn.innerHTML = `
      <span class="spinner"></span>
      <span>Analyzing…</span>
    `;
    analyzeBtn.disabled = true;

    // -------------------------------------------------------
    //  PRODUCTION: replace this setTimeout block with a real
    //  fetch() call to your Flask backend at 127.0.0.1:5003
    //
    //  Example:
    //  const formData = new FormData();
    //  formData.append("image", selectedFile);
    //  fetch("http://127.0.0.1:5003/predict", { method:"POST", body:formData })
    //    .then(r => r.json())
    //    .then(data => renderResult(data))
    //    .catch(() => showToast("Server error. Is Flask running?", "error"));
    //
    //  Expected JSON shape from Flask:
    //  {
    //    status: "healthy" | "diseased" | "invalid",
    //    headline: "Healthy Tomato Leaf",
    //    summary: "No disease markers found.",
    //    disease_name: "Early Blight" | null,
    //    advice: "Continue regular monitoring.",
    //    top_confidence: 94.3,
    //    predictions: [
    //      { label: "Tomato___healthy", confidence: 94.3 },
    //      { label: "Tomato___Early_blight", confidence: 3.1 },
    //      ...
    //    ]
    //  }
    // -------------------------------------------------------

    setTimeout(() => {
      // Mock result for demo (remove once Flask is connected)
      const mockResult = getMockResult(selectedFile.name);
      renderResult(mockResult, selectedFile);

      // Restore button
      analyzeBtn.innerHTML = originalHTML;
      analyzeBtn.disabled = false;
    }, 1800);
  });

  /* ---------------------------------------------------------------
     5. RENDER RESULT
  --------------------------------------------------------------- */
  function renderResult(data, file) {
    // Set preview image
    const reader = new FileReader();
    reader.onload = function (e) {
      resultImage.src = e.target.result;
    };
    reader.readAsDataURL(file);

    // Status badge + card colour
    resultStatusCard.className = "result-status-card " + data.status;

    const badgeIcons = { healthy: "🌱", diseased: "🦠", invalid: "⚠️" };
    const badgeLabels = { healthy: "Healthy Crop", diseased: "Disease Detected", invalid: "Invalid Image" };

    resultBadge.className = "result-status-badge " + data.status;
    resultBadge.innerHTML = `${badgeIcons[data.status] || "🔍"} ${badgeLabels[data.status] || "Unknown"}`;

    // Text
    resultHeadline.textContent = data.headline;
    resultSummary.textContent  = data.summary;

    // Disease name
    if (data.disease_name) {
      resultDiseaseMeta.style.display = "flex";
      resultDiseaseName.textContent   = data.disease_name;
    } else {
      resultDiseaseMeta.style.display = "none";
    }

    // Confidence
    const pct = parseFloat(data.top_confidence) || 0;
    resultConfidence.textContent = pct.toFixed(1) + "%";

    // Confidence bar (animated)
    confidenceBar.className = "confidence-bar " + (data.status === "diseased" ? "red" : "");
    confidenceBar.style.width = "0%";
    setTimeout(() => { confidenceBar.style.width = pct + "%"; }, 100);

    // Predictions list
    predictionsList.innerHTML = "";
    (data.predictions || []).forEach(function (p) {
      const pctP = parseFloat(p.confidence) || 0;
      const item = document.createElement("div");
      item.className = "prediction-item";
      item.innerHTML = `
        <span class="prediction-label">${escapeHTML(p.label)}</span>
        <div class="prediction-bar-wrap">
          <div class="prediction-bar" style="width:0%" data-width="${pctP}%"></div>
        </div>
        <span class="prediction-pct">${pctP.toFixed(1)}%</span>
      `;
      predictionsList.appendChild(item);
    });

    // Animate prediction bars with stagger
    setTimeout(() => {
      predictionsList.querySelectorAll(".prediction-bar").forEach((bar, i) => {
        setTimeout(() => {
          bar.style.width = bar.dataset.width;
        }, i * 100);
      });
    }, 200);

    // Show result section
    resultSection.style.display = "block";
    requestAnimationFrame(() => {
      resultSection.classList.add("visible");
    });

    // Scroll into view smoothly
    setTimeout(() => {
      resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 200);
  }

  /* ---------------------------------------------------------------
     6. MOCK RESULT generator (demo only — replace with real API)
  --------------------------------------------------------------- */
  function getMockResult(filename) {
    // Randomly simulate healthy or diseased for demo
    const isDiseased = Math.random() > 0.5;
    if (isDiseased) {
      return {
        status: "diseased",
        headline: "Early Blight Detected on Tomato",
        summary: "The model has identified symptoms consistent with Early Blight (Alternaria solani). Dark concentric spots visible on lower leaves.",
        disease_name: "Tomato — Early Blight",
        advice: "Apply copper-based fungicide. Remove infected leaves. Ensure proper spacing for airflow.",
        top_confidence: (72 + Math.random() * 20).toFixed(1),
        predictions: [
          { label: "Tomato___Early_blight",     confidence: (72 + Math.random() * 18).toFixed(1) },
          { label: "Tomato___Late_blight",       confidence: (8  + Math.random() * 6 ).toFixed(1) },
          { label: "Tomato___Bacterial_spot",    confidence: (3  + Math.random() * 4 ).toFixed(1) },
          { label: "Tomato___healthy",           confidence: (1  + Math.random() * 2 ).toFixed(1) },
          { label: "Tomato___Leaf_Mold",         confidence: (0.5+ Math.random()     ).toFixed(1) },
        ]
      };
    } else {
      return {
        status: "healthy",
        headline: "Healthy Crop Leaf Detected",
        summary: "No disease markers found. The leaf appears healthy with good chlorophyll distribution and no visible lesions or spots.",
        disease_name: null,
        advice: "Continue regular monitoring and maintain optimal irrigation and fertilization schedules.",
        top_confidence: (88 + Math.random() * 10).toFixed(1),
        predictions: [
          { label: "Tomato___healthy",           confidence: (88 + Math.random() * 8).toFixed(1) },
          { label: "Tomato___Early_blight",      confidence: (4  + Math.random() * 4).toFixed(1) },
          { label: "Pepper__bell___healthy",     confidence: (2  + Math.random() * 2).toFixed(1) },
          { label: "Tomato___Bacterial_spot",    confidence: (0.5+ Math.random()    ).toFixed(1) },
          { label: "Tomato___Late_blight",       confidence: (0.3+ Math.random()*0.5).toFixed(1) },
        ]
      };
    }
  }

  /* ---------------------------------------------------------------
     7. TOAST NOTIFICATION
  --------------------------------------------------------------- */
  function showToast(message, type) {
    const existing = document.querySelector(".disease-toast");
    if (existing) existing.remove();

    const toast = document.createElement("div");
    toast.className = "disease-toast";

    const colors = {
      error:   { bg: "rgba(239,68,68,0.15)",  border: "rgba(239,68,68,0.5)",   color: "#fca5a5" },
      warning: { bg: "rgba(251,191,36,0.15)", border: "rgba(251,191,36,0.5)",  color: "#fde68a" },
      success: { bg: "rgba(74,222,128,0.15)", border: "rgba(74,222,128,0.5)",  color: "#86efac" },
    };
    const c = colors[type] || colors.success;

    toast.style.cssText = `
      position: fixed;
      bottom: 2rem; left: 50%;
      transform: translateX(-50%) translateY(20px);
      background: ${c.bg};
      border: 1px solid ${c.border};
      color: ${c.color};
      padding: 0.7rem 1.5rem;
      border-radius: 99px;
      font-size: 0.85rem; font-weight: 600;
      backdrop-filter: blur(14px);
      z-index: 9999;
      white-space: nowrap;
      box-shadow: 0 8px 30px rgba(0,0,0,0.4);
      opacity: 0;
      transition: opacity 0.3s ease, transform 0.3s ease;
      font-family: 'Inter', sans-serif;
    `;
    toast.textContent = message;
    document.body.appendChild(toast);

    requestAnimationFrame(() => {
      toast.style.opacity = "1";
      toast.style.transform = "translateX(-50%) translateY(0)";
    });

    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateX(-50%) translateY(10px)";
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  /* ---------------------------------------------------------------
     8. UTILS
  --------------------------------------------------------------- */
  function escapeHTML(str) {
    const map = { "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;" };
    return String(str).replace(/[&<>"']/g, m => map[m]);
  }

  /* ---------------------------------------------------------------
     9. INJECT EXTRA STYLES (spinner + shake)
  --------------------------------------------------------------- */
  const extraStyles = document.createElement("style");
  extraStyles.textContent = `
    /* Loading spinner inside button */
    .spinner {
      display: inline-block;
      width: 16px; height: 16px;
      border: 2px solid rgba(255,255,255,0.3);
      border-top-color: #fff;
      border-radius: 50%;
      animation: spin 0.65s linear infinite;
      flex-shrink: 0;
    }
    @keyframes spin { to { transform: rotate(360deg); } }

    /* Dropzone shake on no-file submit */
    .disease-dropzone.shake {
      animation: shake 0.5s ease;
    }
    @keyframes shake {
      0%,100% { transform: translateX(0); }
      20%      { transform: translateX(-8px); }
      40%      { transform: translateX(8px); }
      60%      { transform: translateX(-5px); }
      80%      { transform: translateX(5px); }
    }
  `;
  document.head.appendChild(extraStyles);

})();