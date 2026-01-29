const API_BASE = "http://localhost:8000"; // luego lo cambias al URL de AWS API Gateway

const countrySelect = document.getElementById("countrySelect");
const companySelect = document.getElementById("companySelect");
const branchSelect = document.getElementById("branchSelect");
const questionsArea = document.getElementById("questionsArea");
const submitBtn = document.getElementById("submitBtn");
const statusEl = document.getElementById("status");
const exportLink = document.getElementById("exportLink");

let questions = [];

function setStatus(msg, type = "") {
  statusEl.className = "status " + type;
  statusEl.textContent = msg || "";
}

function setLoadingSelect(select, text) {
  select.innerHTML = `<option value="">${text}</option>`;
}

async function apiGet(path) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`Error ${res.status} en ${path}`);
  return res.json();
}

async function apiPost(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`Error ${res.status} en ${path}`);
  return res.json();
}

async function loadCountries() {
  try {
    setStatus("Cargando países...", "");
    setLoadingSelect(countrySelect, "Cargando...");
    const data = await apiGet("/countries");
    countrySelect.innerHTML = `<option value="">Seleccione un país</option>` +
      data.map(c => `<option value="${c.id}">${c.name}</option>`).join("");
    setStatus("", "");
  } catch (e) {
    setStatus("No se pudieron cargar países. " + e.message, "err");
    setLoadingSelect(countrySelect, "Error al cargar");
  }
}

async function loadCompanies(countryId) {
  try {
    setStatus("Cargando empresas...", "");
    companySelect.disabled = true;
    branchSelect.disabled = true;
    setLoadingSelect(companySelect, "Cargando...");
    setLoadingSelect(branchSelect, "Seleccione una empresa");

    const data = await apiGet(`/companies?country_id=${countryId}`);
    companySelect.innerHTML = `<option value="">Seleccione una empresa</option>` +
      data.map(c => `<option value="${c.id}">${c.name}</option>`).join("");
    companySelect.disabled = false;
    setStatus("", "");
  } catch (e) {
    setStatus("No se pudieron cargar empresas. " + e.message, "err");
    setLoadingSelect(companySelect, "Error al cargar");
  }
}

async function loadBranches(companyId) {
  try {
    setStatus("Cargando sedes...", "");
    branchSelect.disabled = true;
    setLoadingSelect(branchSelect, "Cargando...");
    const data = await apiGet(`/branches?company_id=${companyId}`);
    branchSelect.innerHTML = `<option value="">Seleccione una sede</option>` +
      data.map(b => `<option value="${b.id}">${b.name}</option>`).join("");
    branchSelect.disabled = false;
    setStatus("", "");
  } catch (e) {
    setStatus("No se pudieron cargar sedes. " + e.message, "err");
    setLoadingSelect(branchSelect, "Error al cargar");
  }
}

async function loadQuestions() {
  try {
    setStatus("Cargando preguntas...", "");
    questionsArea.innerHTML = "Cargando preguntas...";
    questions = await apiGet("/questions");

    questionsArea.innerHTML = questions.map(q => `
      <div class="question">
        <div><b>${q.text}</b></div>
        <div class="small">Respuesta</div>
        <input type="text" data-qid="${q.id}" placeholder="Escriba su respuesta..." />
      </div>
    `).join("");

    setStatus("", "");
  } catch (e) {
    setStatus("No se pudieron cargar preguntas. " + e.message, "err");
    questionsArea.innerHTML = `<div class="muted">Error cargando preguntas.</div>`;
  }
}

function getAnswersFromUI() {
  const inputs = questionsArea.querySelectorAll("input[data-qid]");
  const answers = [];
  inputs.forEach(inp => {
    answers.push({ question_id: Number(inp.dataset.qid), value: inp.value.trim() || "-" });
  });
  return answers;
}

// Events
countrySelect.addEventListener("change", async () => {
  const countryId = countrySelect.value;
  setStatus("", "");
  submitBtn.disabled = true;
  questionsArea.innerHTML = `<div class="muted">Seleccione una sede para cargar preguntas.</div>`;

  companySelect.innerHTML = `<option value="">Seleccione un país</option>`;
  branchSelect.innerHTML = `<option value="">Seleccione una empresa</option>`;
  companySelect.disabled = true;
  branchSelect.disabled = true;

  if (!countryId) return;
  await loadCompanies(countryId);
});

companySelect.addEventListener("change", async () => {
  const companyId = companySelect.value;
  setStatus("", "");
  submitBtn.disabled = true;
  questionsArea.innerHTML = `<div class="muted">Seleccione una sede para cargar preguntas.</div>`;

  branchSelect.innerHTML = `<option value="">Seleccione una empresa</option>`;
  branchSelect.disabled = true;

  if (!companyId) return;
  await loadBranches(companyId);
});

branchSelect.addEventListener("change", async () => {
  const branchId = branchSelect.value;
  setStatus("", "");
  submitBtn.disabled = true;

  if (!branchId) {
    questionsArea.innerHTML = `<div class="muted">Seleccione una sede para cargar preguntas.</div>`;
    return;
  }

  await loadQuestions();
  submitBtn.disabled = false;

  // link de export
  exportLink.href = `${API_BASE}/export`;
});

submitBtn.addEventListener("click", async () => {
  try {
    const branchId = branchSelect.value;
    if (!branchId) {
      setStatus("Seleccione una sede antes de enviar.", "err");
      return;
    }

    submitBtn.disabled = true;
    setStatus("Enviando encuesta...", "");

    const payload = {
      branch_id: branchId,
      answers: getAnswersFromUI(),
    };

    const res = await apiPost("/responses", payload);

    setStatus(`✅ Encuesta enviada. ID: ${res.survey_response_id}`, "ok");
  } catch (e) {
    setStatus("No se pudo enviar la encuesta. " + e.message, "err");
  } finally {
    submitBtn.disabled = false;
  }
});

// Init
loadCountries();
