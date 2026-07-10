/**
 * Library AI Agent — Frontend JavaScript
 *
 * Handles:
 *   - Sticky nav panel switching + filter chip strip
 *   - Search form (nav search bar) → POST /api/search
 *   - Pin-grid masonry card rendering with colour-block thumbnails
 *   - Reserve / waitlist modal → POST /api/reserve  (with duplicate-hold guard)
 *   - Cancel reservation → DELETE /api/reserve/:id
 *   - All Books panel → GET /api/books
 *   - Dashboard: high-demand + IBM Robo automation alerts
 *   - Light / dark theme toggle (persisted to localStorage)
 *   - Firebase Auth integration (login overlay + sign-in/sign-out)
 *   - Student ID live validation
 */

// ─────────────────────────────────────────────────────────────────────────────
// State
// ─────────────────────────────────────────────────────────────────────────────
const state = {
  studentId: "s001",
  reservations: [],   // { id, bookId, bookTitle, bookAuthor, status, message }
  activeFilter: "all",
  allBooksSubject: "all",
};

// ─────────────────────────────────────────────────────────────────────────────
// DOM refs
// ─────────────────────────────────────────────────────────────────────────────
const $ = (id) => document.getElementById(id);

const searchBtn          = $("searchBtn");
const queryInput         = $("queryInput");
const studentIdInput     = $("studentId");
const studentIdError     = $("studentIdError");
const nluInsights        = $("nluInsights");
const aiMessage          = $("aiMessage");
const aiMessageText      = $("aiMessageText");
const resultsSection     = $("resultsSection");
const booksGrid          = $("booksGrid");
const resultsTitle       = $("resultsTitle");
const emptyState         = $("emptyState");
const loadingState       = $("loadingState");
const reserveModal       = $("reserveModal");
const modalTitle         = $("modalTitle");
const modalSubtitle      = $("modalSubtitle");
const modalBody          = $("modalBody");
const modalConfirm       = $("modalConfirm");
const modalCancel        = $("modalCancel");
const modalClose         = $("modalClose");
const reservationsList   = $("reservationsList");
const highDemandList     = $("highDemandList");
const automationAlerts   = $("automationAlerts");
const runRoboBtn         = $("runRoboBtn");
const toastEl            = $("toast");
const allBooksGrid       = $("allBooksGrid");
const allBooksCount      = $("allBooksCount");
const allBooksLoading    = $("allBooksLoading");

// ─────────────────────────────────────────────────────────────────────────────
// Theme toggle  (persisted to localStorage)
// ─────────────────────────────────────────────────────────────────────────────
const htmlEl         = document.documentElement;
const themeToggle    = $("themeToggle");
const themeIconLight = $("themeIconLight");
const themeIconDark  = $("themeIconDark");

function applyTheme(theme) {
  htmlEl.setAttribute("data-theme", theme);
  if (theme === "dark") {
    themeIconLight.classList.add("hidden");
    themeIconDark.classList.remove("hidden");
  } else {
    themeIconLight.classList.remove("hidden");
    themeIconDark.classList.add("hidden");
  }
}

// Restore from storage or default to light
applyTheme(localStorage.getItem("theme") || "light");

themeToggle.addEventListener("click", () => {
  const next = htmlEl.getAttribute("data-theme") === "dark" ? "light" : "dark";
  applyTheme(next);
  localStorage.setItem("theme", next);
});

// ─────────────────────────────────────────────────────────────────────────────
// Student ID live validation
// ─────────────────────────────────────────────────────────────────────────────
const STUDENT_ID_RE = /^[A-Za-z0-9_\-]{2,20}$/;

function validateStudentIdInput(value) {
  if (!value) return "Student ID is required";
  if (value.length < 2 || value.length > 20) return "Must be 2–20 characters";
  if (!STUDENT_ID_RE.test(value)) return "Letters, digits, hyphens, underscores only";
  return null;
}

studentIdInput.addEventListener("input", () => {
  const err = validateStudentIdInput(studentIdInput.value.trim());
  if (err) {
    studentIdError.textContent = err;
    studentIdError.classList.remove("hidden");
    studentIdInput.style.borderColor = "var(--color-error)";
  } else {
    studentIdError.classList.add("hidden");
    studentIdInput.style.borderColor = "";
  }
});

