const form = document.querySelector("#uploadForm");
const formStatus = document.querySelector("#formStatus");
const candidateList = document.querySelector("#candidateList");
const candidateCount = document.querySelector("#candidateCount");
const refreshButton = document.querySelector("#refreshButton");
const dialog = document.querySelector("#detailsDialog");

let candidates = [];

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatDate(value) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function renderCandidates() {
  candidateCount.textContent = `${candidates.length} candidate${candidates.length === 1 ? "" : "s"}`;

  if (candidates.length === 0) {
    candidateList.innerHTML = '<div class="empty">No resumes uploaded yet.</div>';
    return;
  }

  candidateList.innerHTML = candidates
    .map((candidate) => {
      const skills = candidate.matched_skills || "No matched skills yet";
      return `
        <article class="candidate-card">
          <div class="score">${candidate.score}%</div>
          <div>
            <h3>${escapeHtml(candidate.name)}</h3>
            <p class="meta">${escapeHtml(candidate.original_filename)} · ${formatDate(candidate.created_at)}</p>
            <p class="skills">${escapeHtml(skills)}</p>
          </div>
          <div class="candidate-actions">
            <div class="status ${escapeHtml(candidate.status)}">${escapeHtml(candidate.status)}</div>
            <button class="details-button" data-id="${candidate.id}">Details</button>
          </div>
        </article>
      `;
    })
    .join("");
}

async function loadCandidates() {
  const response = await fetch("/api/candidates");
  if (!response.ok) {
    throw new Error("Could not load candidates");
  }
  candidates = await response.json();
  renderCandidates();
}

async function uploadResume(event) {
  event.preventDefault();
  const data = new FormData(form);
  formStatus.textContent = "Uploading resume...";

  const response = await fetch("/api/resumes", {
    method: "POST",
    body: data,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Upload failed");
  }

  form.reset();
  formStatus.textContent = "Resume queued. Worker will process it shortly.";
  await loadCandidates();
}

function showDetails(candidate) {
  document.querySelector("#detailsName").textContent = candidate.name;
  document.querySelector("#detailsScore").textContent = `${candidate.score}%`;
  document.querySelector("#detailsStatus").textContent = candidate.status;
  document.querySelector("#detailsSkills").textContent = candidate.matched_skills || "None yet";
  document.querySelector("#detailsText").textContent =
    candidate.error_message || candidate.extracted_text || "Text has not been extracted yet.";
  dialog.showModal();
}

form.addEventListener("submit", (event) => {
  uploadResume(event).catch((error) => {
    formStatus.textContent = error.message;
  });
});

refreshButton.addEventListener("click", () => {
  loadCandidates().catch((error) => {
    formStatus.textContent = error.message;
  });
});

candidateList.addEventListener("click", (event) => {
  const button = event.target.closest("[data-id]");
  if (!button) return;
  const candidate = candidates.find((item) => item.id === Number(button.dataset.id));
  if (candidate) showDetails(candidate);
});

document.querySelector("#closeDialog").addEventListener("click", () => dialog.close());

loadCandidates().catch((error) => {
  candidateList.innerHTML = `<div class="empty">${escapeHtml(error.message)}</div>`;
});

setInterval(() => {
  loadCandidates().catch(() => undefined);
}, 5000);
