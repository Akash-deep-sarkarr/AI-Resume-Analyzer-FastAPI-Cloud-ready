const form = document.getElementById("analyzer-form");
const statusEl = document.getElementById("status");
const resultsSection = document.getElementById("results");
const matchScoreText = document.getElementById("match-score-text");
const matchRing = document.getElementById("match-ring");
const matchedSkillsEl = document.getElementById("matched-skills");
const missingSkillsEl = document.getElementById("missing-skills");
const suggestionsListEl = document.getElementById("suggestions-list");
const resumeSummaryEl = document.getElementById("resume-summary");
const jdHintEl = document.getElementById("jd-hint");
const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("resume");

// Use same origin by default so it works locally and on cloud
const API_BASE = window.location.origin.replace(/\/$/, "");

let radarChart = null;
let barChart = null;
// Drag & drop handlers
["dragenter", "dragover"].forEach((eventName) => {
  dropZone.addEventListener(eventName, (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.add("ring-2", "ring-blue-500");
  });
});

["dragleave", "drop"].forEach((eventName) => {
  dropZone.addEventListener(eventName, (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove("ring-2", "ring-blue-500");
  });
});

dropZone.addEventListener("drop", (e) => {
  const dt = e.dataTransfer;
  const files = dt.files;
  if (files && files[0]) {
    fileInput.files = files;
    const label = dropZone.querySelector("span[data-drop-label]");
    if (label) {
      label.textContent = files[0].name;
    }
  }
});

// Allow click to open file dialog
dropZone.addEventListener("click", () => {
  fileInput.click();
});

// When file is selected via dialog, update label
fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  const label = dropZone.querySelector("span[data-drop-label]");
  if (file && label) {
    label.textContent = file.name;
  }
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const resumeFile = fileInput.files[0];
  const jobDescription = document.getElementById("job-description").value.trim();

  if (!resumeFile || !jobDescription) {
    statusEl.textContent = "Please upload a resume and paste a job description.";
    return;
  }

  const formData = new FormData();
  formData.append("resume", resumeFile);
  formData.append("job_description", jobDescription);

  statusEl.textContent = "Analyzing resume and job description using AI...";
  resultsSection.hidden = true;

  try {
    const response = await fetch(`${API_BASE}/analyze_resume`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }

    const data = await response.json();
    renderResults(data);
    statusEl.textContent = "Analysis complete.";
  } catch (err) {
    console.error(err);
    statusEl.textContent = "Failed to analyze resume. Please ensure the backend is running.";
  }
});

function renderResults(data) {
  resultsSection.hidden = false;

  const score = data.match_score ?? 0;
  updateMatchRing(score);

  renderChips(matchedSkillsEl, data.matched_skills || [], "matched");
  renderChips(missingSkillsEl, data.missing_skills || [], "missing");
  renderList(suggestionsListEl, data.suggestions || []);

  resumeSummaryEl.textContent = data.resume_summary || "No summary available.";

  updateCharts(data);
}

function updateMatchRing(score) {
  const normalized = Math.max(0, Math.min(100, score));
  const circle = matchRing;
  const radius = circle.r.baseVal.value;
  const circumference = 2 * Math.PI * radius;

  circle.style.strokeDasharray = `${circumference} ${circumference}`;
  const offset = circumference - (normalized / 100) * circumference;
  circle.style.strokeDashoffset = offset;

  matchScoreText.textContent = `${normalized}%`;
}

function renderChips(container, items, type) {
  container.innerHTML = "";
  if (!items.length) {
    const span = document.createElement("span");
    span.className = "inline-flex items-center px-3 py-1 rounded-full text-xs bg-gray-200 text-gray-700";
    span.textContent = "None";
    container.appendChild(span);
    return;
  }

  items.forEach((item) => {
    const span = document.createElement("span");
    let base = "inline-flex items-center px-3 py-1 rounded-full text-xs font-medium mr-2 mb-2";
    if (type === "matched") {
      span.className = `${base} bg-green-100 text-green-700`;
    } else if (type === "missing") {
      span.className = `${base} bg-red-100 text-red-700`;
    } else {
      span.className = `${base} bg-blue-100 text-blue-700`;
    }
    span.textContent = item;
    container.appendChild(span);
  });
}

function renderList(container, items) {
  container.innerHTML = "";
  if (!items.length) {
    const li = document.createElement("li");
    li.textContent = "None";
    container.appendChild(li);
    return;
  }

  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    container.appendChild(li);
  });
}

function updateCharts(data) {
  const ctxRadar = document.getElementById("skills-radar");
  const ctxBar = document.getElementById("skills-bar");
  if (!ctxRadar || !ctxBar || typeof Chart === "undefined") return;

  const jdSkills = data.jd_skills || [];
  const resumeSkills = new Set(data.resume_skills || []);

  if (!jdSkills.length) {
    if (radarChart) radarChart.destroy();
    if (barChart) barChart.destroy();
    return;
  }

  const labels = jdSkills;
  const resumeData = labels.map((s) => (resumeSkills.has(s) ? 1 : 0));
  const jdData = labels.map(() => 1);

  if (radarChart) radarChart.destroy();
  radarChart = new Chart(ctxRadar, {
    type: "radar",
    data: {
      labels,
      datasets: [
        {
          label: "Job Description",
          data: jdData,
          borderColor: "rgba(59,130,246,1)",
          backgroundColor: "rgba(59,130,246,0.2)",
        },
        {
          label: "Resume",
          data: resumeData,
          borderColor: "rgba(16,185,129,1)",
          backgroundColor: "rgba(16,185,129,0.2)",
        },
      ],
    },
    options: {
      scales: {
        r: {
          beginAtZero: true,
          max: 1,
          ticks: { stepSize: 1 },
        },
      },
    },
  });

  if (barChart) barChart.destroy();
  barChart = new Chart(ctxBar, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Skill Coverage (1 = present, 0 = missing)",
          data: resumeData,
          backgroundColor: resumeData.map((v) => (v ? "rgba(16,185,129,0.7)" : "rgba(248,113,113,0.7)")),
        },
      ],
    },
    options: {
      scales: {
        y: {
          beginAtZero: true,
          max: 1,
          ticks: { stepSize: 1 },
        },
      },
    },
  });
}