// ─────────────────────────────────────────────────────────────────────────────
// Panel navigation
// ─────────────────────────────────────────────────────────────────────────────
function switchPanel(panelName) {
  document.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));
  const target = document.getElementById(`panel-${panelName}`);
  if (target) target.classList.add("active");
  if (panelName === "reservations") renderReservations();
  if (panelName === "dashboard")    loadDashboard();
  if (panelName === "books")        loadAllBooks();
}

$("navResBtn").addEventListener("click",   () => switchPanel("reservations"));
$("navDashBtn").addEventListener("click",  () => switchPanel("dashboard"));
$("navBooksBtn").addEventListener("click", () => switchPanel("books"));
$("homeBtn").addEventListener("click", (e) => { e.preventDefault(); switchPanel("search"); });

// ─── Side Drawer ─────────────────────────────────────────────────────────────
const sideDrawer  = $("sideDrawer");
const drawerScrim = $("drawerScrim");

function openDrawer()  {
  sideDrawer.classList.add("open");
  drawerScrim.classList.add("open");
  $("menuToggle").setAttribute("aria-expanded", "true");
}
function closeDrawer() {
  sideDrawer.classList.remove("open");
  drawerScrim.classList.remove("open");
  $("menuToggle").setAttribute("aria-expanded", "false");
}

$("menuToggle").addEventListener("click", openDrawer);
$("drawerClose").addEventListener("click", closeDrawer);
drawerScrim.addEventListener("click", closeDrawer);

// Drawer panel links
sideDrawer.querySelectorAll(".drawer__item[data-panel]").forEach((btn) => {
  btn.addEventListener("click", () => { switchPanel(btn.dataset.panel); closeDrawer(); });
});

// Drawer genre/filter links
sideDrawer.querySelectorAll(".drawer__item[data-filter]").forEach((btn) => {
  btn.addEventListener("click", () => {
    const filter = btn.dataset.filter;
    switchPanel("search");
    document.querySelectorAll(".filter-chip").forEach((c) => c.classList.remove("filter-chip--active"));
    const chip = document.querySelector(`.filter-chip[data-filter="${filter}"]`);
    if (chip) chip.classList.add("filter-chip--active");
    state.activeFilter = filter;
    queryInput.value = filter === "all" ? "" : filter;
    if (filter !== "all") doSearch();
    closeDrawer();
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// Filter chip strip (search panel)
// ─────────────────────────────────────────────────────────────────────────────
document.querySelectorAll("#filterStrip .filter-chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    document.querySelectorAll("#filterStrip .filter-chip").forEach((c) => c.classList.remove("filter-chip--active"));
    chip.classList.add("filter-chip--active");
    const filter = chip.dataset.filter;
    state.activeFilter = filter;
    if (filter !== "all") { queryInput.value = filter; doSearch(); }
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// Search
// ─────────────────────────────────────────────────────────────────────────────
searchBtn.addEventListener("click", doSearch);
queryInput.addEventListener("keydown", (e) => { if (e.key === "Enter") doSearch(); });

async function doSearch() {
  const query = queryInput.value.trim();
  const sid   = studentIdInput.value.trim() || "anonymous";

  // Validate student ID before API call
  const idErr = validateStudentIdInput(sid);
  if (idErr && sid !== "anonymous") {
    showToast("Fix your Student ID before searching.", true);
    studentIdInput.focus();
    return;
  }
  state.studentId = sid;

  if (!query) return;

  switchPanel("search");
  setLoading(true);
  hideResults();

  try {
    const res = await fetch("/api/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ student_id: state.studentId, query }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    setLoading(false);

    if (data.search_terms && data.search_terms.length) {
      nluInsights.innerHTML =
        '<span class="nlu-label">Watson NLU extracted:</span>' +
        data.search_terms.map((t) => `<span class="nlu-pill">${esc(t)}</span>`).join("");
      nluInsights.classList.remove("hidden");
    }

    if (data.ai_message) {
      aiMessageText.textContent = data.ai_message;
      aiMessage.classList.remove("hidden");
    }

    if (data.books && data.books.length > 0) {
      resultsTitle.textContent = `${data.total} book${data.total !== 1 ? "s" : ""} found`;
      booksGrid.innerHTML = data.books.map((b, i) => renderPinCard(b, i)).join("");
      resultsSection.classList.remove("hidden");
      attachReserveListeners(booksGrid);
    } else {
      emptyState.classList.remove("hidden");
    }

  } catch {
    setLoading(false);
    showToast("Search failed. Check your connection.", true);
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// All Books panel
// ─────────────────────────────────────────────────────────────────────────────
let _allBooksLoaded = false;
let _allBooksSubjectLoaded = "all";

async function loadAllBooks(subject = state.allBooksSubject, force = false) {
  if (!force && _allBooksLoaded && _allBooksSubjectLoaded === subject) return;

  allBooksLoading.classList.remove("hidden");
  allBooksCount.classList.add("hidden");
  allBooksGrid.innerHTML = "";

  try {
    const url = subject && subject !== "all"
      ? `/api/books?subject=${encodeURIComponent(subject)}&limit=100`
      : `/api/books?limit=100`;
    const res  = await fetch(url);
    const data = await res.json();
    allBooksLoading.classList.add("hidden");

    allBooksCount.textContent = `${data.total} book${data.total !== 1 ? "s" : ""}`;
    allBooksCount.classList.remove("hidden");
    allBooksGrid.innerHTML = (data.books || []).map((b, i) => renderPinCard(b, i)).join("");
    attachReserveListeners(allBooksGrid);

    _allBooksLoaded = true;
    _allBooksSubjectLoaded = subject;
  } catch {
    allBooksLoading.classList.add("hidden");
    showToast("Failed to load books catalogue.", true);
  }
}

// All Books subject filter chips
document.querySelectorAll("#booksFilterStrip .filter-chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    document.querySelectorAll("#booksFilterStrip .filter-chip").forEach((c) => c.classList.remove("filter-chip--active"));
    chip.classList.add("filter-chip--active");
    const subject = chip.dataset.subject || "all";
    state.allBooksSubject = subject;
    loadAllBooks(subject, true);
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// Pin card renderer
// ─────────────────────────────────────────────────────────────────────────────
const RATIOS = ["ratio-square", "ratio-portrait", "ratio-tall", "ratio-xl"];
const BOOK_SVG = `<svg class="pin-thumb__icon" width="48" height="48" viewBox="0 0 48 48" fill="none">
  <rect x="10" y="6" width="28" height="36" rx="2" stroke="#000" stroke-width="2.5"/>
  <path d="M16 14h16M16 20h16M16 26h10" stroke="#000" stroke-width="2" stroke-linecap="round"/>
</svg>`;

function renderPinCard(book, index) {
  const avail       = book.available_copies > 0;
  const ratio       = RATIOS[index % RATIOS.length];
  const thumbClass  = `pin-thumb--${index % 18}`;
  const primaryTag  = (book.subject_tags && book.subject_tags[0]) ? book.subject_tags[0] : null;
  const demandBadge = book.demand_score >= 5
    ? `<div class="pin-card__demand-badge">🔥 ${book.demand_score}</div>` : "";
  const overlayPill = primaryTag
    ? `<div class="pin-card__overlay-pill">${esc(primaryTag)}</div>` : "";
  const tags = (book.subject_tags || []).slice(1, 4)
    .map((t) => `<span class="pin-tag">${esc(t)}</span>`).join("");

  const badgeClass = avail ? "avail-badge--available" : "avail-badge--unavailable";
  const badgeText  = avail ? `✓ ${book.available_copies} available` : "✗ Unavailable";
  const btnClass   = avail ? "" : "btn-pin-action--waitlist";
  const btnText    = avail ? "Reserve" : "Waitlist";

  return `
    <article class="pin-card pin-card--${ratio}" role="listitem"
             data-id="${esc(book._id)}" aria-label="${esc(book.title)}">
      <div class="pin-card__image">
        <div class="pin-card__thumb ${thumbClass}">${BOOK_SVG}</div>
        ${demandBadge}
        ${overlayPill}
      </div>
      <div class="pin-card__meta">
        <div class="pin-card__title">${esc(book.title)}</div>
        <div class="pin-card__author">${esc(book.author)}</div>
      </div>
      ${tags ? `<div class="pin-card__tags">${tags}</div>` : ""}
      <div class="pin-card__footer">
        <span class="avail-badge ${badgeClass}">${badgeText}</span>
        <button class="btn-pin-action ${btnClass}"
                data-id="${esc(book._id)}"
                data-title="${esc(book.title)}"
                data-author="${esc(book.author)}"
                data-avail="${avail}">
          ${btnText}
        </button>
      </div>
    </article>`;
}

function attachReserveListeners(container = document) {
  container.querySelectorAll(".btn-pin-action").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      openReserveModal(
        btn.dataset.id,
        btn.dataset.title,
        btn.dataset.author,
        btn.dataset.avail === "true"
      );
    });
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// Reservation modal
// ─────────────────────────────────────────────────────────────────────────────
let _pendingBookId = null;

function openReserveModal(bookId, title, author, available) {
  // Guard: validate student ID first
  const sid = studentIdInput.value.trim();
  const idErr = validateStudentIdInput(sid);
  if (idErr) {
    showToast(`Invalid Student ID: ${idErr}`, true);
    studentIdInput.focus();
    return;
  }
  _pendingBookId = bookId;
  modalTitle.textContent    = available ? "Reserve this book" : "Join the waitlist";
  modalSubtitle.textContent = `"${title}" by ${author}`;
  modalBody.innerHTML = available
    ? `<p>You are about to reserve a copy for student <strong>${esc(sid)}</strong>.</p>
       <p style="margin-top:8px;color:var(--color-mute);font-size:14px">Held for up to 14 days — IBM Robo will auto-release after that.</p>`
    : `<p>All copies are currently checked out.</p>
       <p style="margin-top:8px;color:var(--color-mute);font-size:14px">Join the waitlist and IBM Robo will promote you automatically when a copy is returned.</p>`;
  modalConfirm.textContent = available ? "Confirm Reservation" : "Join Waitlist";
  reserveModal.classList.remove("hidden");
}

function closeModal() { reserveModal.classList.add("hidden"); }
modalClose.addEventListener("click", closeModal);
modalCancel.addEventListener("click", closeModal);
reserveModal.querySelector(".modal__scrim").addEventListener("click", closeModal);

modalConfirm.addEventListener("click", async () => {
  if (!_pendingBookId) return;
  const bookId = _pendingBookId;
  closeModal();

  try {
    const res = await fetch("/api/reserve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ student_id: state.studentId, book_id: bookId }),
    });
    const data = await res.json();

    // Show specific error (including duplicate-hold message from backend)
    if (data.error) {
      showToast(data.error, true);
      return;
    }

    state.reservations.push({
      id:         data._id,
      bookId,
      bookTitle:  data.book_title,
      bookAuthor: data.book_author,
      status:     data.status,
      message:    data.ai_message || "",
    });

    const msg = data.status === "active" ? "Reservation confirmed!" : "Added to waitlist.";
    showToast(msg);
    _pendingBookId = null;
    updatePinCardState(bookId, data.status);
  } catch {
    showToast("Reservation failed. Try again.", true);
  }
});

function updatePinCardState(bookId, status) {
  // Update cards in both grids
  document.querySelectorAll(`.pin-card[data-id="${bookId}"]`).forEach((card) => {
    const badge = card.querySelector(".avail-badge");
    const btn   = card.querySelector(".btn-pin-action");
    if (badge) {
      badge.className = "avail-badge avail-badge--unavailable";
      badge.textContent = "✗ Unavailable";
    }
    if (btn) {
      btn.className = "btn-pin-action btn-pin-action--waitlist";
      btn.textContent = "Waitlist";
      btn.dataset.avail = "false";
    }
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// Reservations panel
// ─────────────────────────────────────────────────────────────────────────────
function renderReservations() {
  if (!state.reservations.length) {
    reservationsList.innerHTML = `
      <div class="state-card">
        <svg width="48" height="48" viewBox="0 0 48 48" fill="none" aria-hidden="true">
          <rect x="8" y="12" width="32" height="28" rx="3" fill="var(--color-surface-card)" stroke="var(--color-hairline)" stroke-width="1.5"/>
          <path d="M24 20v12M18 26h12" stroke="var(--color-ash)" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        <p class="state-card__title">No holds yet</p>
        <p class="state-card__sub">Search for a book and tap Reserve to add your first hold</p>
      </div>`;
    return;
  }

  reservationsList.innerHTML = state.reservations.map((r) => {
    const chipClass = `status-chip status-chip--${r.status}`;
    return `
      <div class="res-card" data-res-id="${esc(r.id)}">
        <div class="res-card__info">
          <div class="res-card__title">${esc(r.bookTitle || "Unknown Book")}</div>
          <div class="res-card__meta">${esc(r.bookAuthor || "")} · Student: ${esc(state.studentId)}</div>
          ${r.message ? `<div class="res-card__message">${esc(r.message)}</div>` : ""}
        </div>
        <div class="res-card__actions">
          <span class="${chipClass}">${r.status}</span>
          ${r.status !== "cancelled"
            ? `<button class="btn-cancel" data-id="${esc(r.id)}" aria-label="Cancel reservation">Cancel</button>`
            : ""}
        </div>
      </div>`;
  }).join("");

  document.querySelectorAll(".btn-cancel").forEach((btn) => {
    btn.addEventListener("click", () => cancelReservation(btn.dataset.id));
  });
}

async function cancelReservation(resId) {
  try {
    const res  = await fetch(`/api/reserve/${resId}`, { method: "DELETE" });
    const data = await res.json();
    if (data.error) { showToast(data.error, true); return; }
    const r = state.reservations.find((x) => x.id === resId);
    if (r) r.status = "cancelled";
    renderReservations();
    showToast("Reservation cancelled.");
  } catch {
    showToast("Cancel failed.", true);
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Dashboard panel (lazy — only fetches when first opened)
// ─────────────────────────────────────────────────────────────────────────────
let _dashboardLoaded = false;

async function loadDashboard() {
  loadOrchStatus();
  loadExplain();

  if (_dashboardLoaded) return;
  highDemandList.innerHTML   = `<p style="color:var(--color-ash);font-size:13px">Loading…</p>`;
  automationAlerts.innerHTML = `<p style="color:var(--color-ash);font-size:13px">Loading…</p>`;

  try {
    const [demandRes, alertsRes] = await Promise.all([
      fetch("/api/books/high-demand?threshold=3"),
      fetch("/api/automation/alerts"),
    ]);
    const demandData = await demandRes.json();
    const alertsData = await alertsRes.json();

    if (demandData.books && demandData.books.length) {
      highDemandList.innerHTML = demandData.books.map((b) => `
        <div class="demand-item">
          <span class="demand-item__title">${esc(b.title)}</span>
          <span class="demand-score">🔥 ${b.demand_score}</span>
        </div>`).join("");
    } else {
      highDemandList.innerHTML = `<p style="color:var(--color-ash);font-size:13px">No high-demand books yet.</p>`;
    }

    if (alertsData.alerts && alertsData.alerts.length) {
      automationAlerts.innerHTML = alertsData.alerts.map((a) => `
        <div class="alert-item">
          <div class="alert-item__type">${esc(a.type)}</div>
          <div class="alert-item__title">${esc(a.title)}</div>
          <div class="alert-item__meta">Demand: ${a.demand_score} · ${
            new Date(a.raised_at).toLocaleDateString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })
          }</div>
        </div>`).join("");
    } else {
      automationAlerts.innerHTML = `<p style="color:var(--color-ash);font-size:13px">No alerts yet. Run Robo Rules to scan the database.</p>`;
    }

    _dashboardLoaded = true;
  } catch {
    showToast("Dashboard failed to load.", true);
  }
}

runRoboBtn.addEventListener("click", async () => {
  runRoboBtn.disabled = true;
  runRoboBtn.textContent = "Running…";
  try {
    const res  = await fetch("/api/automation/run");
    const data = await res.json();
    showToast(
      `Robo ran — ${data.high_demand_alerts.length} demand alerts, ` +
      `${data.expired_reservations.length} expired, ` +
      `${data.low_stock_reorders.length} reorder alerts.`
    );
    _dashboardLoaded = false;   // Force refresh on next open
    loadDashboard();
  } catch {
    showToast("Automation run failed.", true);
  } finally {
    runRoboBtn.disabled = false;
    runRoboBtn.textContent = "Run Robo Rules";
  }
});

// ─────────────────────────────────────────────────────────────────────────────
// Orchestration status
// ─────────────────────────────────────────────────────────────────────────────
const orchStatus      = $("orchStatus");
const refreshStatusBtn = $("refreshStatusBtn");

async function loadOrchStatus() {
  orchStatus.innerHTML = `<p style="color:var(--color-ash);font-size:13px">Checking services…</p>`;
  try {
    const res  = await fetch("/api/status");
    const data = await res.json();
    orchStatus.innerHTML = Object.entries(data.services).map(([key, s]) => {
      const cls   = s.ok ? "ok" : "fail";
      const badge = s.ok ? "Connected" : "Error";
      const detail = s.ok
        ? `<div class="orch-card__detail">${esc(s.detail || "")}</div>
           <div class="orch-card__latency">${s.latency_ms} ms</div>`
        : `<div class="orch-card__error">${esc((s.error || "").slice(0, 120))}</div>
           ${s.fix ? `<div class="orch-card__fix">Fix: ${esc(s.fix)}</div>` : ""}`;
      return `
        <div class="orch-card orch-card--${cls}">
          <div class="orch-card__service">${esc(key.replace("_", " "))}</div>
          <div class="orch-card__label">${esc(s.label)}</div>
          <div class="orch-card__badge orch-card__badge--${cls}">${badge}</div>
          <div class="orch-card__detail" style="margin-top:2px">${esc(s.description)}</div>
          ${detail}
        </div>`;
    }).join("");
  } catch {
    orchStatus.innerHTML = `<p style="color:var(--color-error);font-size:13px">Could not reach /api/status — is the server running?</p>`;
  }
}

refreshStatusBtn.addEventListener("click", loadOrchStatus);

// ─────────────────────────────────────────────────────────────────────────────
// AI Pipeline explainer
// ─────────────────────────────────────────────────────────────────────────────
const explainPanel     = $("explainPanel");
const toggleExplainBtn = $("toggleExplainBtn");
let _explainLoaded = false;

async function loadExplain() {
  if (_explainLoaded) return;
  try {
    const res  = await fetch("/api/explain");
    const data = await res.json();
    const steps = data.pipeline.map((p, i) => `
      ${i > 0 ? '<div class="pipeline-connector"></div>' : ""}
      <div class="pipeline-step">
        <div class="step-num">${p.step}</div>
        <div class="step-body">
          <div class="step-service">${esc(p.service)}</div>
          <div class="step-role">${esc(p.role)}</div>
          <div class="step-desc">${esc(p.what_it_does)}</div>
          <div class="step-output">${esc(p.output)}</div>
          <div class="step-path">${esc(p.ibm_cloud_path)}</div>
        </div>
      </div>`).join("");
    explainPanel.innerHTML = steps +
      `<div class="explain-summary">${esc(data.architecture_summary)}</div>`;
    _explainLoaded = true;
  } catch {
    explainPanel.innerHTML = `<p style="color:var(--color-error);font-size:13px">Could not load AI explanation.</p>`;
  }
}

toggleExplainBtn.addEventListener("click", () => {
  const hidden = explainPanel.classList.toggle("hidden");
  toggleExplainBtn.textContent = hidden ? "Show" : "Hide";
  if (!hidden && !_explainLoaded) loadExplain();
});

// ─────────────────────────────────────────────────────────────────────────────
// Firebase Auth integration
// Login overlay is controlled by auth.js (ES module), but we also expose
// helpers that auth.js calls via window.
// ─────────────────────────────────────────────────────────────────────────────
const loginNavBtn  = $("loginNavBtn");
const logoutNavBtn = $("logoutNavBtn");
const loginOverlay = $("loginOverlay");

loginNavBtn.addEventListener("click",  () => loginOverlay.classList.remove("hidden"));
logoutNavBtn.addEventListener("click", () => {
  if (window._firebaseSignOut) window._firebaseSignOut();
});

/** Called by auth.js when a user signs in */
window._onAuthSignIn = (user) => {
  loginOverlay.classList.add("hidden");
  loginNavBtn.classList.add("hidden");
  logoutNavBtn.classList.remove("hidden");
  // Pre-fill student ID from email prefix when not already set
  if (studentIdInput.value === "s001") {
    const prefix = (user.email || "").split("@")[0].replace(/[^A-Za-z0-9_\-]/g, "").slice(0, 20);
    if (prefix.length >= 2) studentIdInput.value = prefix;
  }
  state.studentId = studentIdInput.value.trim();
};

/** Exposed for auth.js — lets it read the current student ID input value */
window._getStudentId = () => studentIdInput.value.trim();

/** Called by auth.js when a user signs out */
window._onAuthSignOut = () => {
  loginNavBtn.classList.remove("hidden");
  logoutNavBtn.classList.add("hidden");
};

// ─────────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────────
function hideResults() {
  nluInsights.classList.add("hidden");
  aiMessage.classList.add("hidden");
  resultsSection.classList.add("hidden");
  emptyState.classList.add("hidden");
  loadingState.classList.add("hidden");
}

function setLoading(on) {
  loadingState.classList.toggle("hidden", !on);
}

let _toastTimer = null;
function showToast(msg, error = false) {
  toastEl.textContent = msg;
  toastEl.className   = "toast" + (error ? " toast--error" : "");
  void toastEl.offsetWidth;   // force reflow so transition fires on re-show
  toastEl.classList.add("toast--visible");
  clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => toastEl.classList.remove("toast--visible"), 3600);
}

function esc(str) {
  if (str == null) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}
